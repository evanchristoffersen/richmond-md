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

# import namelist
# import resp



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

def find_filepath(searchquery, showhidden=False):
    """

    """
    searchresults = []
    for paths, dirs, files in os.walk('.', topdown=False):
        for f in files:
            if searchquery in f:
                if f.startswith('.') and showhidden == False:
                    pass
                else:
                    out = os.path.join(paths, f)
                    searchresults.append(out)
    return searchresults

def find_dirpath(searchquery, showhidden=False):
    """

    """
    searchresults = []
    for paths, dirs, files in os.walk('.', topdown=False):
        for d in dirs:
            if searchquery in d:
                if d.startswith('.') and showhidden == False:
                    pass
                else:
                    out = os.path.join(paths, d)
                    searchresults.append(out)
    return searchresults


def get_integer(prompt, negative = False):
    """ Gets integer values from the user, checking the integer's
    sign and that it isn't a different type.

    --- PARAMETERS ---
    prompt : string
        The desired parameter you wish to prompt from the user.
    negative : Boolean
        True -> negative integer values are allowed
        False -> negative integer values are not allowed (default)

    --- RETURNS ---
    out : string                                                            
        Integer value from user as string type                              

    """
    while True:
        try:
            out = int(input(prompt))
            if int(out) < 0 and negative == False:
                print('\nERROR: Enter a positive integer value.\n')
            else:
                return str(out)
        except(ValueError, TypeError):
            print('\nEnter an integer value.\n')

def print_file_contents(path):
    print('\nReviewing contents of {}:\n'.format(path))
    try:
        with open(path, 'r') as f:
            for line in f:
                print(line)
        input('Press any key to continue...\n')
    except FileNotFoundError:
        print('File not found.\n')
        print('Cannot display contents of file {}\n'.format(path))
    finally:
        return None

def fortran_format(n):
    """ Formats a string of digits to look like the scientific
    notation in fortran.

    --- PARAMETERS ---
    n : string
        The number that needs to be converted to fortran's scientific
        notation. Must be convertable to a float type for function to
        work (i.e. string must not contain any letters).

    --- RETURNS ---
    out : string
        The number formatted in fortran scientific notation is returned
        as a string.

    """
    # Explicity handle the case of -0.0
    if n.startswith('-') and float(n) == 0:
        out = '-0.000000E+00'
        return out
    # Explicitly handle the case of 0.0
    elif float(n) == 0:
        out = '0.000000E+00'
        return out
    # Handle all negative non-zero numbers
    elif n.startswith('-'):
        n = n[1:]
        a = '{:.5E}'.format(float(n))
        e = a.find('E')
        out = '-' + '0.{}{}{}{:02d}'.format(
            a[0], a[2:e], a[e:e+2], abs(int(a[e+1:])+1))
        if out.endswith('E-00'):
            out = out[:-3]
            out = out + '+00'
        return out
    # Handle all other possibilities (i.e. positive non-zero numbers)
    else:
        a = '{:.5E}'.format(float(n))
        e = a.find('E')
        out = '0.{}{}{}{:02d}'.format(
            a[0], a[2:e], a[e:e+2], abs(int(a[e+1:])+1))
        if out.endswith('E-00'):
            out = out[:-3]
            out = out + '+00'
        return out

def main():
    """ Function called by __main__

    """
    main_menu()

if __name__=="__main__":
    main()

