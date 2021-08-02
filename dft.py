#!/usr/bin/env python

"""

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

    """

    def print_menu():
        title = "GAUSSIAN MENU"
        formatting = int((78 - len(title)) / 2) * '-'
        print(formatting, title, formatting, '\n')
        print('I want to...\n')
        print('1. Write and submit calculations to Gaussian.\n')
        print('2. Check output files for correct termination.\n')
        print('3. Pull molecular coordinates from output files.\n')
        print('#. Exit the program.\n')
        print(79 * '-', '\n')

    def get_choice():
        while True:
            print_menu()
            choice = input('Enter your choice [1-4]: ')
            print()

            if choice == '1':
            elif choice == '2':
            elif choice == '3':
            elif choice == '4':
            elif choice == '#':
                sys.exit('Program halted by user.\n') 
            else:
                input('"{}" is not an option. Try again.\n'.format(choice))

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

def make_inp_template(path,templatetype):
    templatepath = 
        os.path.join(path,'templates/','template_{}.inp'.format(templatetype))
    try:
        with open(templatepath, 'w') as f:
            f.write("%NProcShared=12\n")
            f.write("%mem=12GB\n")
            f.write("%rwf=/tmp/template_{}/,-1\n".format(templatetype))
            f.write("%chk=/tmp/template_{}/template_{}.chk\n".format(templatetype))
            if templatetype == 'opt':
                f.write("#P B3LYP/6-311++G(2d,2p) opt(tight,MaxCycles=1000) scf(tight,MaxCycles=1000)\n\n")
                f.write("Gaussian09 geometry optimization at B3LYP/6-311++G(2d,2p)\n\n")
            elif templatetype == 'hf':
                f.write("#P HF/6-31G* opt(tight,MaxCycles=1000) scf(tight,MaxCycles=1000)\n\n")
                f.write("Gaussian09 geometry optimization at HF/6-31G*\n\n")
            elif templatetype == 'freq':
                f.write("#P B3LYP/6-311++G(2d,2p) Freq(HPModes) scf(tight,MaxCycles=1000)\n\n")  
                f.write("Gaussian09 harmonic vibrational frequency calculation at B3LYP/6-311++G(2d,2p)\n\n")
            elif templatetype == 'anharm':
                f.write("#P B3LYP/6-311++G(2d,2p) Freq(Anharmonic) scf(tight,MaxCycles=1000)\n\n")
                f.write("Gaussian09 anharmonic vibrational frequency calculation at B3LYP/6-311++G(2d,2p)\n\n")
            elif templatetype == 'geom':
                f.write("#P HF/6-31G* opt(tight,MaxCycles=1000) scf(tight,MaxCycles=1000)\n\n")
                f.write("Gaussian09 geometry optimization at HF/6-31G*\n\n")
            elif templatetype == 'resp':
                f.write("#P B3LYP/c-pVTZ scf(tight,MaxCycles=1000) Pop=MK IOp(6/33=2,6/41=10,6/42=17)\n\n")
                f.write("Gaussian09 single point electrostatic potential calculation at B3LYP/c-pVTZ\n\n")
            else:
                f.write("#P [functional]/[basisset] [calculation type]\n\n")
                f.write("Gaussian09 [calculation type] at [functional]/[basisset]\n\n")
            f.write("0 1\n")
    except FileNotFoundError:
        print('\nUnable to find the templates/ directory.\n')
        print('Unable to write the template_{}.inp file.\n'.format(templatetype))
        print('Program must be executed from the main project directory.\n')
    finally:
        return None

