#!/usr/bin/env python

"""

"""



import glob # File selection wildcard *
import os # Change directories and prevent file overwrite
import re # Regular expressions (i.e. grep)
import shutil # Move files between directories
import subprocess as sp # Run shell commands
import sys # Error management

# from main import find_dirpath, build_directory_space

__authors__ = "Evan Christoffersen", "Konnor Jones"
# __license__
# __version__





# def find_template_folder():
#     # Find all possible subdirectories called "templates/"
#     templatepath = find_dirpath("templates")
# 
#     # If more than one "templates/" directory is found allow user to choose
#     if len(templatepath) > 1:
#         print("Multiple "templates/" folders detected:\n")
# 
#         while True:
#             # Print all "templates/" directories
#             for i,item in enumerate(templatepath):
#                 print(str(i) + ":", templatepath[i])
#             # Give user option to exit if desired folder not found
#             print(str(len(templatepath)) + ":", "None of the above.")
#             q = input(
#                 "\nChoose the correct "templates/" folder [0-{}]: ".format(
#                 len(templatepath)))
# 
#             # Handling user input
#             try:
#                 if int(q) < len(templatepath):
#                     templatepath = templatepath[int(q)]
#                     return templatepath
#                 elif int(q) == len(templatepath):
#                     print("\nDouble check:\n")
#                     print("1. Script must be run above the "templates/" folder in the directory tree.")
#                     print("2. The name of the folder must match the string "templates".")
#                     input("\nPress any key to exit.\n")
#                     sys.exit("Exiting program to allow user to correct missing "templates/" error.")
#                 # If user enters integer not in list
#                 else:
#                     print("\n"{}" is not an option. Try again.\n".format(q))        
#             # If user enters something other than an integer
#             except ValueError:
#                 print("\n"{}" is not an option. Try again.\n".format(q))        
# 
#     # If no "templates/" directory is found
#     elif len(templatepath) == 0:
#         sys.exit("No templates/ folder detected.")
#     else:
#         return templatepath

def make_inp_template(filepath,templatetype):
    """ Writes the template_{}.inp file. Best practice: write 
    template_{}.inp to a directory called "templates/". Returns None.

    --- PARAMETERS ---
    filepath : string
        Path to the relevant template_{}.inp file

    templatetype : string
        One of six key strings designating the type of .inp file
        Acceptable options:
        opt     - [DFT] geometry optimization
        hf      - [DFT] geometry optimization (error minimization)
        freq    - [DFT] gas phase vibrational mode calculation
        anharm  - [DFT] gas phase vibrational anharmonics calculation
        geom    - [MD]  geometry optimization (error minimization)
        resp    - [MD]  electrostatic potential single point calculation

    """
    if templatetype == "opt":
        contents = (
            "#P B3LYP/6-311++G(2d,2p) opt(tight,MaxCycles=1000) scf(tight,MaxCycles=1000)\n\n"
            "Gaussian09 geometry optimization at B3LYP/6-311++G(2d,2p)\n\n"
        )
    elif templatetype == "hf":
        contents = (
            "#P HF/6-31G* opt(tight,MaxCycles=1000) scf(tight,MaxCycles=1000)\n\n"
            "Gaussian09 geometry optimization at HF/6-31G*\n\n"
        )
    elif templatetype == "freq":
        contents = (
            "#P B3LYP/6-311++G(2d,2p) Freq(HPModes) scf(tight,MaxCycles=1000)\n\n"
            "Gaussian09 harmonic vibrational frequency calculation at B3LYP/6-311++G(2d,2p)\n\n"
        )
    elif templatetype == "anharm":
        contents = (
            "#P B3LYP/6-311++G(2d,2p) Freq(Anharmonic) scf(tight,MaxCycles=1000)\n\n"
            "Gaussian09 anharmonic vibrational frequency calculation at B3LYP/6-311++G(2d,2p)\n\n"
        )
    elif templatetype == "geom":
        contents = (
            "#P HF/6-31G* opt(tight,MaxCycles=1000) scf(tight,MaxCycles=1000)\n\n"
            "Gaussian09 geometry optimization at HF/6-31G*\n\n"
        )
    elif templatetype == "resp":
        contents = (
            "#P B3LYP/c-pVTZ scf(tight,MaxCycles=1000) Pop=MK IOp(6/33=2,6/41=10,6/42=17)\n\n"
            "Gaussian09 single point electrostatic potential calculation at B3LYP/c-pVTZ\n\n"
        )
    else:
        contents = (
            "#P [functional]/[basisset] [calculation type]\n\n"
            "Gaussian09 [calculation type] at [functional]/[basisset]\n\n"
        )

    try:
        with open(filepath, "w") as f:
            f.write("%NProcShared=14\n")
            f.write("%mem=12GB\n")
            f.write(f"%rwf=/tmp/template_{templatetype}/,-1\n")
            f.write(f"%chk=/tmp/template_{templatetype}/template_{templatetype}.chk\n\n")
            f.write(contents)
            f.write("0 1\n")
        return None

    except FileNotFoundError:
        msg = (
            f"\nFileNotFoundError: Unable to complete path to {filepath}\n"
            f"Aborting template_{templatetype}.inp file creation.\n"
        )
        print(msg)
        return None



