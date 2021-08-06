#!/usr/bin/env python

"""

"""



import glob # File selection wildcard *
import os # Change directories and prevent file overwrite
import re # Regular expressions (i.e. grep)
import shutil # Move files between directories
import subprocess as sp # Run shell commands
import sys # Error management

from main import find_file_paths,\
                 build_directory_space

__authors__ = "Evan Christoffersen", "Konnor Jones"
# __license__
# __version__


# def choose_paths(paths):
#     
#     print("Multiple paths detected: \n\n")
# 
#     for i,item in enumerate(paths):
#         print(str(i) + ":", paths[i])
# 
# 
# 
#         print(str(len(paths)) + ":", "None of the above.")
# 
# 
# 
# def display_paths(

# 
# def find_template_folder():
#     # Find all possible subdirectories called "templates/"
#     templatepath = find_dirpath("templates")
# 
#     # If more than one "templates/" directory is found allow user to choose
#     if len(templatepath) > 1:
#         print("Multiple directories named templates/ detected:\n")
# 
#         while True:
# 
#             # Print all "templates/" directories
#             for i,item in enumerate(templatepath):
#                 print(str(i) + ":", templatepath[i])
# 
#             # Give user option to exit if desired folder not found
#             print(str(len(templatepath)) + ":", "None of the above.")
# 
#             q = input(f"\nChoose the correct directory [0-{len(templatepath)}]: ")
# 
#             # Handling user input
#             try:
#                 if int(q) < len(templatepath):
#                     templatepath = templatepath[int(q)]
#                     return templatepath
# 
#                 elif int(q) == len(templatepath):
#                     msg = (
# "Reasons your templates/ directory may be missing from this list:\n\n"
# "1. The templates/ directory hasn't been created yet.\n"
# "2. The templates/ directory is not one of the subdirectories in the\n"
# "   directory tree in which this script was run.\n"
# "3. The directory holding your template files is called something other\n"
# "   than 'templates'\n\n"
#                     )
#                     print(msg)
#                     input("\nPress any key to exit.\n")
#                     sys.exit("FileNotFoundError: User exit.")
# 
#                 # If user enters integer not in list
#                 else:
#                     print(f"\n'{q}' is not an option. Try again.\n")
# 
#             # If user enters something other than an integer
#             except ValueError:
#                 print(f"\n'{q}' is not an option. Try again.\n")
# 
#     # If no "templates/" directory is found
#     elif len(templatepath) == 0:
#         sys.exit("FilelNotFoundError: No templates/ folder detected.")
# 
#     else:
#         return templatepath

def match_inp_pbs():
    find_file_paths() # for .inp
    find_file_paths() # for .pbs
    # Check to see if any of the .inp files are missing their .pbs counterparts
    # or vice-versa





def flatten_list(listarg):
    """ Converts a list of lists into a list: 
    [[1, 2, 3], [4, 5, 6]] --> [1, 2, 3, 4, 5, 6]. 
    Note: this function is rudimentary in scope, and should only be 
    expected to work properly if list consists of only sublists that 
    are all the nested the same amount.

    --- PARAMETERS ---
    listarg : list
        The input list of sublists that needs converting.

    --- RETURNS ---
    out : list
        The flattened output list.

    None : NoneType
        Returns None if input is not a list.

    """
    if type(listarg) != list:
        return None

    out = [item for sublist in listarg for item in sublist]
    return out



def remove_whitespace(listarg):
    """ Removes all whitespace from items in a list:
    ['\\t foo \\n bar', '\\t biz \\n baz'] --> ['foobar', 'bizbaz']

    --- PARAMETERS ---
    listarg : list
        The input list containing list items with whitespace

    --- RETURNS ---
    out : list
        The output list with all whitespace removed.

    None : NoneType
        Returns None if input is not a list.

    """
    if type(listarg) != list:
        return None

    out = ["".join(item.split()) for item in listarg]
    return out



def remove_duplicate_items(listarg):
    """ Removes duplicate items from a list: 
    [1, 1, 2, 3] --> [1, 2, 3]

    --- PARAMETERS ---
    listarg : list
        The input list containing duplicate values.

    --- RETURNS ---
    out : list
        The output list containing unique values only.

    None : NoneType
        Returns None if input is not a list.

    """
    if type(listarg) != list:
        return None

    out = list(dict.fromkeys(listarg))
    return out



