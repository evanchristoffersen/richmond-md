#!/stuff

"""
This is a re-write of GeomRespCreator_slurm.f90.
Originally written in Fortran 90 and now ported over to Python3.

Authors (alphabetical):
Evan Christoffersen
Konnor Jones

Python Version:
3.9.2

Update Log:

2021.04.28
Job type 1 almost completely finished. Just need to implement a way to add
geometry coordinates from an xyz file into the _geom.inp file (see
writeGeomInp() function). Preliminary work on job type 2 begun. 

Last edited:
Wednesday 28 April 2021
"""



### IMPORT MODULES ###
import os # allows for making and changing directories
import os.path # allows for checking if file exists
import sys # allows for exiting program when necessary
import glob # allows for selecting files based on wildcard *
import shutil # allows for moving files into different directories
import subprocess # allows for running shell commands from inside .py
import re # allows for regular expressions (grep in python)



### DEFINE FUNCTIONS ###
def checkFilepath(filename):
    """
    Checks to see if a filepath exists. Exits on failure.
    """
    if not os.path.isfile(filename): # true if namelist.in can't be found
        print('\nERROR: '+filename+" file is missing!\n")
        sys.exit() # exit program

def readNamelistin(filename):
    """
    Reads in the parameters and conformer names from namelist.in
    Note: this function only works for a modified version of the namelist.in
    file in which the multiplicity and charge are each given their own lines.
    """
    namelist=[] # list creation
    with open(filename, 'r') as f: # opens namelist.in and appends to list
        for line in f:
            namelist.append(line.strip('\n')) # removes all newline characters
    
    confnames = namelist[12:] # conformer names go in their own list
    confnames[:] = [x for x in confnames if x] # removes empty items from list

    # renames the first element to "jobtype"
    namelist=[x.replace(namelist[0], 'jobtype') for x in namelist]    
    del namelist[12:] # removes conformer names before dictionary creation
    params=dict(zip(namelist[::2], namelist[1::2])) # dictionary creation
    return params,confnames

# UNFINISHED - ADD GEOMETRY COORDINATES
def writeGeomInp(filename,resname,conf,chrg,mult):
    """
    Creates the conformer_geom.inp file.
    """
    if os.path.isfile(filename): # true if file exists already
        print('\nERROR: Geometry input file '+filename+' already exists!\n')
        sys.exit() # exit program
    with open(filename, 'a') as f: # make and append header to file
        f.write("%NProcShared=12")
        f.write("%mem=12GB")
        f.write("%chk=/{0}/{1}_resp.chk".format(resname,conf))
        f.write("#P HF/6-31g* opt(tight,MaxCycles=1000) scf(tight,MaxCycles=1000)\n")
        f.write("Gaussian09 geometry optimization at HF/6-31g*\n")
        f.write("({0} {1}".format(chrg,mult))
    #    f.write(xyzgeometry)
    # don't forget to include two empty lines at the end

# FORTRAN SCRIPT DOESN'T SEEM TO INCLUDE COORDINATES BUT I THINK IT NEEDS TO?
def writeRespInp(filename,resname,conf,chrg,mult):
    """
    Creates the conformer_resp.inp file.
    """
    if os.path.isfile(filename): # true if file exists already
        print('\nERROR: RESP input file '+filename+' already exists!\n')
        sys.exit() # exit program
    with open(filename, 'a') as f: # make and append header to file
        f.write("%NProcShared=12")
        f.write("%mem=12GB")
        f.write("%chk=/{0}/{1}_resp.chk".format(resname,conf))
        f.write("#P B3LYP/cc-pVTZ scf(tight,MaxCycles=1000) Pop=MK IOp(6/33=2,6/41=10,6/42=17)\n")
        f.write("Gaussian09 single point electrostatic potential calculation at B3LYP/cc-pVTZ\n")
        f.write("({0} {1}".format(chrg,mult))

def writePbs(filename,resname,ftype):
    """
    Creates the .pbs script for _geom.inp or _resp.inp files.
    The _geom.pbs and _resp.pbs files are nearly identical, so only one
    function is needed, unlike for the _geom.inp vs. _resp.inp files.
    """
    if os.path.isfile(filename): # true if file exists already
        print('\nERROR: '+filename+' already exists!\n')
        sys.exit() # exit program
    with open(filename, 'a') as f: # make and append header to file 
        f.write("#!/bin/bash")
        f.write("#SBATCH --partition=short")
        f.write("#SBATCH --nodes=1")
        f.write("#SBATCH --ntasks-per-node=12")
        f.write("#SBATCH --export=ALL")
        f.write("#SBATCH --time=0-24:00:00")
        f.write("#SBATCH --error={0}_{1}.err\n".format(resname,ftype))
        f.write("module load gaussian\n")
        f.write("g09 < {0}_{1}.inp > {0}_{1}.out\n\n".format(resname,ftype))