def make_inp_file(path,resname,conf,inptype):
    """ Creates the "conformer_geom.inp" file, using the information
    loaded from the "namelist.in" file. Loads molecular coordinates from
    the .xyz file format (REQUIRED). Returns None.

    PARAMETERS
    ----------
    resname : string
        Three letter residue prefix
    conf : string
        Three letter residue prefix + integer (conformer index number)
    inptype : string
        One of six acceptable values designating the type of .inp file desired
        Acceptable options:
        opt     - [DFT] geometry optimization
        hf      - [DFT] geometry optimization (error minimization)
        freq    - [DFT] gas phase vibrational mode calculation
        anharm  - [DFT] gas phase vibrational anharmonics calculation
        geom    - [MD]  geometry optimization (error minimization)
        resp    - [MD]  electrostatic potential single point calculation

    """
    inp = os.path.join(path,'templates/','template_{}.inp'.format(inptype))
    xyz = os.path.join(path,'geometries/','{}.xyz'.format(conf))
    out = os.path.join(path,'{0}_{1}.inp'.format(conf,inptype))

    # Copies information from template file to actual .inp file
    try:
        with open(inp, 'r') as header,
             open(out, 'w') as f:
            for line in header:
                f.write(line)
    except FileNotFoundError:
        print('Template file {} cannot be found.\n'.format(inp))
        print('Aborting {} file creation...\n'.format(out))
        return None

    # Replaces place holders from template with conformer designations 
    with open(out, 'r+') as f:
        for line in f:
            if 'template' in line:
                line.replace('template',conf)

    # Loads the molecular geometry into a list called "coords"
    try:
        coords = []
        with open(xyz, 'r') as cartesiancoords:
            for line in cartesiancoords:
                lines = line.split()
                coords.append(lines)
    except FileNotFoundError:
        print('Molecular coordinate file {} cannot be found.\n'.format(xyz))
        print('Aborting {} file creation...\n'.format(out))
        os.remove(out)
        return None

    # Removes the first two header lines of the xyz file 
    # Removes any lines without exactly four items (atom, x, y, z coords)
    del coords[0]
    del coords[0]
    for i in range(len(coords)):
        if len(coords[i]) != 4:
            del coords[i]

    # Appends the formatted molecular coordinates to the .inp file
    with open(out, 'a') as f:
        for i in range(0,len(coords)):
            a = format(coords[i][0],'<3s')
            x = format(float(coords[i][1]),'15.5f')
            y = format(float(coords[i][2]),'15.5f')
            z = format(float(coords[i][3]),'15.5f')
            f.write('{}{}{}{}\n'.format(a, x, y, z))
        f.write('\n')
    return None