def remove_empty_items(listarg):
    """ Removes empty items from a list: 
    ['1', '', '2', '3'] --> ['1', '2', '3']

    --- PARAMETERS ---
    listarg : list
        The input list containing empty values.

    --- RETURNS ---
    out : list
        The output list with all empty list values removed.

    None : NoneType
        Returns None if input is not a list.

    """
    if type(listarg) != list:
        return None

    out = [item for item in listarg if "" is not item]
    return out



def convert_item_type(listarg,convert):
    """ Converts list item types between str <--> int <--> float:
    ['1', '2', '3'] <--> [1, 2, 3] <--> [1.0, 2.0, 3.0]

    --- PARAMETERS ---
    listarg : list
        The input list containing items of an undesirable type.

    --- RETURNS ---
    out : list
        The output list containing items of the new type.

    None : NoneType
        Returns None if input is not a list, or if function is unable
        to convert all list items to new type.

    """
    if type(listarg) != list:
        return None

    try:
        if convert == 'str':
            out = [str(item) for item in listarg]
        elif convert == 'int':
            out = [int(item) for item in listarg]
        else:
            out = [float(item) for item in listarg]
        return out

    except ValueError:
        return None


def display_items(datastructure):
    """ Displays all items in a list or dictionary line by line with
    numbers.

    --- PARAMETERS ---
    datastructure : list or dict
        The input datastructure containing items wish to view.

    """
    if type(datastructure) == list:
        for i,item in enumerate(listarg):
            print(str(i+1) + ":", listarg[i])
        return None
    elif type(datastructure) == dict:
        for key, item in datastructure.items():
            print(key + ":", item)
        return None
    else:
        return None



# def display_list_items(listarg):
#     """ Displays all numbered items in a list.
# 
#     --- PARAMETERS ---
#     listarg : list
#         The input list containing items wish to view.
# 
#     """
#     if type(listarg) != list:
#         return None
# 
#     for i,item in enumerate(listarg):
#         print(str(i+1) + ":", listarg[i])
#     return None
# 
# def display_dict_items(dictarg):
#     """ Displays all items in a dictionary.
# 
#     --- PARAMETERS ---
#     dictarg : dictionary
#         The input dictionary containing items wish to view.
# 
#     """
#     if type(dictarg) != dict:
#         return None
# 
#     for key,item in enumerate(dictarg):
#         print(str(i+1) + ":", listarg[i])
#     return None

def get_user_selections():
    """ After displaying a list of numbered options to the user, for
    instance a list of files detected by a script, this function
    prompts the user to select n number of the given options, and
    processes the user input to yield a list containing each number
    explicity listed.

    --- RETURNS ---
    out : list
        List containing each number selection made by the user. List
        items are string type.

    None : NoneType
        Returns None if the user input is invalid.

    """
    msg = (
        "Please make your selection(s) below.\n\n"
        "Note: Entry should contain integers and delimiters only.\n"
        "      Spaces not required.\n\n"
        "Delimiter : comma ',' (Denotes separate entries)\n"
        "Optional  : dash  '-' (Denotes a range of entries)\n\n"
        "Example user input: 1, 3-6, 9\n"
    )
    print(msg)
    rawinput = input("Enter selection here: ")

    # Check if user input is valid
    validinput = re.search(r"^[\s0-9,-]+$",rawinput)
    if not validinput:
        print("Error: User input not valid.\n")
        return None

    # Delimits by commas, removes whitespace, and removes empty items
    processinput = rawinput.split(',')
    processinput = remove_whitespace(processinput)
    processinput = remove_empty_items(processinput)

    # Separate valid ranges from invalid ranges and single selections
    validranges = [
        item for item in processinput if "-" in item
        and item.count('-') == 1
        and not item.startswith('-')
        and not item.endswith('-')
    ]

    # Separate single selections
    selections = [int(item) for item in processinput if "-" not in item]

    # Prepare output list and append single selections to it
    out = []
    out.append(selections)

    # Process valid ranges if detected
    if len(validranges) > 0:
        # Sublist(s) in "parsed" contain start and end of each range
        parsed = []
        for i in range(len(validranges)):
            parsed.append(validranges[i].split("-"))

        # Sublist(s) in interpolated contain each value in a range 
        # explcitly listed
        interpolated = []
        for i in range(len(parsed)):
            startindex = int(parsed[i][0])
            endindex = int(parsed[i][1]) + 1
            interpolated.append(list(range(startindex,endindex)))

        # Flatten and append ranges to the output list
        ranges = flatten_list(interpolated)
        out.append(ranges)

    # Clean up output list
    out = flatten_list(out)
    out.sort()
    out = remove_duplicate_items(out)
    out = convert_item_type(out,'int')
    return out



