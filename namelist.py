# Script made with Python 3.9.2
# The script generates namelist.in

# Example of namelist.in:
# Job type (1=rungaussian, 2=get esp.dat, 3=iteration with default atomtypes )
# 3
# nconf
# 4
# natoms
# 9
# charge and multiplicity
# 0 1
# resname
# GLD
#
# GLD1
# GLD2
# GLD3
# GLD4


from pathlib import Path
import os

# Count the number of conf***** files in a directory
dir_path = input('What is the path of the conformers to which you want to RESP fit?  ')
dir = os.listdir(dir_path)

conf_num = 0
for file in dir:
    if file.startswith('conf00'):   # Assumes less than 1000 conformers are in the directory
        conf_num += 1
    else:
        continue


# Read the number of atoms in the molecule from an .xyz file of one of the conformers
file_path = input('What is the path of the .xyz file for one of the conformeres?  ')
xyz_file = open(file_path, 'r')
num_atoms = xyz_file.readline()
xyz_file.close()


# Read charge and multiplicity from .inp file of one of the conformers
inp_path = input('What is the path of one of the .inp file for one of the conformers?  ')
inp_file = open(inp_path, 'r')

c, start_count = 0,0
for line in inp_file:
    if c == 4:                  # Finds the line that contains the charge and multiplicity and exits loop
        charge_mutl = line
        break
    elif start_count == 1:      # This elif is placed here to ensure the line.startswith('#') executes only once
        c = c + 1
    elif line.startswith('#'):  # Finds the line that specifies the calculation that is being done
        c = c + 1
        start_count = 1
    else:
        continue
inp_file.close()


# User defines the name of the residue
res_name = input('What is the name of the residue? ')
while len(res_name) != 3:                                           # Assures residue name is 3 characters long
    res_name = input('What is the name of the residue? ').upper()
    print(res_name)



# Creates namelist.in
namelist_dir = input('Where should namelist.in be saved? Enter the path: ')
namelist_path = os.path.join(namelist_dir, "namelist.in")
namelist = open(namelist_path, 'w')

# Writes the contents of namelist.in
namelist.write('Job type (1=rungaussian, 2=get esp.dat, 3=iteration with default atomtypes ) \n')
namelist.write('3 \n')
namelist.write('nconf \n')
namelist.write(str(conf_num) + '\n')
namelist.write('natoms \n')
namelist.write(str(num_atoms))
namelist.write('charge and multiplicity \n')
namelist.write(str(charge_mutl))
namelist.write('resname \n')
namelist.write(str(res_name) + '\n\n')

for i in range(conf_num):
    namelist.write(str(res_name) + str(i + 1) + '\n')
namelist.close()



"""---------------------------------------------- READ ME ---------------------------------------------- """
""" Potential things that may be good to incorportate """
# * Warning before overwriting an existing namelist.in
# * A fail-safe so the user cannot name the residue as some AMBER has pre-defined (e.g. CYS for cystine)
# * Have this script read the file path from a .txt file or something. That way, the user will not have to enter the file paths each time
#   the script is ran. Instead, the user would insert the file paths into the .txt file, instead.
# * Depending on what step the user is on in the RESP fitting procedure, automatically update the JobType. To do this, I think namelist_auto.py
    # would have to know which script is calling namelist_auto.py or the script that is calling namelist.py would set JobType.

# * Before adding additional functions/fail-safes, check with Konnor. He may have some snippets of code that may help perform these functions.
