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
- Added the FormatCoordMat() function to properly format the matrix of atomic
  coordinates that are copied from the .xyz file into the .inp files. 
  Code was added to WriteGeomInp() and WriteRespInp() functions to incoprorate 
  the FormatCoordMat() function.
        -Konnor, May 2, 2021
- Completed: Job Type 1 section is finished. Added a line to WriteGeomInp() and
  WriteRespInp() functions so the .xyz file of each conformer is opened.
 Modified the first for loop in the Job TYPE 1 section so it iterates as many
 times as there are conformers.
 Previously, the loop iterated twice.
 Work in progress: Setting the format of the .dat file
        -Konnor, May 3, 2021
- Modified FormatCoordMat() function to make it more easy to read and created
  spacing() function to handle only the spacing between columns in the
  tables that contain the atomic coordinates.
  Made some comments in the job == "2" section as to how this code should be
  written.
        -Konnor, May 3, 2021
- Added if else statements to spacing() and FormatCoordMat() functions so these
  functions can be ran when job = 1 or 2. This makes the body of the
  code easier to read. The spacing() function correctly sets the spacing
  between columns. In both functions, the code for job = 2 needs to be cleaned
  up.
  Added and commented out a for loop in the job == "2" section. This loop can
  replace all of the with open() statements.
          -Konnor, May 4, 2021
- Added fortranFormat() function so numbers written to the _esp.dat file are in
  the same format as when Nick's fortran code is executed
  Added code to the beginning of the job == 2 section so the number at the
  top-left corner of the file is written.
  Added code to the job == 2 section so the first part of the _esp.dat file is
  formatted correctly
          -Konnor, May 8, 2021
- Added code to the job = 2 section that properly formats the file that is
  created in this section. The file is formatted correctly, but the values
  in the file may not be correct; these need to be checked. Also need to look
  into what d0 means in fortran. In readit.f, unit = 0.529177249d0. I am
  not sure d0 needs to be incorporated into the script.
        -Konnor, May 13, 2021
- Started to fill in the job type = 2 section so it will actually peform the
  tasks that will be executed.
          -Konnor, May 21, 2021
- Continued to work on filling in the job type = 2 section so it will actually
  peform the tasks that will be executed. Line 322 should be the last thing
  that needs to be finished in the for loop. Something can probably be added to
  def read_namelist(filename) to extract and set the three letters that
  name/describe
  the conformer (e.g. GLD) to a variable that can be used on this line. This is
  probably a very quick thing to do, but I ran out of time.
            -Konnor, May 22, 2021    

Next Steps:
Complete job type 2 section. Once completed, run Nick's and the python scripts
on at least two molecules. Compare the files to assure to assure
his scripts have been correctly translated into python. I believe this should
be done before moving on to Job type 3 and 4. I think this should be
done for two molecules because it will better help find bugs/errors than if
this was done for only one molecule. It is important to find the bugs/
errors before we start working with larger molecules, for which our Ph.D.s are
on the line.

Additional notes:
I noticed that esp.sh creates a.out, but this script doesn't create it. Nick's
guide states this file is important. Something that needs to be considered.