def make_inp_template(savepath,calculation):
    """ Writes the template_{}.inp file. Best practice: write 
    template_{}.inp to a directory called "templates/". Returns None.

    --- PARAMETERS ---
    savepath : string
        Path to the relevant template_{}.inp file

    calculation : string
        One of six key strings designating the type of .inp file
        Acceptable options:
        opt     - [DFT] geometry optimization
        hf      - [DFT] geometry optimization (error minimization)
        freq    - [DFT] gas phase vibrational mode calculation
        anharm  - [DFT] gas phase vibrational anharmonics calculation
        geom    - [MD]  geometry optimization (error minimization)
        resp    - [MD]  electrostatic potential single point calculation

    """
    validcalculation = True

    if calculation == "opt":
        contents = (
            "#P B3LYP/6-311++G(2d,2p) opt(tight,MaxCycles=1000) scf(tight,MaxCycles=1000)\n\n"
            "Gaussian09 geometry optimization at B3LYP/6-311++G(2d,2p)\n\n"
        )

    elif calculation == "hf":
        contents = (
            "#P HF/6-31G* opt(tight,MaxCycles=1000) scf(tight,MaxCycles=1000)\n\n"
            "Gaussian09 geometry optimization at HF/6-31G*\n\n"
        )

    elif calculation == "freq":
        contents = (
            "#P B3LYP/6-311++G(2d,2p) Freq(HPModes) scf(tight,MaxCycles=1000)\n\n"
            "Gaussian09 harmonic vibrational frequency calculation at B3LYP/6-311++G(2d,2p)\n\n"
        )

    elif calculation == "anharm":
        contents = (
            "#P B3LYP/6-311++G(2d,2p) Freq(Anharmonic) scf(tight,MaxCycles=1000)\n\n"
            "Gaussian09 anharmonic vibrational frequency calculation at B3LYP/6-311++G(2d,2p)\n\n"
        )

    elif calculation == "geom":
        contents = (
            "#P HF/6-31G* opt(tight,MaxCycles=1000) scf(tight,MaxCycles=1000)\n\n"
            "Gaussian09 geometry optimization at HF/6-31G*\n\n"
        )

    elif calculation == "resp":
        contents = (
            "#P B3LYP/c-pVTZ scf(tight,MaxCycles=1000) Pop=MK IOp(6/33=2,6/41=10,6/42=17)\n\n"
            "Gaussian09 single point electrostatic potential calculation at B3LYP/c-pVTZ\n\n"
        )

    else:
        validcalculation = False
        contents = (
            "#P [functional]/[basisset] [calculation type]\n\n"
            "Gaussian09 [calculation type] at [functional]/[basisset]\n\n"
        )

    try:
        with open(savepath, "w") as f:
            f.write("%NProcShared=14\n")
            f.write("%mem=12GB\n")

            if validcalculation == False:
                f.write(f"%rwf=/tmp/[molecule]_[calculation type]/,-1\n")
                f.write(f"%chk=/tmp/[molecule]_[calculation type]/[molecule]_[calculation type].chk\n\n")

            else:
                f"%rwf=/tmp/[molecule]_{calculation}/,-1\n"
                f"%chk=/tmp/[molecule]_{calculation}/[molecule]_{calculation}.chk\n\n"

            f.write(contents)
            f.write("0 1\n")

    except FileNotFoundError:
        msg = (
            f"\nFileNotFoundError: Unable to complete path to {savepath}\n"
            f"Aborting {savepath} file creation.\n"
        )
        print(msg)

    finally:
        return None



