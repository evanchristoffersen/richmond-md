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
        except:
            print('\nERROR: Enter an integer value.\n')

# def check_template_exists(filepath):
#    if os.path.exists(filepath) == False:
#        print('File {} not found.'.format(filepath))
#        q = input('Would you like to generate it automatically [y or n]?')
#        
#        while True:
#            if q == 'Y' or q == 'y':
#                return make_template()
#            elif q == 'N' or q == 'n':
#                print("Please build {} manually.".format(filepath))
#                print('Exiting...')
#                raise SystemExit
#            else:
#                print('ERROR: "{}" is not an option. Try again.\n')
#    else:
#        return print_template()

def print_file_contents(filepath):
    print('\nReview contents of {}:\n'.format(filepath))
    with open(filepath, 'r') as f:
        for line in f:
            print(line)
    q = input('\nPress any key to continue, or [q] to quit.\n')
    if q == 'Q' or q == 'q':
        sys.exit('Exiting program after reviewing {} file contents.\n'.format(filepath))
    else:
        return None

def make_inp_template(filepath,resname,chrg,mult,templatetype)
    if templatetype == 'opt':
        with open(filepath, 'w') as f:
            f.write("%NProcShared=12\n")
            f.write("%mem=12GB\n")
            f.write("%rwf=/tmp/{}_opt/,-1\n".format(resname))
            f.write("%chk=/tmp/{}_opt/{}_opt.chk\n".format(resname))
            f.write("#T B3LYP/6-311++G(2d,2p) OPT(Tight) SCF(Tight,MaxCycles=1000)\n\n")
            f.write("Gaussian09 geometry optimization at B3LYP/6-311++G(2d,2p)\n\n")
            f.write("{0} {1}\n".format(chrg,mult))
    elif templatetype == 'hf':
        with open(filepath, 'w') as f:
            f.write("%NProcShared=12\n")
            f.write("%mem=12GB\n")
            f.write("%rwf=/tmp/{}_hf/,-1\n".format(resname))
            f.write("%chk=/tmp/{}_hf/{}_hf.chk\n".format(resname))
            f.write("#P HF/6-31g* OPT(Tight) SCF(Tight,MaxCycles=1000)\n\n")
            f.write("Gaussian09 hartree fock geometry optimization at HF/6-31g*\n\n")
            f.write("{0} {1}\n".format(chrg,mult))
    elif templatetype == 'freq':
        with open(filepath, 'w') as f:
            f.write("%NProcShared=12\n")
            f.write("%mem=12GB\n")
            f.write("%rwf=/tmp/{}_freq/,-1\n".format(resname))
            f.write("%chk=/tmp/{}_freq/{}_freq.chk\n".format(resname))
            f.write("#T B3LYP/6-311++G(2d,2p) Freq(HPModes) SCF(Tight,MaxCycles=1000)\n\n")  
            f.write("Gaussian09 harmonic vibrational frequency calculation at B3LYP/6-311++G(2d,2p)\n\n")
            f.write("{0} {1}\n".format(chrg,mult))
    elif templatetype == 'anharm':
        with open(filepath, 'w') as f:
            f.write("%NProcShared=12\n")
            f.write("%mem=12GB\n")
            f.write("%rwf=/tmp/{}_anharm/,-1\n".format(resname))
            f.write("%chk=/tmp/{}_anharm/{}_anharm.chk\n".format(resname))
            f.write("#T B3LYP/6-311++G(2d,2p) Freq(Anharmonic) SCF(Tight,MaxCycles=1000)\n\n")
            f.write("Gaussian09 anharmonic vibrational frequency calculation at B3LYP/6-311++G(2d,2p)\n\n")
            f.write("{0} {1}\n".format(chrg,mult))
    elif templatetype == 'geom':
        with open(filepath, 'w') as f:
            f.write("%NProcShared=12\n")
            f.write("%mem=12GB\n")
            f.write("%rwf=/tmp/{}_geom/,-1\n".format(resname))
            f.write("%chk=/tmp/{}_geom/{}_geom.chk\n".format(resname))
            f.write("#T HF/6-31G* OPT(Tight) SCF(Tight,MaxCycles=1000)\n\n")
            f.write("Gaussian09 geometry optimization at HF/6-31G*\n\n")
            f.write("{0} {1}\n".format(chrg,mult))
    elif templatetype == 'resp':
        with open(filepath, 'w') as f:
            f.write("%NProcShared=12\n")
            f.write("%mem=12GB\n")
            f.write("%rwf=/tmp/{}_resp/,-1\n".format(resname))
            f.write("%chk=/tmp/{}_resp/{}_resp.chk\n".format(resname))
            f.write("#P B3LYP/c-pVTZ SCF(Tight,MaxCycles=1000) Pop=MK IOp(6/33=2,6/41=10,6/42=17)\n\n")
            f.write("Gaussian09 single point electrostatic potential calculation at B3LYP/c-pVTZ\n\n")
            f.write("{0} {1}\n".format(chrg,mult))
    else:
        sys.exit('Error in function make_inp_template() -> "templatetype" argument not recognized.')