### EXECUTE THE PROGRAM HERE ###

cwd = os.getcwd() # save current directory
innamelist='namelist.in' # fortran carryover
checkFilepath(innamelist) # confirm namelist.in exists

# read namelist.in parameters and conformer names into the "namelist" variable
namelist = readNamelistin(innamelist)
job = namelist[0]["jobtype"] # save job type as "job"



### JOB TYPE 1 ###
if job == "1":
    resname = namelist[0]["resname"] # save residue prefix as "resname"
    chrg = namelist[0]["charge"] # save charge as "chrg"
    mult = namelist[0]["multiplicity"] # save multiplicity as "mult"
    nconf = namelist[0]["nconf"] # save number of conformers as "nconf"
    
    for i in [0,nconf-1]:
        conformer = namelist[1][i] # conformer iterator
        writeGeomPbs(conformer+"_geom.pbs",conformer)
        writeRespPbs(conformer+"_resp.pbs",conformer)
        writeGeomInp(conformer+"_geom.inp",resname,conformer,chrg,mult)
        writeRespInp(conformer+"_resp.inp",resname,conformer,chrg,mult)
        os.mkdir(conformer) # make a directory for the conformer
        # move any files for the conformer ending in pbs into its directory
        for f in glob.glob(conformer+'*pbs'):
            shutil.move(f, conformer)
        # move any files for the conformer ending in pbs into its directory
        for f in glob.glob(conformer+'*inp'):
            shutil.move(f, conformer)
    
    # Submits the pbs files in each directory
    for i in [0,nconf-1]:
        conformer = namelist[1][i] # conformer iterator
        os.chdir(conformer) # enter conformer directory
        # submit all files ending in pbs to Talapas
        subprocess.check_call("sbatch -A richmondlab *pbs", shell=True)
        os.chdir(cwd) # return to working directory


    
### JOB TYPE 2 ###
elif job == "2":

# NOTE: MUST BE CAREFUL NOT TO STORE ENTIRE .out FILE RESULTS INTO A LIST OR
# ARRAY. THE .out FILES, ESPECIALLY FOR LARGER MOLECULES, BECOME MASSIVE, AND
# TRYING TO STORE IT ALL IN RAM IS JUST POOR CODING PRACTICE. DO NOT USE
# readlines() ! PROCESS FILES LINE BY LINE AS SHOWN.

    newfile = open('test.txt', 'a')
    with open("GLM1_resp.out", 'r') as f:
        for line in f:
            if re.search("Atomic Center ", line):
                newfile.write(line)
    with open("GLM1_resp.out", 'r') as f:
        for line in f:
            if re.search("ESP Fit", line):
                newfile.write(line)
    with open("GLM1_resp.out", 'r') as f:
        for line in f:
            if re.search("Fit    ", line):
                newfile.write(line)
    with open("GLM1_resp.out", 'r') as f:
        for line in f:
            if re.search("NGrid ", line):
                newfile.write(line)
    newfile.close()

# newfile = open('test.txt', 'a')
# with open("GLM1_resp.out", 'r') as f:
#     for line in f:
#         if re.search("Atomic Center ", line):
#             a=[]
#             a=line.split()
#             a=a[5:]
#             newfile.write(a)
#         if re.search("ESP Fit", line):
#             b=[]
#             b=line.split()
#             b=b[6:]
#             newfile.write(b)
#         if re.search("Fit    ", line):
#             c=[]
#             c=line.split()
#             c=c[2]
#             newfile.write(c)
#         if re.search("NGrid ", line):
#             d=[]
#             d=line.split()
#             d=d[2]
#             newfile.write(d)
# newfile.close()



### JOB TYPE 3 ###
elif job == "3":

# Use subprocess.check_call("bash cmd", shell=True)

# Note: subprocess.check_call() and subprocess.run() should ALWAYS be preferred
# over subprocess.call(), subprocess.Popen(), os.system(), and os.popen().



### JOB TYPE 4 ###
elif job == "4":

# Use subprocess.check_call("bash cmd", shell=True)

# Note: subprocess.check_call() and subprocess.run() should ALWAYS be preferred
# over subprocess.call(), subprocess.Popen(), os.system(), and os.popen().



else:
    print("\nERROR: Unacceptable job type chosen.\n")
    print("Please choose job type 1, 2, 3, or 4 and try again.")
    sys.exit()