def make_pbs_template(savepath,calculation):
    """ Writes the template_{}.pbs file. Best practice: write
    template_{}.pbs to a directory called "templates/".
    
    --- PARAMETERS ---
    savepath : string
        Path to the relevant template_{}.pbs file
    
    calculation : string
        One of six key strings designating the type of .inp file
        Recognized options:
        opt     - [DFT] geometry optimization
        hf      - [DFT] geometry optimization (error minimization)
        freq    - [DFT] gas phase vibrational mode calculation
        anharm  - [DFT] gas phase vibrational anharmonics calculation
        geom    - [MD]  geometry optimization (error minimization)
        resp    - [MD]  electrostatic potential single point calculation

    --- RETURNS ---
    None : NoneType

    """
    if calculation == "anharm":
        partition = "long"
        ntasks = "28"
        walltime = "14-00:00:00"

    elif calculation in ['opt','hf','freq','geom','resp']:
        partition = "short"
        ntasks = "14"
        walltime = "1-00:00:00"

    else:
        calculation = '[calculation type]'
        partition = '[partition type]'
        ntasks = '0'
        walltime = '0-00:00:00'

    contents = (
         "#!/bin/bash\n\n"
         "#SBATCH --account=richmond:\n"
        f"#SBATCH --partition={partition}\n"
         "#SBATCH --nodes=1 ### 14 cores per CPU, 2 CPU per node\n"
        f"#SBATCH --ntasks-per-node={ntasks} ### Number of MPI processes\n"
        f"#SBATCH --time={walltime}\n"
         "#SBATCH --export=ALL\n"
        f"#SBATCH --error=[molecule]_{calculation}.err\n\n"
        f"test -d /tmp/[molecule]_{calculation} || mkdir -v /tmp/[molecule]_{calculation}\n\n"
         "module load intel-mpi\n"
         "module load mkl\n"
         "module load gaussian\n\n"
         "which g09\n\n"
        f"g09 < [molecule]_{calculation}.inp > [molecule]_{calculation}.out\n\n"
        f"cp -pv /tmp/[molecule]_{calculation}/[molecule]_{calculation}.chk .\n\n"
        f"rm -rv /tmp/[molecule]_{calculation}\n\n"
    )

    try:
        with open(savepath, "w") as f:
            f.write(contents)

    except FileNotFoundError:
        msg = (
            f"\nFileNotFoundError: Unable to complete path to {savepath}\n"
            f"Aborting [molecule]_{calculation}.pbs file creation.\n"
        )
        print(msg)

    finally:
        return None



def get_coords_from_xyz(xyzpath):
    """ Loads atom identities and coordinates from files ending in .xyz
    into a list.

    --- PARAMETERS ---
    xyzpath : string
        Path to the relevant .xyz file

    --- RETURNS ---
    coords : list
        List of sublists, where each list item is a line from the .xyz
        file, and each sublist (line) has four items:
        1. atomic identity
        2. x coordinate
        3. y coordinate
        4. z coordinate

    None : NoneType
        Returns this if unsuccessful in accessing .xyz file

    """
    coords = []
    try:
        with open(xyzpath, "r") as xyz:
            for line in xyz:
                lines = line.split()
                coords.append(lines)

    except FileNotFoundError:
        msg = (
        f"\nFileNotFoundError: Cannot open {xyzpath}\n"
        "Cannot retrieve molecular coordinates.\n"
        )
        print(msg)
        return None

    else:
        # Removes the first two header lines of the xyz file 
        del coords[0]
        del coords[0]

        # Removes any lines without exactly four items (atom, x, y, z)
        for i in range(len(coords)):
            if len(coords[i]) != 4:
                del coords[i]

    finally:
        return coords



def make_file(templatepath, savepath, conf, inp, xyzpath):
    """ Creates the .inp file, using the information from a
    template_{}.inp file, and the molecular coordinates from a .xyz
    file. Returns None.

    --- PARAMETERS ---
    templatepath : string
        Path to the relevant template_{}.inp file

    savepath : string
        Full path to save new .inp file

    conf : string
        Three letter residue prefix + integer (conformer index number)

    inp : boolean
        True --> if building a .inp file
        False --> if building a .pbs file

    xyzpath : string
        Path to the relevant .xyz file containing the molecular 
        coordinates for the molecule

    """
    lines = []

    try:
        # Loads template file into memory - writing conformer
        # designation in where necessary.
        with open(templatepath, "r") as template:
            for line in template:
                if "[molecule]" in line:
                    line = line.replace("[molecule]", conf)
                lines.append(line)

    except FileNotFoundError:
        msg = (
            f"\nFileNotFoundError: Cannot open {templatepath}\n\n"
            f"Aborting creation of {savepath}\n"
        )
        print(msg)
        return None

    try:
        # Writes template file lines from memory into file
        with open(savepath, "w") as f:
            for line in lines:
                f.write(line)

    except FileNotFoundError:
        msg = (
            f"\nFileNotFoundError: Cannot open {savepath}\n\n"
            f"Aborting creation of {savepath}\n"
        )
        print(msg)
        return None

    # Do if .inp file - ignore if .pbs file
    if inp:
        coords = get_coords_from_xyz(xyzpath)

        if coords == None:
            print(f"Aborting creation of {savepath}\n")
            os.remove(savepath)
            return None

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



