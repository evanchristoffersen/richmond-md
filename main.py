#!/usr/bin/env python

""" This is a re-write of GeomRespCreator_slurm.f90.  Originally written
in Fortran 90 and now ported over to Python3.

Authors (alphabetical): Evan Christoffersen Konnor Jones

Python Version: 3.9.2

Update Log:

#SBATCH --account=appquantchem   
Account to bill needs to be added to the top of the .pbs files. 

The each conformer .pbs file needs to create a scratch directory and 
.chk file

Maybe have two versions of the program--one that is lightly
commented and the other be more heavily commented?

On line 612, write_geom_input() requires 2 additional arguments (nodes 
and memory). I temporartly added two additional arguments so I could 
proceed with debugging the program. These temporary place holders need 
to be changed.

Added code so there are two empty lines in the .inp files.

Adjusted the spacing between columns in geom.inp and resp.inp files to 
match the spacing of files that I have successfully ran on Talapas

Program now successfully submits all geomery optimization jobs to 
Talapas, except for conformer0 - this needs to be corrected



With the short tail tail version of SDS, assure the Python and Nick's 
program create exactly the same files. Evan--I have already run some of 
the jobs, so I need to give you the files, if I haven't already.




TEST DATA SET: 
This data set would preferably be 12 conformers total of some small
molecule that would take only seconds to minutes to run the calculations
for, but would still have at least 12 atoms, where some of the atoms are
heavier than Ne. Maybe like a short chain SDS molecule. Let's say
propanol with a sulfate head group. I chose this molecule because I want
to confirm that all of the files format correctly when handling numbers
that are 1 character and 2 characters long.

OTHER:
The popular computational open source tool: "open babel" will
automatically make .mol2 copies of any and all .xyz files using the
command: obabel *.xyz -omol2 -m but it may require installation of
open babel on Talapas, which probably isn't possible. This will save
us from having to write a function to build .mol2 files from
scratch, hopefully. .mol2 files seem very complicated, and I imagine
even if we got a function working that we wrote to convert .xyz to
.mol2, it would be buggy and likely not stand the test of time.

"""



import glob # File selection wildcard *
import os # Change directories and prevent file overwrite
import re # Regular expressions (i.e. grep)
import shutil # Move files between directories
import subprocess as sp # Run shell commands
import sys # Error management



__authors__ = 'Evan Christoffersen', 'Konnor Jones'
# __license__
# __version__



def main_menu():
    """
    UNFINISHED
    """
    def print_main_menu():
        title = "MAIN MENU"
        formatting = int( (78 - len(title)) / 2 ) * "-"
        print(formatting, title, formatting, "\n")
        print("I want to...")
        print("1. Build conformer libraries and run electronic structure calculations.")
        print("2. Build the force fields for MD simulations (RESP fitting).")
        print("3. Read more about what this program does.")
        print("4. Exit the program.\n")
        print(79 * "-", "\n")

    loop = True

    while loop:
        print_main_menu()
        choice = input("Enter your choice [1-4]: ")
        print()

        if choice == "1":
            loop = False
            # return dft_menu()
        elif choice == "2":
            loop = False
            return resp_menu()
        elif choice == "3":
            help(main_menu)
        elif choice == "4":
            loop = False
            raise SystemExit
        else:
            input('ERROR: {} is not at option. Try again.\n'.format(choice))


def main():
    """ This is the main program.
    UNFINISHED
    """

    main_menu()

if __name__=="__main__":
    main()