def make_pbs_template(path,templatetype):
    templatepath = 
        os.path.join(path,'templates/','template_{}.pbs'.format(templatetype))
    if templatetype == 'anharm':
        partition = 'long'
        ntasks = '28'
        walltime = '14'
    else:
        partition = 'short'
        ntasks = '14'
        walltime = '1'
    try:
        with open(filepath, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("#SBATCH --account=richmond\n")
            f.write("#SBATCH --partition={}\n".format(partition))
            f.write("#SBATCH --nodes=1 ### 14 cores per CPU, 2 CPU per node\n")
            f.write("#SBATCH --ntasks-per-node={} ### Number of MPI processes\n".format(ntasks))
            f.write("#SBATCH --time={}-00:00:00\n".format(walltime))
            f.write("#SBATCH --export=ALL\n")
            f.write("#SBATCH --error=template_{}.err\n\n".format(templatetype))
            f.write("test -d /tmp/template_{} || mkdir -v /tmp/template_{}\n\n".format(templatetype))
            f.write("module load intel-mpi\n")
            f.write("module load mkl\n")
            f.write("module load gaussian\n\n")
            f.write("which g09\n\n")
            f.write("g09 < template_{}.inp > template_{}.out\n\n".format(templatetype))
            f.write("cp -pv /tmp/template_{}/template_{}.chk .\n\n".format(templatetype))
            f.write("rm -rv /tmp/template_{}\n\n".format(templatetype))
    except FileNotFoundError:
        print('\nUnable to find the templates/ directory.\n')
        print('Unable to write the template_{}.pbs file.\n'.format(templatetype))
        print('Program must be executed from the main project directory.\n')
    finally:
        return None

def make_pbs_file(path,resname,conf,pbstype):
    """ Creates the .pbs submission script for any .inp files.
    Returns None.

    --- PARAMETERS ---
    path : string
        Path + name of the .pbs file written by this function.
    resname : string
        Three letter prefix for the molecule
    conf : string
        Three letter residue prefix + integer (conformer index number)
    pbstype : string
        One of six acceptable values designating the type of .inp file desired
        Acceptable options:
        opt     - [DFT] geometry optimization
        hf      - [DFT] geometry optimization (error minimization)
        freq    - [DFT] gas phase vibrational mode calculation
        anharm  - [DFT] gas phase vibrational anharmonics calculation
        geom    - [MD]  geometry optimization (error minimization)
        resp    - [MD]  electrostatic potential single point calculation

    """

    pbs = os.path.join(path,'templates/','template_{}.pbs'.format(pbstype))
    out = os.path.join(path,'{0}_{1}.pbs'.format(conf,pbstype))

    # Copies information from template file to actual .inp file
    try:
        with open(pbs, 'r') as header,
             open(out, 'w') as f:
            for line in header:
                f.write(line)
    except FileNotFoundError:
        print('Template file {} cannot be found.\n'.format(pbs))
        print('Aborting {} file creation...\n'.format(out))
        return None
    else:
        # Replaces place holders from template with conformer designations 
        with open(out, 'r+') as f:
            for line in f:
                if 'template' in line:
                    line.replace('template',conf)
        return None


def check_termination(path):
    """ Checks gaussian out files for normal termination.
    UNFINISHED
    """
    termination = False
    try:
        with open(path, 'r') as f:
            for line in f:
                if 'Normal termination of Gaussian ' in line:
                    termination = True
    except FileNotFoundError:
        print('\nUnable to find/open {}\n'.format(path))
        print('Cannot check {} for normal termination of Gaussian.\n'.format(path))
        return False
    else:
        if termination == False:
            print('{} did not terminate correctly!'.format(path))
            return False
        else:
            return True



def make_xyz():

    def get_coords(path):
        firstline = 0
        lastline = 0
        i = 0
        try:
            with open(path, 'r') as f:
                for i,line in enumerate(f):
                    if 'Standard orientation:' in line:
                        firstline = max(i, firstline)
                    if 'Rotational constants ' in line:
                        lastline = max(i, lastline)
            return firstline, lastline
        except FileNotFoundError:
            print('Unable to open file {}.\n'.format(path))
            return None

    def format_coords(path,start,end):
        coords = []
        with open(path, 'r') as f:
            for i,line in enumerate(f):
                if i >= start+5 and i <= end-2:
                    coords.append(line.split())
        for i in range(len(coords)):
            del coords[i][2]
            del coords[i][0]
        atomicnumber = {
            1 : 'H',
            2 : 'He',
            3 : 'Li',
            4 : 'Be',
            5 : 'B',
            6 : 'C',
            7 : 'N',
            8 : 'O',
            9 : 'F',
            10 : 'Ne',
            11 : 'Na',
            12 : 'Mg',
            13 : 'Al',
            14 : 'Si',
            15 : 'P',
            16 : 'S',
            17 : 'Cl',
            18 : 'Ar',
            19 : 'K',
            20 : 'Ca',
            21 : 'Sc',
            22 : 'Ti',
            23 : 'V',
            24 : 'Cr',
            25 : 'Mn',
            26 : 'Fe',
            27 : 'Co',
            28 : 'Ni',
            29 : 'Cu',
            30 : 'Zn',
            31 : 'Ga',
            32 : 'Ge',
            33 : 'As',
            34 : 'Se',
            35 : 'Br',
            36 : 'Kr',
            37 : 'Rb',
            38 : 'Sr',
            39 : 'Y',
            40 : 'Zr',
            41 : 'Nb',
            42 : 'Mo',
            43 : 'Tc',
            44 : 'Ru',
            45 : 'Rh',
            46 : 'Pd',
            47 : 'Ag',
            48 : 'Cd',
            49 : 'In',
            50 : 'Sn',
            51 : 'Sb',
            52 : 'Te',
            53 : 'I',
            54 : 'Xe'}
        for i in range(len(coords)):
            coords[i][0] = atomicnumber[int(coords[i][0])]
        return coords

    def write_xyz(path,coords):
        with open(path, 'w') as f:
            f.write(str(len(coords))+'\n')
            f.write('comment line\n')
            for item in coords:
                f.write('{:<}{:>16}{:>14}{:>14}\n'.format(item[0],item[1],item[2],item[3]))
        return None

    cwd = os.getcwd()
    outpath = os.path.join(cwd,filename)
    textblock = get_coords(outpath)
    coords = format_coords(outpath,textblock[0],textblock[1])

    xyzpath = os.path.join(cwd,filename)
    write_xyz(xyzpath,coords)













































