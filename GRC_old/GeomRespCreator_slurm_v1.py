#!/stuff

"""
This is a re-write of the GeomRespCreator program in Python3, originally
written in Fortran and now ported over to Python.

Authors:
Evan Christoffersen
Konnor Jones

Version: 1

Version Updates:

Last edited:
"""

# IMPORT NECESSARY MODULES
import itertools
import os
import os.path
import sys
import glob
import shutil
import subprocess
import re



def checkFilepath(filename):
    """
    Checks to see if a filepath exists. Exits on failure.
    """
    if not os.path.isfile(filename):
        print('\nERROR: '+filename+" file is missing!\n")
        sys.exit()
    return



def readNamelistin(filename):
    """
    Reads in the following variables from the namelist.in file:
    Job type
    Number of conformers
    Number of atoms
    Charge
    Multiplicity
    Conformer names
    """
    namelist=[]
    with open(filename, 'r') as f: # opens namelist.in file and reads each line
    # as an element in a list and strips the newline character from each item
        for line in f:
            namelist.append(line.strip('\n'))
    
    confnames = namelist[12:] # puts all conformer names in their own list
    confnames[:] = [x for x in confnames if x] # removes empty list items
    
    namelist=[x.replace(namelist[0], 'jobtype') for x in namelist] # renames
    # the job type element in the list to just "jobtype"
    del namelist[12:] # removes all conformer names from list
    params=dict(zip(namelist[::2], namelist[1::2])) # turns list into
    # dictionary
    
    return params,confnames



# UNFINISHED - FIGURE OUT HOW TO IMPORT GEOMETRY COORDINATES
def writeGeomInp(filename,resname,conf,chrg,mult):
    """
    Creates the conformer_geom.inp file.
    """
    if os.path.isfile(filename): # True if file exists already
        print('\nERROR: Geometry input file '+filename+' already exists!\n')
        sys.exit() # Exit program
    with open(filename, 'a') as f: # Make and append header to file
       f.write(
'''%NProcShared=12
%mem=12GB
%chk=/{0}/{1}_resp.chk
#P HF/6-31g* OPT(Tight) scf(Tight)\n
Gaussian09 geometry optimization at HF/6-31g*\n
{2} {3}'''.format(resname,conf,chrg,mult)
        )
    # with open(filename, 'a') as f: # Make and append to file
    #    f.write(xyzgeometry)
    return



# FORTRAN SCRIPT DOESN'T SEEM TO INCLUDE COORDINATES BUT I THINK IT NEEDS TO?
def writeRespInp(filename,resname,conf,chrg,mult):
    """
    Creates the conformer_resp.inp file.
    """
    if os.path.isfile(filename): # True if file exists already
        print('\nERROR: RESP input file '+filename+' already exists!\n')
        sys.exit() # Exit program
    with open(filename, 'a') as f: # Make and append header to file
       f.write(
'''%NProcShared=12
%mem=12GB
%chk=/{0}/{1}_resp.chk
#P B3LYP/cc-pVTZ SCF=Tight Pop=MK IOp(6/33=2,6/41=10,6/42=17)\n
Gaussian09 single point electrostatic potential calculation at B3LYP/cc-pVTZ\n
{2} {3}\n'''.format(resname,conf,chrg,mult)
        )
    return



def writeGeomPbs(filename,resname):
    """
    Creates the conformer_geom.pbs script.
    """
    if os.path.isfile(filename): # True if file exists already
        print('\nERROR: Geometry script '+filename+' already exists!\n')
        sys.exit() # Exit program
    with open(filename, 'a') as f: # Make and append header to file 
       f.write(
'''#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --export=ALL
#SBATCH --time=0-24:00:00
#SBATCH --error={0}_geom.err\n
hostname\n
test -d /tmp/{0} || mkdir -v /tmp/{0}\n
module load gaussian\n
which 09\n
g09 < {0}_geom.inp > {0}_geom.out\n\n'''.format(resname)
        )
    return



def writeRespPbs(filename,resname):
    """
    Creates the conformer_resp.pbs script.
    """
    if os.path.isfile(filename): # True if file exists already
        print('\nERROR: Geometry script '+filename+' already exists!\n')
        sys.exit() # Exit program
    with open(filename, 'a') as f: # Make and append header to file
       f.write(
'''#!/bin/bash
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --export=ALL
#SBATCH --time=0-24:00:00
#SBATCH --error={0}_resp.err\n
hostname\n
test -d /tmp/{0} || mkdir -v /tmp/{0}\n
module load gaussian\n
which 09\n
g09 < {0}_resp.inp > {0}_resp.out\n\n'''.format(resname)
        )
    return



