# cwd = os.getcwd()
# 
# namelist = read_namelist('namelist.in')
# job = namelist[0]["jobtype"]
# 
# #  JOB TYPE 1
# 
# if job == "1":
# 
#     # Make .inp and .pbs files for geom and resp calculations and move them
#     # into their own directories
#     for i in range(0,nconf):
#         conformer = namelist[1][i]
#         write_submission_script(conformer+"_geom.pbs",conformer,"geom")
#         write_submission_script(conformer+"_resp.pbs",conformer,"resp")
#         write_geom_input(conformer+"_geom.inp",resname,conformer,chrg,mult, 4, 8)
#         write_resp_input(conformer+"_resp.inp",resname,conformer,chrg,mult, 4, 8)
#         os.mkdir(conformer)
#         for f in glob.glob(conformer+'*pbs'):
#             shutil.move(f, conformer)
#         for f in glob.glob(conformer+'*inp'):
#             shutil.move(f, conformer)
# 
#     # Submits the pbs files in each directory
#     for i in range(0,nconf):
#         conformer = namelist[1][i]
#         os.chdir(conformer)
#         sp.check_call("sbatch -A richmondlab *geom.pbs", shell=True)
#         os.chdir(cwd)
# 
# #  JOB TYPE 2
# 
# elif job == "2":
# 
#     # Generate esp.dat files
#     for i in range(0,nconf):
#         write_esp_dat(namelist[1][i])
# 
#     # Concatenate all esp.dat files
#     sp.check_call("cat *esp.dat > espot", shell=True)
# 
#     # END STEP 6 --- START STEP 7
# 
#     # Build the first resp.in file
#     write_resp_in('resp.in',nconfs,'1','1','00')
# 
#     # END STEP 7 --- START STEP 8
# 
#     # Run the resp fit for the first time
#     # -q qin not required since iqopt = 1
#     sp.check_call("resp -O -i resp.in -o resp.out -e espot", shell=True)
# 
#     # Check punch file to make sure everything is working
# 
#     # Duplicate qout as qin (output charge file becomes the input charge
#     # file for the next resp fit)
#     sp.check_call("cp qout qin", shell=True)
# 
#     # Rename punch, qout, espot files to punch##, qout##, espot## so that
#     # the files are backed up and don't get overwritten
#     os.rename('punch', 'punch{}'.format(0))
#     os.rename('qout', 'qout{}'.format(0))
#     os.rename('espot', 'espot{}'.format(0))
# 
#     """
#     STEP 9 SHOULD BE DONE MANUALLY?
# 
#     # END STEP 8 --- START STEP 9
# 
#     try:
#         sp.check_call(
#             "cp /packages/amber/12/dat/leap/parm/parm99.dat ./", \
#              shell=True)
#     except:
#         raise FileNotFoundError('Could not find parm99.dat file!\n')
# 
#     # Check the parameters with one of (the first in this case) mol files
#     sp.check_call(
#         "parmchk -i {}1.mol2 -o {}.frcmod -f mol2 -p parm99.dat".format(
#             resname), shell=True)
# 
#     # Checks the parameters automatically
#     with open(resname + '.frcmod', 'r') as f:
#         for line in f:
#             if re.search('ATTN', line):
#                 raise Exception('ATTN Error detected in .frcmod file!\n')
#     """
# 
# 
#     """
#     Job type = 2 steps:
# 
#     DONE-- Create RESP directory
#     DONE-- Move files to the RESP directory
#     DONE-- Change the current directory to RESP
#     DONE-- Create esp.dat files for each conformer
#     DONE-- Concatenate all esp.dat files into espot
#     DONE-- For the first resp fit, edit resp.in so iqopt = 1 and for each
#            conformer, list the atoms and the restrictions for the charge and
#            create the matrix at the bottom of the file
#     DONE-- Run the resp fit
# 
#     Get the charges for the first molecular unit from qout and copy them into
#     qnext
# 
#     DONE-- Make a copy of qout and name the file qin
# 
#     Rename punch, qout, and espot to punch#, qout#, and espot# so everything is
#     backed up
# 
#     Run job type = 3 to get updated .mol2 file (I don't think this is
#     necessary. If anything, we just need to run a single command - the
#     antechamber command I think...)
# 
#     DONE-- Copy the parm99.dat file into the RESP folder
# 
#     BY HAND ? Check the parameters with one of the mol2 files
# 
#     BY HAND ? Find suitable replacment parameters in parm99.dat or gaff.dat
# 
#     BY HAND ? Edit the [ABC].frcmod file with the new parameters
# 
#     Edit the leap.in files so it knows to get the modified parameter file
# 
#     """
# 
#     resp_dir = os.mkdir('RESP')
# 
#     for files in os.listdir():
#         if filename.endswith('_resp.out'):
#             shutil.move(files, resp_dir)
#         if filename.endswith('.mol2'):
#             shutil.move(files, resp_dir)
# 
#     cwd = os.chdir('RESP')
# 
#     for i in range(0,nconf):
#         conf = resname + str(i + 1)
#         write_esp_dat(conf)
# 
#     esp_filelist = []
#     cwd = os.getcwd()
#     # Create a list of [ABC]_esp.dat files that is sorted based on the
#     # number in the file name.
#     for files in os.listdir(cwd):
#         if filename.endswith("_esp.dat"):
#             esp_filelist.append(filename)
#         esp_filelist = sorted(esp_filelist, key=lambda x:
#                       int("".join([i for i in x if i.isdigit()])
#                          )
#                      )
# 
#     # Concatenate all esp.dat files into the espot file.
#     with open('espot', 'w') as espot:
#         for i in esp_filelist:
#             with open(os.path.join(cwd,i)) as infile:
#                 for line in infile:
#                     espot.write(line)
# 
# # Tried to run the program to test job type ==1, but the program will not run
# # --Python doesn't like ' in the code
# """ JOB TYPE 3 """
# elif job == "3":
# 
#     # For each conformer:
# 
#         ' mv ABC#_esp.dat esp.dat '
# 
#         '
#         antechamber -o Temp.mol2 -fo mol2 -c rc -cf qnext -at amber -fi
#             mol2 -i ABC#.mol2 -rn ABC
# 
#             -o    : output file name
#             -fo   : output file format
#             -c    : charge method
#             -cf   : charge file name
#             -at   : atom type (gaff [default], amber, bcc, sybyl)
#             -fi   : input file format
#             -i    : input file name
#             -rn   : residue name (overrides input file [default = MOL])
#             -help : gives full flag menu for antechamber
# 
#             -i, -o, -fi, -fo MUST appear. All other flags are optional.
#         '
# 
#         '
#         tleap -s -f leap.in
# 
#             -s : ignore leaprc startup file
#             -f : source file
#         '
# 
#         '
#         sander -O -i sander.in -o sander.out -c prmcrd -p prmtop
# 
#             -O : overwrite output files
#             -i : input control data for the min/md run
#             -o : output user readable state infor and diagnostics (-o
#             stdout will send output to stdout (to the terminal) instead of
#             to a file)
#             -c : input initial coordinates and (optionally) velocities and
#             periodic box size
#             -p : input molecular topology, force field, periodic box type,
#             atom and residue names
#         '
# 
#         ' rm ANTECHAMBER* ATOMTYPE.INF leap.log mdinfo prmcrd sander.out
#            restrt '
# 
#         ' mv Temp.mol2 ABC#.mol2 '
# 
#         ' mv esp.dat ABC#_esp.dat '
# 
#         ' mv prmtop ABC#.top '
# 
#         ' mv esp.induced ABC#_esp.induced '
# 
#         ' mv esp.qm-induced ABC#_esp.qm-induced '
# 
#     sp.check_call("mv {}_esp.dat esp.dat".format(conf))
# 
#     sp.check_call(\
#         'antechamber -o Temp.mol2 -fo mol2 -c rc -cf qnext -at amber \
#         -fi mol2 -i {}.mol2 -rn {}'.format(conf,resname)
# 
# # Use sp.check_call("bash cmd", shell=True)
# # Note: sp.check_call() and sp.run() should ALWAYS be
# # preferred over sp.call(), sp.Popen(), os.system(), and
# # os.popen().
# 
# """ UNRECOGNIZED JOB TYPE """
# else:
#     raise ValueError('Unacceptable job type chosen. Check namelist.in \
#     file and try again.\n')