def check_gaussian_termination(filepath):
    """ Checks gaussian out files for normal termination.
    
    --- PARAMETERS ---
    filepath : string
        Path to the gaussian .out file

    --- RETURNS ---
    True : Boolean
        If file terminated normally

    False : Boolean
        If file did not terminate normally

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


def removekeys(d, keys):
    copy = dict(d)
    for item in keys:
        del copy[item]
    return copy

def keepkeys(d, keys):
    copy = dict(d)
    out = {key:copy[key] for key in keys if key in copy}
    return out 

def main_menu():
    """

    """
    def print_menu():

        title = "GAUSSIAN MENU"
        formatting = int((78 - len(title)) / 2) * '-'
        print(formatting, title, formatting, '\n')

        menu = (
"0. Documentation/Help\n"
"1. Build template Gaussian input files (.inp).\n"
"2. Build template Gubmission scripts (.pbs).\n"
"3. Write batch of Gaussian input files for molecule of interest.\n"
"4. Write batch of submission scripts for Gaussian input files.\n"
"5. Submit jobs to Gaussian.\n"
"6. Check Gaussian output (.out) files for normal termination.\n"
"7. Pull molecular coordinates from Gaussian output files.\n"
"8. Pull ___ from Gaussian output files.\n"
"#. Exit the program.\n"
        )

        print(menu)
        print(79 * '-', '\n')
        return None

    while True:
        print_menu()
        choice = input('Enter your choice [1-4]: ')
        print()

        if choice == '0':
            print('Under construction')
            generate_conformers()
            approximate_lowest_energy_conformers()
            rename_conformers()

        elif choice == '1':
            geometryfiles = find_file_paths(".xyz")
            geometryfiles = {key : item for key, item in enumerate(geometryfiles)}

            msg = (
            f"{len(geometryfiles)} geometry files were detected:\n"
            "(Press any key to view detected files...)\n\n"
            )
            input(msg)

            display_items(geometryfiles)


            q = input("\nEdit list? Enter [y or n]: ")

            if q == 'y':
                loop = True
                while loop:
                    msg = (
                        "\nSelect files of interest.\n"
                    )
                    print(msg)

                    selectedfiles =  get_user_selections()

                    innerloop = True
                    while innerloop:
                        q = input('Keep or remove? Enter [keep or remove]: ')
                        if q == 'keep':
                            bar = keepkeys(bar, selectedfiles)

                        elif q == 'remove':
                            bar = removekeys(bar, selectedfiles)

                        else:
                            print("Not an option.")

                    msg = (
                        "\nThe following files were removed: \n"
                        "(Press any key to continue...)\n\n"
                    )
                    input(msg)
                    print(bar)

                    msg = (
                        "\nThe following files were kept: \n"
                        "(Press any key to continue...)\n\n"
                    )
                    input(msg)
                    print(bar)

            #make_inp_template(savepath, calculation)

        elif choice == '2':
            make_pbs_template(savepath, calculation)

        elif choice == '3':
            make_file(templatepath, savepath, conf, True, xyzpath)

        elif choice == '4':
            make_file(templatepath, savepath, conf, False, xyzpath)

        elif choice == '5':
            print('Under construction')
            submit_jobs()

        elif choice == '6':
            check_gaussian_termination(filepath)

        elif choice == '7':
            make_xyz(gaussianpath,outputpath)

        elif choice == '8':
            print('Under construction')
            pass

        elif choice == '9':
            print('Under construction')
            pass

        elif choice == '#':
            sys.exit('Program halted by user.\n')

        else:
            input('"{}" is not an option. Try again.\n'.format(choice))
    return None


def main():
    # build_directory_space()
    main_menu()

if __name__ == "__main__":
    main()
#    foo = get_user_selections()
#    print(foo)
#    make_inp_template("opt")