def make_inp_file(resname,conf,inptype):
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

    inptypes = ['opt','hf','freq','anharm','geom','resp']
    if inptype not in inptypes:
        sys.exit('Error in function make_inp_file() -> "inptype" argument not recognized.')

    cwd = os.getcwd()

    inp = os.path.join(cwd,'templates/','template_{}.inp'.format(inptype))
    xyz = os.path.join(cwd,'geometries/','{}.xyz'.format(conf))
    out = os.path.join(cwd,'{0}_{1}.inp'.format(conf,inptype))

    if os.path.exists(template) == False:
        sys.exit('Error in function make_inp_file() -> {} not found.'.format(template))
    elif os.path.exists(xyz) == False:
        sys.exit('Error in function make_inp_file() -> {} not found.'.format(xyz))
    else:
        pass

    # Makes the inp file header by copying over the template file contents
    with open(inp, 'r') as header,
         open(out, 'w') as f:
        for line in header:
            f.write(line)

    # Replaces all three letter residues in file with conformer designation
    with open(out, 'r+') as f:
        for line in f:
            if resname in line:
                line.replace(resname,conf)
        
    # Loads the molecular geometry into a list called "coords"
    coords = []
    with open(xyz, 'r') as cartesiancoords:
        for line in cartesiancoords:
            lines = line.split()
            coords.append(lines)

    # Removes the first two header lines of the molecular geometry file
    # (xyz format ONLY) and removes any additional lines containing more
    # or less than just four items, the atom, and its x, y, and z 
    # coordinates
    del coords[0]
    del coords[0]
    for i in range(len(coords)):
        if len(coords[i]) != 4:
            del coords[i]

    # Reopens the "conformer_resp.inp" file and appends the formatted 
    # molecular geometry coordinates to the file
    with open(out, 'a') as f:
        for i in range(0,len(coords)):
            a = format(coords[i][0],'<3s')
            x = format(float(coords[i][1]),'15.5f')
            y = format(float(coords[i][2]),'15.5f')
            z = format(float(coords[i][3]),'15.5f')
            f.write('{}{}{}{}\n'.format(a, x, y, z))
        f.write('\n')
    return None

def write_submission_script(filepath,resname,inptype):
    """ Creates the .pbs submission script for any .inp files.
    Returns None.

    PARAMETERS
    ----------
    filepath : string
        Path + name of the .pbs file written by this function.
    resname : string
        Three letter prefix for the molecule
    inptype : string
        "geom" or "resp" designator for whether this generates a .pbs
        file for a corresponding "_geom.inp" or "_resp.inp" file.

    """
    with open(filepath, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("#SBATCH --partition={} \n".format())
        f.write("#SBATCH --nodes=1\n")
        f.write("#SBATCH --ntasks-per-node=12\n")
        f.write("#SBATCH --export=ALL\n")
        f.write("#SBATCH --time=0-{}:00:00\n".format())
        f.write("#SBATCH --error={0}_opt.err\n\n".format(resname,inptype))
        f.write("test -d /tmp/{0}_{1} || mkdir -v /tmp/{0}_{1}\n\n".format(resname,inptype))
        f.write("module load gaussian\n\n")
        f.write("which g09\n\n")
        f.write("g09 < {0}_{1}.inp > {0}_{1}.out\n\n".format(resname,inptype))
        f.write("cp -pv /tmp/{0}_{1}/{0}_{1}.chk .\n\n".format(resname,inptype))
        f.write("rm -rv /tmp/{0}_{1}\n\n".format(resname,inptype))
    return None


def check_termination(filepath):                                                
    """ Checks gaussian out files for normal termination.
    UNFINISHED
    """
    with open(filepath, 'r') as f:                                              
        for line in f:                                                          
            if 'Normal termination of Gaussian ' in line:                       
                return True                                                     
    print('{} did not terminate correctly!'.format(filepath))                   
    return False 