def make_pbs_template(filepath,templatetype):
    """ Writes the template_{}.pbs file. Best practice: write
    template_{}.pbs to a directory called "templates/". Returns None.
    
    --- PARAMETERS ---
    filepath : string
        Path to the relevant template_{}.pbs file
    
    templatetype : string
        One of six key strings designating the type of .inp file
        Recognized options:
        opt     - [DFT] geometry optimization
        hf      - [DFT] geometry optimization (error minimization)
        freq    - [DFT] gas phase vibrational mode calculation
        anharm  - [DFT] gas phase vibrational anharmonics calculation
        geom    - [MD]  geometry optimization (error minimization)
        resp    - [MD]  electrostatic potential single point calculation

    """
    if templatetype == "anharm":
        partition = "long"
        ntasks = "28"
        walltime = "14"
    else:
        partition = "short"
        ntasks = "14"
        walltime = "1"

    contents = (
         "#!/bin/bash\n\n"
         "#SBATCH --account=richmond:\n"
        f"#SBATCH --partition={partition}\n"
         "#SBATCH --nodes=1 ### 14 cores per CPU, 2 CPU per node\n"
        f"#SBATCH --ntasks-per-node={ntasks} ### Number of MPI processes\n"
        f"#SBATCH --time={walltime}-00:00:00\n"
         "#SBATCH --export=ALL\n"
        f"#SBATCH --error=template_{templatetype}.err\n\n"
        f"test -d /tmp/template_{templatetype} || mkdir -v /tmp/template_{templatetype}\n\n"
         "module load intel-mpi\n"
         "module load mkl\n"
         "module load gaussian\n\n"
         "which g09\n\n"
        f"g09 < template_{templatetype}.inp > template_{templatetype}.out\n\n"
        f"cp -pv /tmp/template_{templatetype}/template_{templatetype}.chk .\n\n"
        f"rm -rv /tmp/template_{templatetype}\n\n"
    )

    try:
        with open(filepath, "w") as f:
            f.write(contents)
        return None

    except FileNotFoundError:
        msg = (
            f"\nFileNotFoundError: Unable to complete path to {filepath}\n"
            f"Aborting template_{templatetype}.pbs file creation.\n"
        )
        print(msg)
        return None


def custom_FNFerror():
    msg = (

    )
    print(msg)
    return None