# CALL THE ACTUAL PROGRAM HERE

cwd = os.getcwd()

# os.mkdir()
# os.chdir()
# os.listdir()

innamelist='namelist.in'

checkFilepath(innamelist)
namelist = readNamelistin(innamelist)

job = namelist[0]["jobtype"]

###
# JOB TYPE 1
if job == "1":
    resname = namelist[0]["resname"]
    chrg = namelist[0]["charge"]
    mult = namelist[0]["multiplicity"]
    
    # Makes the pbs and inp files in each conformer directory
    for i in [0,len(namelist[1])-1]:
        conformer = namelist[1][i]
        writeGeomPbs(conformer+"_geom.pbs",conformer)
        writeRespPbs(conformer+"_resp.pbs",conformer)
        writeGeomInp(conformer+"_geom.inp",resname,conformer,chrg,mult)
        writeRespInp(conformer+"_resp.inp",resname,conformer,chrg,mult)
        os.mkdir(conformer)
        for f in glob.glob(conformer+'*pbs'): # for any files starting with
        # conformer prefix and ending in "pbs", move to that conformer's folder
            shutil.move(f, conformer)
        for f in glob.glob(conformer+'*inp'): # for any files starting with
        # conformer prefix and ending in "inp", move to that conformer's folder
            shutil.move(f, conformer)
    
    # Submits the pbs files in each directory
    for i in [0,len(namelist[1])-1]:
        conformer = namelist[1][i]
        os.chdir(conformer)
        subprocess.check_call("cd "+conformer+"/ && sbatch -A richmondlab *pbs", shell=True)
        os.chdir(cwd)
    
###
# JOB TYPE 2
elif job == "2":
    print("job2")
    
# Rewrite readit.f and esp.sh into Python code here. There is no reason we
# should have to have a fortran (now Python) script to call an additional
# fortran script and a c-shell (not even Bash!) script. Let's make one program
# instead of 3 that all call to each other.

    newfile = open('test.txt', 'a')
    with open("GLM1_resp.out", 'r') as f: # Must be careful not to try to store
    # this all in memory - must read line by line instead of saving to list/array
        for line in f:
            if re.search("Atomic Center ", line):
                newfile.write(line)
    newfile.close()
    
    newfile = open('test.txt', 'a')
    with open("GLM1_resp.out", 'r') as f:
        for line in f:
            if re.search("ESP Fit", line):
                newfile.write(line)
    with open("GLM1_resp.out", 'r') as f:
        for line in f:
            if re.search("Fit    ", line):
                newfile.write(line)
    newfile.close()
    
    newfile = open('test.txt', 'a')
    with open("GLM1_resp.out", 'r') as f:
        for line in f:
            if re.search("NGrid ", line):
                newfile.write(line)
    newfile.close()

newfile = open('test.txt', 'a')
with open("GLM1_resp.out", 'r') as f:
    for line in f:
        if re.search("Atomic Center ", line):
            a=[]
            a=line.split()
            a=a[5:]
            newfile.write(a)
        if re.search("ESP Fit", line):
            b=[]
            b=line.split()
            b=b[6:]
            newfile.write(b)
        if re.search("Fit    ", line):
            c=[]
            c=line.split()
            c=c[2]
            newfile.write(c)
        if re.search("NGrid ", line):
            d=[]
            d=line.split()
            d=d[2]
            newfile.write(d)
newfile.close()

    

with open("GLM1_resp.out", 'r') as f:
     for line in f:
         if re.search("Atomic Center ", line):
             array=[]
             array=line.split()
             array=array[5:]
             w, h = [float(x) for x in next(f).split()]
             array = []
             for line in f:
                 array.append([float(x) for x in line.split()])

###
# JOB TYPE 3
elif job == "3":
    print("job3")
    
###
# JOB TYPE 4
elif job == "4":
    print("job4")
    
else:
    print("\nERROR: Unacceptable job type chosen.\n")
    print("Please choose job type 1, 2, 3, or 4 and try again.")
    sys.exit()