"""

import os # Change directories
import os.path # Prevent file overwrite

import sys # Error management

import glob # File selection wildcard *

import shutil # Move files between directories

import subprocess # Run shell commands

import re # Regular expressions (i.e. grep) 

# from pathlib import Path

try:
    import fortranformat as ff
except:
    raise ModuleNotFoundError('The "fortranformat" module must be installed.')



def read_namelist(f="namelist.in"):
    """Reads in the parameters and conformer names from "namelist.in"

    Designed to work on a modified version of namelist.in in which the
    multiplicity and charge are given on separate lines. Also note, this
    function does NOT check that "namelist.in" is properly formatted, so double
    check formatting before use.

    PARAMETERS
    ----------
    f : string
        The path/filename containing the data to be imported. Defaults to
        "namelist.in" if no argument is given.

    RETURNS
    -------
    params : dictionary
        Contains the job parameters.
    confnames : list
        Contains the conformer names.
    """
    # Checks that "namelist.in" exists
    if os.path.isfile(f) is not True:
        raise Exception(f, ' is missing or does not exist.\n')
    # Opens namelist.in and appends each line to a list while stripping newline
    # "\n" characters
    namelist=[]
    with open(f, 'r') as file:
        for line in file:
            namelist.append(line.strip('\n'))
    # Makes a separate list for just the conformer names and removes all empty
    # items from the list of conformer names
    confnames = namelist[12:]
    confnames[:] = [x for x in confnames if x]
    # Renames the first element to "jobtype" and creates a dictionary for the
    # different parameters
    namelist=[x.replace(namelist[0], 'jobtype') for x in namelist]
    del namelist[12:]
    params=dict(zip(namelist[::2], namelist[1::2]))
    return params,confnames




def write_geom_input(f,resname,conf,chrg,mult):
    """
    Creates the "conformer_geom.inp" file.
    """
    if os.path.isfile(f) is True:
        raise Exception(f, 'already exists!\n')
    # Saves file name of the molecular coordinate file. Note: coordinates MUST
    # be given in the ".xyz" format
    coords = os.path.join(cwd,conformer + '.xyz')
    with open(f, 'a') as outfile, open(coords, 'r') as xyz:
        outfile.write("%NProcShared=12\n")
        outfile.write("%mem=12GB\n")
        outfile.write("%chk=/{0}/{1}_resp.chk\n".format(resname,conf))
        outfile.write("#P HF/6-31g* opt(tight,MaxCycles=1000)
        scf(tight,MaxCycles=1000)\n\n")
        outfile.write("Gaussian09 geometry optimization at HF/6-31g*\n\n")
        outfile.write("{0} {1}\n".format(chrg,mult))


        # Copies the matrix of
        # atomic coordinates from the .xyz to the .inp file
        coord_matrix = FormatCoordMat(xyzfile)
        for i in range(len(coord_matrix)):
            f.write(coord_matrix[i])




# FORTRAN SCRIPT DOESN'T SEEM TO INCLUDE COORDINATES BUT I THINK IT NEEDS TO?
def writeRespInp(filename,resname,conf,chrg,mult):
    """
    Creates the conformer_resp.inp file.
    """
    if os.path.isfile(f) is True:
        raise Exception(f, 'already exists!\n')
    # Saves file name of the molecular coordinate file. Note: coordinates MUST
    # be given in the ".xyz" format
    coords = os.path.join(cwd,conformer + '.xyz')
    with open(f, 'a') as outfile, open(coords, 'r') as xyz:
        outfile.write("%NProcShared=12\n")
        outfile.write("%mem=12GB\n")
        outfile.write("%chk=/{0}/{1}_resp.chk\n".format(resname,conf))
        outfile.write("#P B3LYP/c-pVTZ scf(tight,MaxCycles=1000) Pop=MK \
        IOp(6/33=2,6/41=10,6/42=17)\n\n")
        outfile.write("Gaussian09 single point electrostatic potential \
        calculation at B3LYP/c-pVTZ\n\n")
        outfile.write("{0} {1}\n".format(chrg,mult))

    with open(xyz, 'r') as coordinatefile:
        for line in coordinatefile:
            lines = line.split()
            

        coord_matrix = FormatCoordMat(xyzfile)
        for i in range(len(coord_matrix)):
            f.write(coord_matrix[i])


# python format:

n = 123.456

print(format(n,'<10d'))
# gives: 123.456   
print(format(n,'10.2f'))
# gives:     123.46
print(format(n,'16.2E'))
# gives:         1.23E+02

with open('GLM1.xyz', 'r') as coordinatefile:
    foo = []
    for line in coordinatefile:
        for number in line.split():
            
        lines = line.split()
        foo.append(lines)

for i in range(len(foo)):
    try:
        type(foo[i][0]) == str
    except:
        bar.append(i)


def FormatCoordMat(xyzfile):
    """ Formats the atomic coordinates matrix/table that is written to the .inp
    files """
    if job == "1":
        coord_matrix = []
        for line in xyzfile:              # reads each line of the .xyz file
            cord = line.split()           # Splits each line into a list
            if len(cord) == 4:            # Determines if the current line
            # contains the identity of the atom (e.g. H) and its coordiantes
                spaces = spacing(cord)    # Sets the spacing between the
                # columns in the file
                coordinates = cord[0] + spaces[0] + cord[1] + spaces[1] +
                cord[2] + spaces[2] +  cord[3] + '\n'      # one row that will
                # be written to the file
                coord_matrix.append(coordinates)    # appends the row to a
                # list. The list contains all of the rows that will be written to
                # the file

        coord_matrix.append('\n')         # Adds two empty lines to
        # coord_matrix
        return coord_matrix
    elif job == "2":
        data = []
        for line in xyzfile:
            if type(line) == str:             # reads each line of the .xyz
            # file
                Data = line.split()           # Splits each line into a list
            if len(cord) == 4:            # Determines if the current line
            # contains the identity of the atom (e.g. H) and its coordiantes
                spaces = spacing(cord)    # Sets the spacing between the
                # columns in the file
                coordinates = cord[0] + spaces[0] + cord[1] + spaces[1] +
                cord[2] + spaces[2] +  cord[3] + '\n'      # one row that will
                # be written to the file
                coord_matrix.append(coordinates)    # appends the row to a
                # list. The list contains all of the rows that will be written to
                # the file
    else:
        pass

def spacing(cord):
    """ Sets the spacing between columns in a matrix of atomic coordiantes """
    if job == "1":
        print('job 1 is ')
        space_1, space_2, space_3 = '    ', ' ', ' '    # Sets the initial
        spacing between the columns in the matrix of atomic coordinates
        for i in range(4):
            if i == 0:                                  # Does not adjust
            spacing if the current element is a letter
                continue
            else:
                space = ''
                # if |number| < 10, add one space
                if abs(float(cord[i])) < 10:
                    space = space + ' '
                # If the number is >= 0 (positive), add one space
                if float(cord[i]) > 0:
                    space = space + ' '
                # if the number is -0.000000, do not add any spaces
                if i == '-0.000000':
                    space = ''
                if float(cord[i]) == float(cord[1]):
                    space1 = space_1 + space
                elif float(cord[i]) == float(cord[2]):
                    space2 = space_2 + space
                elif float(cord[i]) == float(cord[3]):
                    space3 = space_3 + space
                else:
                    pass
        spaces = [space1, space2, space3]
        return spaces

    else:
        pass

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
        f.write("#!/bin/bash\n")
        f.write("#SBATCH --partition=short\n")
        f.write("#SBATCH --nodes=1\n")
        f.write("#SBATCH --ntasks-per-node=12\n")
        f.write("#SBATCH --export=ALL\n")
        f.write("#SBATCH --time=0-24:00:00\n")
        f.write("#SBATCH --error={0}_{1}.err\n\n".format(resname,ftype))
        f.write("module load gaussian\n\n")
        f.write("g09 < {0}_{1}.inp > {0}_{1}.out\n\n".format(resname,ftype))

def fortranFormat(number):
    """ Formats a string of digits to look like the scientific notation in
    fortran. """
    if number.startswith('-'):   # Correctly formats the number if it is
    negative
        number = number[1:]
        a = '{:.5E}'.format(float(number))           #
        e = a.find('E')
        num = '-'
        +'0.{}{}{}{:02d}'.format(a[0],a[2:e],a[e:e+2],abs(int(a[e+1:])*1+1))
    else:                   # Correctly formats the number if it is psoitive
        a = '{:.5E}'.format(float(number))
        e = a.find('E')
        num =
        '0.{}{}{}{:02d}'.format(a[0],a[2:e],a[e:e+2],abs(int(a[e+1:])*1+1))
    if num == '-0.000000E+01':
        num = '-0.000000E+00'
    return num


cwd = os.getcwd() # save current directory
print(cwd)
innamelist='namelist.in' # fortran carryover
check_filepath(innamelist) # confirm namelist.in exists

# read namelist.in parameters and conformer names into the "namelist" variable
namelist = read_namelist(innamelist)
job = namelist[0]["jobtype"] # save job type as "job"



### JOB TYPE 1 ###
if job == "1":
    resname = namelist[0]["resname"] # save residue prefix as "resname"
    chrg = namelist[0]["charge"] # save charge as "chrg"
    mult = namelist[0]["multiplicity"] # save multiplicity as "mult"
    nconf = int(namelist[0]["nconf"]) # save number of conformers as "nconf"

    for i in range(nconf):
        conformer = namelist[1][i] # conformer iterator
        writePbs(conformer+"_geom.pbs",conformer,"geom")
        writePbs(conformer+"_resp.pbs",conformer,"resp")
        write_geom_input(conformer+"_geom.inp",resname,conformer,chrg,mult)
        writeRespInp(conformer+"_resp.inp",resname,conformer,chrg,mult)
        os.mkdir(conformer) # make a directory for the conformer
        # move any files for the conformer ending in pbs into its directory
        for f in glob.glob(conformer+'*pbs'):
            shutil.move(f, conformer)
        # move any files for the conformer ending in pbs into its directory
        for f in glob.glob(conformer+'*inp'):
            shutil.move(f, conformer)
#
#     # Submits the pbs files in each directory
#     for i in [0,nconf-1]:
#         conformer = namelist[1][i] # conformer iterator
#         os.chdir(conformer) # enter conformer directory
#         # submit all files ending in pbs to Talapas
#         subprocess.check_call("sbatch -A richmondlab *pbs", shell=True)
#         os.chdir(cwd) # return to working directory



### JOB TYPE 2 ###
elif job == "2":

    """Job type = 2 steps"""
# DONE--Create RESP directory
# DONE-- Move files to the RESP directory
# DONE-- Change the current directory to RESP .
# Create esp.dat files for each conformer (e.g. ABC1_esp.dat).
# DONE-- Concatenate all esp.dat files into espot. (cat ABC1_esp.dat
# ABC2_esp.dat ABC3_esp.dat (etc.) >espot)
# For the first resp fit, edit resp.in so iqopt = 1 and for each conformer,
# list hte atoms and the restrictions for the charge and create the matrix at
# the bottom of the file
# Run the resp fit
# Get the charges for the first molecular unit from qout and copy them into
# qnext
# Make a copy of qout and name the file qin
# Rename punch, qout, and espot to punch#, qout#, and espot# so everything is
# backed up
# Run job type = 3 to get updated .mol2 file (I don't know if we sholud do
# this. It may require a lot of time for
#  this to run. Maybe it is only needed for one conformer. Need to understand
#  this step before coding it)
# Copy the parm99.dat fil into the RESP folder
# Check the parameters with one of the mol2 files
# Find suitable replacment parameters in parm99.dat or gaff.dat (This will
# require some thinking)
# Edit the [ABC].frcmod file with the new parameters
# Edit the leap.in files so it knows to get the modified parameter file
    """ Iterating through the RESP fitting routine until convergence achieved
    """
# I belive there are "three" iterations/instances the charges have converged.
# The three instances are 1) resp.in 2) resp.in1 3) resp.in2
# In resp.in, set iqopt = 2, ihfree = 1, qwt = 0.000000
# This is where Nick's instructions get confusing. I think qin should be
# created from qout, then loop through steps 8-11, but I am not sure right now
# In the punch file, check that charges have converged
# Create resp.in1
# Part of making resp.in1--deal with polar atoms and H’s on polar atoms, by
# editing the restrictions in the list of atoms (setting equivalent atoms
# equal)
# The remaing steps are not listed yet

# Create a directory named RESP
    dir_resp = os.mkdir('RESP')

# Move files to the RESP directory
# Note-- This moves GeomRespCreator2.py to the RESP directory. Have to think
# about if this is necessary
    """
    respfit_files =['namelist.in', 'GeomRespCreator2.py', 'leap.in',
    'leaprc.ff02pol.r1', 'sander.in', 'resp.in', 'resp.in1', 'resp.in2']

    for files in os.listdir(os.getcwd()):
        if files in respfit_files:
            shutil.move(i, dir_resp)
        elif filename.endswith("_resp.out"):
            shutil.move(i, dir_resp)
        elif filename.endswith(".mol2"):
            shutil.move(i, dir_resp)
        else:
            continue
    """

# change current directory to RESP directory.
    """ dir = os.chdir('RESP') """

# ______________________________________________________

# Create esp.dat files for each conformer (e.g. ABC1_esp.dat).
    for i in range(nconf):  # Need this for loop to iterate the conformers in
    order (ABC1, ABC2, ABC3, etc.)


        """ *** Evan- The fortran code have unit = 0.529177249d0, which means
        unit is a double precision number. I think the float data type is
        comparable to this, so no rounding errors will not be introduced, but I
        am not sure """
        unit = 0.529177249

        confnum = "GLM" + str(i + 1)   # GLM1 need to be replaced with the
        conformer name

        # writes the number of atoms in the molecule and another number (the
        # number of data points in the RESP fit - the nmber of atoms in the
        # molecule) to the top left corner of the [ABC]_esp.dat file
        with open(confnum + "_resp.out", 'r') as f, open(confnum + '_esp.dat',
        'a') as esp:
            topcorner = []
            for line in f:
            # Search file for lines that contain the string "NGrid " and
            extract necessary values
                if re.search("NGrid ", line):
                    topcorner.append(line.split()[2])
            i = topcorner[0]
            j = int(topcorner[1]) - int(topcorner[0])
            esp.write(f"    {i}{j}\n")

        # creates the 3 columns at the top of the [ABC]_esp.dat file
        with open(confnum + "_resp.out", 'r') as f, open(confnum + '_esp.dat',
        'a') as esp:
            for line in f:
                if re.search("Atomic Center ", line):
                # Search file for lines that contain the string "Atomic Center
                "
                    atom_center = line.split()
                    atom_cent = atom_center[5:]
                    # Isolates the x, y, and z coordinates in the current line
                    atom_cent[0] = fortranFormat(str(float(atom_cent[0])/unit))
                    # Correctly fomrats atomic coordinates
                    atom_cent[1] = fortranFormat(str(float(atom_cent[1])/unit))
                    atom_cent[2] = fortranFormat(str(float(atom_cent[2])/unit))
                    coordinates = '{:>32}  {:>14}  {:>14}'.format(atom_cent[0],
                    atom_cent[1], atom_cent[2]) + '\n'   # Correctly format the
                    spacing in each row of numbers
                    esp.write(coordinates)

        # Extracts RESP fit data from the [ABC]_resp.out file
        with open(confnum + "_resp.out", 'r') as f, open("b", 'w') as b,
        open("c", 'w') as c:
            for line in f:
                if re.search("ESP Fit", line):
                # Search file for lines that contain the string  "ESP Fit" and
                write to b file
                    b.write(line)
                if re.search("Fit    ", line):
                # Search file for lines that contain the string "Fit    " and
                write to c file
                    c.write(line)

        # Creates the four columns in the bottom section of hte [ABC]_esp.dat
        # file
        with open("b", 'r') as b, open("c", 'r') as c, open(confnum +
        '_esp.dat', 'a') as esp:
            for line_a, line_b in zip(b, c):
                val1 = line_a.split()
                val2 = line_b.split()
                val1[6] = fortranFormat(val1[6])
                val1[7] = fortranFormat(str(float(val1[7])/unit))
                # Correctly fomrats formats data
                val1[8] = fortranFormat(str(float(val1[8])/unit))
                val2[2] = fortranFormat(str(float(val2[2])/unit))
                line_new = '{:>16}  {:>14}  {:>14}  {:>14}'.format(val1[6],
                val1[7], val1[8], val2[2]) + '\n'   # Correctly format the
                spacing in each row of numbers
                esp.write(line_new)

        os.remove('b') # Remove file b
        os.remove('c') # Remove file c

        quit()
    # ______________________________________________________

        list = []
        cwd = os.getcwd()

        # Create a list of [ABC]_esp.dat files that is sorted based on the
        # number in the file name.
        for files in os.listdir(cwd):
            if filename.endswith("_esp.dat"):
                list.append(filename)
            list = sorted(list, key=lambda x: int("".join([i for i in x if
            i.isdigit()])))

        # Concatenate all esp.dat files into the espot file.
        with open('espot', 'w') as espot:
            for i in list:
                with open(os.path.join(cwd,i)) as infile:
                    for line in infile:
                        espot.write(line)











""" JOB TYPE 3 """
# elif job == "3": # python gets mad if there isn't something in this loop
#     print("job3")
#
# # Use subprocess.check_call("bash cmd", shell=True)
#
# # Note: subprocess.check_call() and subprocess.run() should ALWAYS be
# preferred
# # over subprocess.call(), subprocess.Popen(), os.system(), and os.popen().
#
#
#
# ### JOB TYPE 4 ###
# elif job == "4": # python gets mad if there isn't something in this loop
#     print("job4")
#
# # Use subprocess.check_call("bash cmd", shell=True)
#
# # Note: subprocess.check_call() and subprocess.run() should ALWAYS be
# preferred
# # over subprocess.call(), subprocess.Popen(), os.system(), and os.popen().
#
#
#
# else:
#     print("\nERROR: Unaceptable job type chosen.\n")
#     print("Please choose job type 1, 2, 3, or 4 and try again.")
#     sys.exit()