def make_inp_file(templatepath, xyzpath, savepath, conf, inptype):
    """ Creates the .inp file, using the information from a
    template_{}.inp file, and the molecular coordinates from a .xyz
    file. Returns None.

    --- PARAMETERS ---
    templatepath : string
        Path to the relevant template_{}.inp file

    xyzpath : string
        Path to the relevant .xyz file containing the molecular 
        coordinates for the molecule

    savepath : string
        Full path to save new .inp file

    conf : string
        Three letter residue prefix + integer (conformer index number)

    filetype : string
        One of six key strings designating the type of .inp file
        Recognizable options:
        opt     - [DFT] geometry optimization
        hf      - [DFT] geometry optimization (error minimization)
        freq    - [DFT] gas phase vibrational mode calculation
        anharm  - [DFT] gas phase vibrational anharmonics calculation
        geom    - [MD]  geometry optimization (error minimization)
        resp    - [MD]  electrostatic potential single point calculation

    """
    # Copies information from template file to actual .inp file
    try:
        with open(templatepath, "r") as template,\
             open(savepath, "w") as f:
            for line in template:
                f.write(line)

    except FileNotFoundError:
        msg = (
            f"\nFileNotFoundError: Cannot open {templatepath}\n"
            f"Aborting {savepath} file creation...\n"
        )
        print(msg)
        return None

    # Replaces place holders from template with conformer designations 
    # NOTE: Not working yet - need to split line by everything and anything
    # except for alphanumeric characters
    with open(savepath, "r+") as f:
        for line in f:
            if "template" in line:
                line.replace("template",conf)

    # Loads the molecular geometry into a list called "coords"
    try:
        coords = []
        with open(xyzpath, "r") as cartesiancoords:
            for line in cartesiancoords:
                lines = line.split()
                coords.append(lines)

    except FileNotFoundError:
        msg = (
            f"\nFileNotFoundError: Cannot open {xyzpath}\n"
            f"Aborting {savepath} file creation...\n"
        )
        print(msg)
        os.remove(out)
        return None

    # Removes the first two header lines of the xyz file 
    del coords[0]
    del coords[0]

    # Removes any lines without exactly four items (atom, x, y, z coords)
    for i in range(len(coords)):
        if len(coords[i]) != 4:
            del coords[i]

    # Appends the formatted molecular coordinates to the .inp file
    with open(savepath, "a") as f:
        for i in range(0,len(coords)):
            a = format(coords[i][0],"<3s")
            x = format(float(coords[i][1]),"15.5f")
            y = format(float(coords[i][2]),"15.5f")
            z = format(float(coords[i][3]),"15.5f")
            f.write(f"{a}{x}{y}{z}\n")
        f.write("\n\n")
    return None



def make_pbs_file(templatepath,savepath,conf,filetype):
    """ Creates the .pbs submission script for any .inp files.
    Returns None.

    --- PARAMETERS ---
    templatepath : string
        Path to the relevant template_{}.pbs file

    savepath : string
        Full path to save new .inp file

    conf : string
        Three letter residue prefix + integer (conformer index number)

    filetype : string
        One of six key strings designating the type of .pbs file
        Recognizable options:
        opt     - [DFT] geometry optimization
        hf      - [DFT] geometry optimization (error minimization)
        freq    - [DFT] gas phase vibrational mode calculation
        anharm  - [DFT] gas phase vibrational anharmonics calculation
        geom    - [MD]  geometry optimization (error minimization)
        resp    - [MD]  electrostatic potential single point calculation

    """
    # Writes template contents to save file
    try:
        with open(templatepath, "r") as template,\
             open(savepath, "w") as f:
            for line in template:
                f.write(line)

    except FileNotFoundError:
        msg = (
            f"\nFileNotFoundError: Cannot open {templatepath}\n"
            f"Aborting {savepath} file creation...\n"
        )
        print(msg)
        return None

    # If no exception thrown, all instances of string "template" are
    # replaces with conformer designation in save file
    else:
        with open(savepath, "r+") as f:
            for line in f:
                if "template" in line:
                    line.replace("template",conf)
        return None



def check_gaussian_termination(filepath):
    """ Checks gaussian out files for normal termination.
    
    --- PARAMETERS ---
    filepath : string
        Path to the gaussian .out file

    --- RETURNS ---
    True -> if file terminated normally
    False -> if file did not terminate normally

    """
    # If file contains the string "Normal termination of Gaussian"
    # the function returns True
    try:
        with open(filepath, "r") as f:
            for line in f:
                if "Normal termination of Gaussian " in line:
                    return True

    except FileNotFoundError:
        print(f"FileNotFoundError: Unable to check {filepath} for termination.\n")
        return False

    # If function doesn't exit on True before reading the last line, it
    # is assumed normal termination was not achieved and returns False
    else:
        print(f"{filepath} did not terminate correctly!\n")
        return False



