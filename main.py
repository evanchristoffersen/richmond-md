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

# from . import namelist
# from . import resp

import namelist
import resp



__authors__ = 'Evan Christoffersen', 'Konnor Jones'
# __license__
# __version__



def build_directory_space():
    """ Builds the folder tree hierarchy for the this computational
    work. Note: messing with the generated structure will prevent this
    program from functioning properly.

    """
    def get_project_name():
        """ Prompts user for project/main directory name. 
        
        """
        while True:
            q = input('Enter the name for this project: ')
            # User must input something
            if len(q) == 0:
                print('\nERROR: Project must have a name.\n')
            # Symbols make for bad directory names
            elif re.search(r'[^a-zA-Z0-9_-]',q):
                print('\nERROR: Only alphanumeric, "-", and "_" characters allowed.\n')
            # Make sure directory doesn't already exist
            elif os.path.exists(q) == True:
                print('\nERROR: Project already exists.\n')
            else:
                return q

    def build_tree(project):
        """ Builds the directory tree.
        
        --- PARAMETERS ---
        project : string
            The head directory/project name.
        
        """
        directorylist = [
            project,
            '{}/DFT'.format(project),
            '{}/DFT/conformer_files'.format(project),
            '{}/DFT/geometries'.format(project),
            '{}/DFT/libraries'.format(project),
            '{}/DFT/templates'.format(project),
            '{}/MD'.format(project),
            '{}/MD/geometries'.format(project),
            '{}/MD/templates'.format(project)]
        for item in directorylist:
            try: os.mkdir(item)
            except FileExistsError: pass
        return None

    name = get_project_name()
    build_tree(name)
    return None


def find_path(searchquery):
    """

    """
    results = []
    for paths, dirs, files in os.walk('.', topdown=False)
        for f in files:
            out = os.path.join(paths, f)
            if '{}'.format(searchquery) in out:
                results.append(out)
    return results


def main_menu():
    """ Display's the main menu for this program, and handles the user's
    choices based on the menu options.

    """
    def print_menu():
        title = "MAIN MENU"
        formatting = int((78 - len(title)) / 2) * '-'
        print(formatting, title, formatting, '\n')
        print('I want to...\n')
        print('1. Set up my project directory tree.')
        print('2. Build conformer libraries and run electronic structure calculations.')
        print('3. Build the force fields for molecular dynamices simulations (RESP fitting).')
        print('4. Read more about these menu options.')
        print('5. Exit the program.\n')
        print(79 * '-', '\n')

    def get_choice():
        while True:
            print_menu()
            choice = input("Enter your choice [1-4]: ")
            print()

            if choice == '1':
                return build_directory_space()
            elif choice == '2':
                return dft_menu()
            elif choice == '3':
                return md_menu()
            elif choice == '4':
                help(main_menu)
            elif choice == '5':
                sys.exit('Program halted by user.\n')
            else:
                input('"{}" is not at option. Try again.\n'.format(choice))

    get_choice()


def main():
    """ Function called by __main__

    """
    main_menu()

if __name__=="__main__":
    main()

