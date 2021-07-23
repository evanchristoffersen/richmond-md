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
- Added hb_fortran_format() function so numbers written to the _esp.dat file are in
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



""" IMPORT MODULES """



""" STANDARD PYTHON MODULES """ 
import glob # File selection wildcard *
import os # Change directories and prevent file overwrite
import re # Regular expressions (i.e. grep) 
import shutil # Move files between directories
import subprocess as sp # Run shell commands
import sys # Error management

""" NON-STANDARD PYTHON MODULES """
# Try to import non-standard module and exit gracefully if not installed.
# Module can be installed (even on Talapas!) using the following:
# pip install fortranformat
# TO INSTALL PIP (may have to use sudo):
# curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
# python get-pip.py
try:
    import fortranformat as ff # Format values properly
except:
    raise ModuleNotFoundError('The "fortranformat" module must be installed.')



""" DEFINE FUNCTIONS """



def check_filepath(f):
    """
    Raises FileNotFoundError if a file doesn't exist. Returns None.

    PARAMETERS
    ----------
    f : string
        The path/filename containing the data to be imported.

    """
    if os.path.isfile(f) is not True:
        raise FileNotFoundError('File {} is missing!\n'.format(f))
    return None



def read_namelist(f="namelist.in"):
    """
    Reads in the parameters and conformer names from "namelist.in" 
    Designed to work on a modified version of namelist.in in which the
    multiplicity and charge are given on separate lines. Also note, this
    function does NOT check that "namelist.in" is properly formatted, so 
    double check formatting before use.

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
        raise FileNotFoundError('File {} is missing!\n'.format(f))

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
    Creates the "conformer_geom.inp" file, using the information loaded from
    the "namelist.in" file. Loads molecular coordinates from the .xyz file
    format (REQUIRED). Returns None.

    PARAMETERS
    ----------
    f : string
        The full name for the "conformer_resp.inp" file
    resname : string
        Three letter conformer designation (taken from "namelist.in")
    conf : string
        Three letter conformer designation + integer (taken from "namelist.in")
    chrg : string
        Charge (taken from "namelist.in")
    mult : string
        Multiplicity (taken from "namelist.in")

    """
    # Check if file exists (prevents overwrite)
    if os.path.isfile(f) is True:
        raise Exception('File {} already exists!\n'.format(f))

    # Writes a new file (the "conformer_geom.inp" file) and appends to it all
    # of the header information needed for the calculation
    coords = os.path.join(cwd,conformer + '.xyz')
    with open(f, 'a') as outfile, open(coords, 'r') as xyz:
        outfile.write("%NProcShared=12\n")
        outfile.write("%mem=12GB\n")
        outfile.write("%chk=/{0}/{1}_resp.chk\n".format(resname,conf))
        outfile.write("#P HF/6-31g* opt(tight,MaxCycles=1000)
        scf(tight,MaxCycles=1000)\n\n")
        outfile.write("Gaussian09 geometry optimization at HF/6-31g*\n\n")
        outfile.write("{0} {1}\n".format(chrg,mult))

    # Loads the molecular geometry into a list called "coords"
    coords = []
    xyz = os.path.join(cwd,conformer + '.xyz')
    with open(xyz, 'r') as coordinatefile:
        for line in coordinatefile:
            lines = line.split()
            coords.append(lines)

    # Removes the first two header lines of the molecular geometry file (xyz
    # format ONLY) and removes any additional lines containing more or less
    # than just four items, the atom, and its x, y, and z coordinates
    del coords[0]
    del coords[0]
    for i in range(0,len(coords)):
        if coords[i] != 4:
            del coords[i]
            
    # Reopens the "conformer_resp.inp" file and appends the formatted molecular
    # geometry coordinates to the file
    with open(f, 'a') as outfile:
        for i in range(0,len(coords)):
            a = format(int(coords[i][0]),'<10d')
            x = format(float(coords[i][1]),'12.6f')
            y = format(float(coords[i][2]),'12.6f')
            z = format(float(coords[i][3]),'12.6f')
            outfile.write('{}{}{}{}'.format(a, x, y, z))
    return None



def write_resp_input(filename,resname,conf,chrg,mult):
    """
    Creates the "conformer_resp.inp" file, using the information loaded from
    the "namelist.in" file. Loads molecular coordinates from the .xyz file
    format (REQUIRED). Returns None.

    PARAMETERS
    ----------
    f : string
        The full name for the "conformer_resp.inp" file
    resname : string
        Three letter conformer designation (taken from "namelist.in")
    conf : string
        Three letter conformer designation + integer (taken from "namelist.in")
    chrg : string
        Charge (taken from "namelist.in")
    mult : string
        Multiplicity (taken from "namelist.in")

    """
    # Check if file exists (prevents overwrite)
    if os.path.isfile(f) is True:
        raise Exception('File {} already exists!\n'.format(f))

    # Writes a new file (the "conformer_resp.inp" file) and appends to it all
    # of the header information needed for the calculation
    with open(f, 'a') as outfile:
        outfile.write("%NProcShared=12\n")
        outfile.write("%mem=12GB\n")
        outfile.write("%chk=/{0}/{1}_resp.chk\n".format(resname,conf))
        outfile.write("#P B3LYP/c-pVTZ scf(tight,MaxCycles=1000) Pop=MK \
        IOp(6/33=2,6/41=10,6/42=17)\n\n")
        outfile.write("Gaussian09 single point electrostatic potential \
        calculation at B3LYP/c-pVTZ\n\n")
        outfile.write("{0} {1}\n".format(chrg,mult))

    # Loads the molecular geometry into a list called "coords"
    coords = []
    xyz = os.path.join(cwd,conformer + '.xyz')
    with open(xyz, 'r') as coordinatefile:
        for line in coordinatefile:
            lines = line.split()
            coords.append(lines)

    # Removes the first two header lines of the molecular geometry file (xyz
    # format ONLY) and removes any additional lines containing more or less
    # than just four items, the atom, and its x, y, and z coordinates
    del coords[0]
    del coords[0]
    for i in range(0,len(coords)):
        if coords[i] != 4:
            del coords[i]
            
    # Reopens the "conformer_resp.inp" file and appends the formatted molecular
    # geometry coordinates to the file
    with open(f, 'a') as outfile:
        for i in range(0,len(coords)):
            a = format(int(coords[i][0]),'<10d')
            x = format(float(coords[i][1]),'12.6f')
            y = format(float(coords[i][2]),'12.6f')
            z = format(float(coords[i][3]),'12.6f')
            outfile.write('{}{}{}{}'.format(a, x, y, z))
    return None



def write_submission_script(f,resname,ftype):
    """
    Creates the .pbs submission script for "_geom.inp" or "_resp.inp" files.
    Returns None.

    PARAMETERS
    ----------
    f : string
        Filename
    resname : string
        Three letter prefix for this molecule
    ftype : string
        "geom" or "resp" designator for whether this generates a .pbs file for
        a corresponding "_geom.inp" or "_resp.inp" file.

    """
    # Check if file exists (prevents overwrite)
    if os.path.isfile(f) is True:
        raise Exception('File {} already exists!\n'.format(f))
    # Append header to .pbs submission file
    with open(filename, 'a') as f:
        f.write("#!/bin/bash\n")
        f.write("#SBATCH --partition=short\n")
        f.write("#SBATCH --nodes=1\n")
        f.write("#SBATCH --ntasks-per-node=12\n")
        f.write("#SBATCH --export=ALL\n")
        f.write("#SBATCH --time=0-24:00:00\n")
        f.write("#SBATCH --error={0}_{1}.err\n\n".format(resname,ftype))
        f.write("module load gaussian\n\n")
        f.write("g09 < {0}_{1}.inp > {0}_{1}.out\n\n".format(resname,ftype))
    return None



def write_esp_dat(conf):
    """
    This function uses the contents of the "conformer_resp.out" file to write
    the corresponding "conformer_esp.dat" file. Depending on the size of the
    conformer and the size of its .out file, this function may take a few
    seconds to run. Returns None.

    PARAMETERS
    ----------
    conf : string
        The three letter + number conformer prefix used to identify the
        different conformers at play.

    """
    # Make sure the "_resp..out" file exists, and that the "_esp.dat" file will
    # not be overwritten
    if os.path.isfile(conf + '_resp.out') is not True:
        raise Exception('File {} is missing!'.format(conf + '_resp.out'))
    if os.path.isfile(conf + '_esp.dat') is True:
        raise Exception('File {} already exists!'.format(conf + '_esp.dat'))
    # Removes any left over temporary files in case of freak accident
    os.remove('esp_tmp01.txt')
    os.remove('esp_tmp02.txt')

    # Retrieves the two ngrid values from the resp.out file (the number
    # of atoms in the molecule, and the number of points involved in
    # the electstatic potential fit). Subtracts the number of atoms from the 
    # number of points, and then appends the number of atoms to the front of 
    # the result. This modified ngrid value is written to the esp.dat file.
    ngrid = []
    with open(conf + '_resp.out', 'r') as f, \
         open(conf + '_esp.dat', 'a') as esp:
        for line in f:
            if re.search('NGrid ', line):
                lines = line.split()
                ngrid.append(line.split()[2])
        ngrid_esp = ngrid[0] + str(int(ngrid[1]) - int(ngrid[0]))
        spacing = 4 + len(ngrid_esp)
        # Four empty spaces must always lead this number. Depending on the
        # character length of the numbers, it is important to let the spacing
        # vary.
        esp.write('{v:>{s}}\n'.format(v=ngrid_esp,s=spacing))

    # Retrieves the "Atomic Centers" from the "_resp.out" file and writes them
    # to the "_esp.dat" file in fortran scientific notation
    atomic_centers = []
    with open(conf + '_resp.out', 'r') as f, \
         open(conf + '_esp.dat', 'a') as esp:
        for line in f:
            if re.search('Atomic Center ', line):
                atomic_centers.append(line.split()[5:8])
        # Formats the numbers in fortran format using nonstandard module
        numberformat1 = ff.FortranRecordWriter('1E32.6')
        numberformat2 = ff.FortranRecordWriter('1E16.6')
        for i in range(0,len(atomic_centers)):
            x = float(atomic_centers[i][0])
            y = float(atomic_centers[i][1])
            z = float(atomic_centers[i][2])
            esp.write('{}{}{}\n'.format(numberformat1.write([x]), \
                                        numberformat2.write([y]), \
                                        numberformat2.write([z])))

    # Writes the "ESP Fit Center" and "Fit" values from the "_resp.out" file to
    # two temporary files, respectively. Trying to store this much data in 
    # memory (i.e. in a list) could be risky.
    with open(conf + '_resp.out', 'r') as f, \
         open('esp_tmp01.txt', 'w') as b, \
         open('esp_tmp02.txt', 'w') as c:
        for line in f:
            if re.search('ESP Fit', line):
                b.write(line)
            if re.search('Fit    ', line):
                c.write(line)

    # Formats and writes the content of the temporary files to the "_esp.dat"
    # file. First column is the "Fit" value, followed by the "ESP Fit Center"
    # values in the remaining three columns. Each of the "ESP Fit Center"
    # values is divided by a conversion factor.
    cnv_factor = 0.529177249
    with open('esp_tmp01.txt', 'r') as b, \
         open('esp_tmp02.txt', 'r') as c, \
         open(conf + '_esp.dat', 'a') as esp:
        for line_b, line_c in zip(b, c):
            esp_fit = line_b.split()
            fit = line_c.split()
            w = float(fit[2])
            x = float(esp_fit[6]) / cnv_factor
            y = float(esp_fit[7]) / cnv_factor
            z = float(esp_fit[8]) / cnv_factor
            # Formats the numbers in fortran format using nonstandard module
            numberformat = ff.FortranRecordWriter('(1E16.6)')
            esp.write('{}{}{}{}\n'.format(numberformat.write([w]), \
                                          numberformat.write([x]), \
                                          numberformat.write([y]), \
                                          numberformat.write([z])))
    # Removes the temporary files from the directory
    os.remove('esp_tmp01.txt')
    os.remove('esp_tmp02.txt')
    return None

# def hb_fortran_format(number):
#     """ Formats a string of digits to look like the scientific notation in
#     fortran. """
#     if number.startswith('-'):   # Correctly formats the number if it is
#     negative
#         number = number[1:]
#         a = '{:.5E}'.format(float(number))           #
#         e = a.find('E')
#         num = '-'
#         +'0.{}{}{}{:02d}'.format(a[0],a[2:e],a[e:e+2],abs(int(a[e+1:])*1+1))
#     else:                   # Correctly formats the number if it is psoitive
#         a = '{:.5E}'.format(float(number))
#         e = a.find('E')
#         num =
#         '0.{}{}{}{:02d}'.format(a[0],a[2:e],a[e:e+2],abs(int(a[e+1:])*1+1))
#     if num == '-0.000000E+01':
#         num = '-0.000000E+00'
#     return num
# ----------------------------------------------------------------------------
#         with open('esp_tmp01.txt', 'r') as b, \
#              open('esp_tmp02.txt', 'r') as c, \
#              open(conf + '_esp.dat', 'a') as esp:
#             for line_b, line_c in zip(b, c):
#                 esp_fit = line_b.split()
#                 fit = line_c.split()
#         
#                 esp_fit[6] = hb_fortran_format(esp_fit[6])
#                 esp_fit[7] = hb_fortran_format(str(float(esp_fit[7])/cnv_factor))
#                 esp_fit[8] = hb_fortran_format(str(float(esp_fit[8])/cnv_factor))
#         
#                 fit[2] = hb_fortran_format(str(float(fit[2])/cnv_factor))
#         
#                 esp.write('{}{}{}{}\n'.format())
#         
#                 line_new = '{:>16}  {:>14}  {:>14}  {:>14}'.format(esp_fit[6],
#                 esp_fit[7], esp_fit[8], fit[2]) + '\n'   # Correctly format the
#                 esp.write(line_new)

# Check punch file for convergence (compare q0 to qopt)
def check_convergence(f='punch'):
    """
    This function compares the values in the "q0" column of a "punch" 
    file to the "qopt" column. When all q0 = qopt, this indicates that 
    the resp fitting has converged.

    PARAMETERS
    ----------
    f : string
        Filename (should always just be "punch")

    RETURNS
    -------
    Returns True if converged or False if not yet converged.

    """
    # Check if a punch file exists
    if os.path.isfile(f) is not True:
        raise FileNotFoundError('File {} is missing!\n'.format(f))
    # Open punch file and save lines to memory (isolate items indexed
    # at '2' and '3' where applicable
    punch = []
    with open(f, 'r') as punchfile:
        for line in punchfile:
            punch.append(line.split()[2:4])
    # Delete the first 11 lines and the last 5 lines
    del punch[:11]
    del punch[-6:]
    # Make separate lists for the q0 and qopt values
    q0 = []
    qopt = []
    for q in punch:
        q0.append(q[0])
        qopt.append(q[1])
    # Determine convergence
    if q0 == qopt is True:
        return True
    else:
        return False


if __name__=="__main__":

    cwd = os.getcwd()
    check_filepath('namelist.in')
    
    namelist = read_namelist('namelist.in')
    job = namelist[0]["jobtype"]
    
""" JOB TYPE 1 """    
    if job == "1":
        resname = namelist[0]["resname"]
        chrg = namelist[0]["charge"]
        mult = namelist[0]["multiplicity"]
        nconf = int(namelist[0]["nconf"])
    
        for i in range(0,nconf):
            conformer = namelist[1][i] # conformer iterator
            write_submission_script(conformer+"_geom.pbs",conformer,"geom")
            write_submission_script(conformer+"_resp.pbs",conformer,"resp")
            write_geom_input(conformer+"_geom.inp",resname,conformer,chrg,mult)
            write_resp_input(conformer+"_resp.inp",resname,conformer,chrg,mult)
            os.mkdir(conformer)

            # Move any files for the conformer ending in pbs into its directory
            for f in glob.glob(conformer+'*pbs'):
                shutil.move(f, conformer)

            # Move any files for the conformer ending in inp into its directory
            for f in glob.glob(conformer+'*inp'):
                shutil.move(f, conformer)

    #     # Submits the pbs files in each directory
    #     for i in [0,nconf-1]:
    #         conformer = namelist[1][i] # conformer iterator
    #         os.chdir(conformer) # enter conformer directory
    #         # submit all files ending in pbs to Talapas
    #         sb.check_call("sbatch -A richmondlab *pbs", shell=True)
    #         os.chdir(cwd) # return to working directory
    
""" JOB TYPE 2 """
    elif job == "2":

        # Generate esp.dat files
        for i in range(0,nconf):
            write_esp_dat(namelist[1][i])

        # Concatenate all esp.dat files
        sp.check_call("cat *esp.dat > espot", shell=True)

        # END STEP 6 --- START STEP 7

        # Build the first resp.in file
        write_resp_in('resp.in',nconfs,'1','1','00')

        # END STEP 7 --- START STEP 8

        # Run the resp fit for the first time
        # -q qin not required since iqopt = 1
        sp.check_call("resp -O -i resp.in -o resp.out -e espot", shell=True)

        # Check punch file to make sure everything is working

        # Duplicate qout as qin (output charge file becomes the input charge
        # file for the next resp fit)
        sp.check_call("cp qout qin", shell=True)

        # Rename punch, qout, espot files to punch##, qout##, espot## so that
        # the files are backed up and don't get overwritten
        os.rename('punch', 'punch{}'.format(0))
        os.rename('qout', 'qout{}'.format(0))
        os.rename('espot', 'espot{}'.format(0))

        """
        STEP 9 SHOULD BE DONE MANUALLY?

        # END STEP 8 --- START STEP 9

        try:
            sp.check_call(
                "cp /packages/amber/12/dat/leap/parm/parm99.dat ./", \
                 shell=True)
        except:
            raise FileNotFoundError('Could not find parm99.dat file!\n')

        # Check the parameters with one of (the first in this case) mol files
        sp.check_call(
            "parmchk -i {}1.mol2 -o {}.frcmod -f mol2 -p parm99.dat".format(
                resname), shell=True)
        
        # Checks the parameters automatically
        with open(resname + '.frcmod', 'r') as f:
            for line in f:
                if re.search('ATTN', line):
                    raise Exception('ATTN Error detected in .frcmod file!\n')
        """







        # Copy charges for first molecular unit of qout and copy to qnext
        # This sets up the input charges for JOB TYPE 3
        






        write_resp_in('resp.in',nconfs,'2','1','00')
        write_resp_in('resp.in',nconfs,'2','0','05')
        write_resp_in('resp.in',nconfs,'2','0','1')


def write_resp_in(f='resp.in',nconfs,iqopt,ihfree,qwt)
    """
    UNFINISHED
    """
    if os.path.isfile(f) is True:
        raise Exception('File {} already exists!\n'.format(f))

    with open(f, 'a') as outfile:
        # Writes the header options
        outfile.write("Resp charges for organic molecule\n\n")
        outfile.write(" &cntrl\n\n")
        outfile.write(" nmol = {},\n".format(nconfs))
        outfile.write(" ihfree = {},\n".format(ihfree))
        outfile.write(" iqopt = {},\n".format(iqopt))
        outfile.write(" qwt = 0.00{},\n\n".format(qwt))
        outfile.write(" &end\n")

        # Writes the first three lines of each molecule table
        for i in range(0,nconf):
            outfile.write("    1.0\n")
            outfile.write("{}".format(conf[i]))
            outfile.write("    charge    numberofatoms")

            # Writes the atom identities and restrictions for each molecule
            for j in range(0,numberofatoms):
                outfile.write("    atomidentity[j]    0")
            outfile.write("\n")

        # Writes the table of conformers and atoms
        conf = 1
        atom = 1
        for i in range(0,natom):
            outfile.write('\n{n:>5d}\n'.format(n=nconf))
            for j in range(0,nconf):
                outfile.write('{n:>5d}{m:>5d}'.format(n=conf,m=atom))
                conf += 1
            conf = 1
            atom += 1














    """Job type = 2 steps:
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
    """

    """ Iterating through the RESP fitting routine until convergence achieved
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
    """


    # Move files to the RESP directory
    # Note-- This moves GeomRespCreator2.py to the RESP directory. Have to think
    # about if this is necessary

        resp_dir = os.mkdir('RESP')

        resp_files =['namelist.in',
                     'GeomRespCreator.py',
                     'leaprc.ff02pol.r1',
                     ]

def write_leap_in(f='leap.in',resname):
    """
    """
    if os.path.isfile(f) is True:
        raise Exception('File {} already exists!\n'.format(f))
    with open(f, 'a') as outfile:
        outfile.write("set default IPOL 1\n\n")
        outfile.write("source leaprc.ff02pol.r1\n\n")
        outfile.write("loadamberparams {}.frcmod\n\n".format(resname))
        outfile.write("x = loadmol2 Temp.mol2\n\n")
        outfile.write("check x\n")
        outfile.write("saveAmberParmPol x prmtop prmcrd\n\n")
        outfile.write("quit")
    return None

def write_sander_in():
    """
    """
    if os.path.isfile(f) is True:
        raise Exception('File {} already exists!\n'.format(f))
    with open(f, 'a') as outfile:
        outfile.write("Title\n")
        outfile.write(" &cntrl\n")
        outfile.write("  irest=0,ntx=1,\n")
        outfile.write("  imin=1,maxcyc=1,\n")
        outfile.write("  ntc=1,ntf=1,\n")
        outfile.write("  cut=999.0,\n")
        outfile.write("  ntpr=100,ntwx=0,ntwv=0,ntwe=0,\n")
        outfile.write("  ipol=1,iesp=1,\n")
        outfile.write("  igb=0,ntb=0,\n")
        outfile.write(" &end\n")
        outfile.write(" &ewald\n")
        outfile.write("  indmeth=1\n")
        outfile.write(" &end")
    return None










        for files in os.listdir():
            if filename.endswith('_resp.out'):
                shutil.move(files, resp_dir)
            if filename.endswith('.mol2'):
                shutil.move(files, resp_dir)



        resp_dir = os.mkdir('RESP')
        cwd = os.chdir('RESP')

        for i in range(0,nconf): 
            conf = resname + str(i + 1)
            write_esp_dat(conf)

        esp_filelist = []
        cwd = os.getcwd()
        # Create a list of [ABC]_esp.dat files that is sorted based on the
        # number in the file name.
        for files in os.listdir(cwd):
            if filename.endswith("_esp.dat"):
                esp_filelist.append(filename)
            esp_filelist = sorted(esp_filelist, key=lambda x: 
                          int("".join([i for i in x if i.isdigit()])
                             )
                         )

        # Concatenate all esp.dat files into the espot file.
        with open('espot', 'w') as espot:
            for i in esp_filelist:
                with open(os.path.join(cwd,i)) as infile:
                    for line in infile:
                        espot.write(line)



""" JOB TYPE 3 """
    elif job == "3":
        print("job3")
    
    # Use sp.check_call("bash cmd", shell=True)
    
    # Note: sp.check_call() and sp.run() should ALWAYS be
    # preferred over sp.call(), sp.Popen(), os.system(), and 
    # os.popen().
    
""" JOB TYPE 4 """
    elif job == "4":
        print("job4")
    
""" UNRECOGNIZED JOB TYPE """    
    else:
        raise ValueError('Unacceptable job type chosen. Check namelist.in \
        file and try again.\n')