def make_xyz(gaussianpath,outputpath):
    """

    """
    # Find converged geometry in gaussian09 out file
    try:
        i = 0
        firstline = 0
        lastline = 0
        with open(gaussianpath, "r") as f:
            for i,line in enumerate(f):
                if "Standard orientation:" in line:
                    firstline = max(i, firstline)
                if "Rotational constants " in line:
                    lastline = max(i, lastline)
    except FileNotFoundError:
        print("FileNotFoundError: Unable to open file {}.\n".format(path))
        return None

    atomicnumber = { 
        1   : 'H' , 2   : 'He', 3   : 'Li', 4   : 'Be', 5   : 'B' , 6   : 'C' , 
        7   : 'N' , 8   : 'O' , 9   : 'F' , 10  : 'Ne', 11  : 'Na', 12  : 'Mg', 
        13  : 'Al', 14  : 'Si', 15  : 'P' , 16  : 'S' , 17  : 'Cl', 18  : 'Ar', 
        19  : 'K' , 20  : 'Ca', 21  : 'Sc', 22  : 'Ti', 23  : 'V' , 24  : 'Cr', 
        25  : 'Mn', 26  : 'Fe', 27  : 'Co', 28  : 'Ni', 29  : 'Cu', 30  : 'Zn', 
        31  : 'Ga', 32  : 'Ge', 33  : 'As', 34  : 'Se', 35  : 'Br', 36  : 'Kr', 
        37  : 'Rb', 38  : 'Sr', 39  : 'Y' , 40  : 'Zr', 41  : 'Nb', 42  : 'Mo', 
        43  : 'Tc', 44  : 'Ru', 45  : 'Rh', 46  : 'Pd', 47  : 'Ag', 48  : 'Cd',
        49  : 'In', 50  : 'Sn', 51  : 'Sb', 52  : 'Te', 53  : 'I' , 54  : 'Xe',
        55  : 'Cs', 56  : 'Ba', 57  : 'La', 58  : 'Ce', 59  : 'Pr', 60  : 'Nd',
        61  : 'Pm', 62  : 'Sm', 63  : 'Eu', 64  : 'Gd', 65  : 'Tb', 66  : 'Dy',
        67  : 'Ho', 68  : 'Er', 69  : 'Tm', 70  : 'Yb', 71  : 'Lu', 72  : 'Hf',
        73  : 'Ta', 74  : 'W' , 75  : 'Re', 76  : 'Os', 77  : 'Ir', 78  : 'Pt', 
        79  : 'Au', 80  : 'Hg', 81  : 'Tl', 82  : 'Pb', 83  : 'Bi', 84  : 'Po', 
        85  : 'At', 86  : 'Rn', 87  : 'Fr', 88  : 'Ra', 89  : 'Ac', 90  : 'Th', 
        91  : 'Pa', 92  : 'U' , 93  : 'Np', 94  : 'Pu', 95  : 'Am', 96  : 'Cm', 
        97  : 'Bk', 98  : 'Cf', 99  : 'Es', 100 : 'Fm', 101 : 'Md', 102 : 'No', 
        103 : 'Lr', 104 : 'Rf', 105 : 'Db', 106 : 'Sg', 107 : 'Bh', 108 : 'Hs', 
        109 : 'Mt', 110 : 'Ds', 111 : 'Rg', 112 : 'Cn', 113 : 'Nh', 114 : 'Fl', 
        115 : 'Mc', 116 : 'Lv', 117 : 'Ts', 118 : 'Og'}

    coords = []

    # Open gaussian09 out file and copy converged coordinates to the
    # coords = [] array
    with open(gaussianpath, "r") as f:
        for i,line in enumerate(f):
            if i >= firstline+5 and i <= lastline-2:
                coords.append(line.split())

    # Format coords = [] array to contain only atomic numbers and x, y, 
    # and z coordinates
    for i in range(len(coords)):
        del coords[i][2]
        del coords[i][0]
        try:
            coords[i][0] = atomicnumber[int(coords[i][0])]
        except KeyError:
           # print("KeyError: Atom identity unknown for atomic number "{}".\n".format(coords[i][0]))
            return None

    # Write .xyz file
    try:
        with open(outputpath, "w") as f:
            f.write(str(len(coords))+"\n")
            f.write("comment line\n")
            for item in coords:
                f.write("{:<}{:>16}{:>14}{:>14}\n".format(item[0],item[1],item[2],item[3]))
    except FileNotFoundError:
        print("FileNotFoundError: Unable to save {} to directory {}.\n".format())
        return None

    return None

# if __name__ == "__main__":
#     make_inp_template("opt")
