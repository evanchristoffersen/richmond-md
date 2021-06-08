# The script creates the table at the bottom of the resp.in file
# Example of the table
#     3                              . Defines the numbe of atoms being defined on hte next line.    This line is created by the first for loop
#     1    1    2    1    3    1       Alternates between conf_num and atom_num.                     This line is created by the second for loop
#     3
#     1    2    2    2    3    2

# Sets the spacing between numbers
def spacing(var):
    if conformer < 10:
        print('    ' + str(var),end = '')
    elif conformer < 100:
        print('   ' + str(var),end = '')
    else:
        print('  ' + str(var),end = '')

print()
num_conf = int(input('Enter the number of conformers: '))
num_atom = int(input('Enter the number of atoms in the molcule: '))
print()
outloop, inloop, conformer, atom = 1, 1, 1, 1

# Prints a single numer (number of conformers), then moves to the next line
for i in range(num_atom):
    # var = num_conf
    if num_conf < 10:
        print('    ' + str(num_conf))
    elif num_conf < 100:
        print('   ' + str(num_conf))
    elif num_conf < 1000:
        print('  ' + str(num_conf))
    else:
        print('Script cannot handle more thant 999 conformers.')
        print('Exiting script.\n')

# Prints the conformer number and atom number to a single.
    for i in range(num_conf):
        spacing(conformer)
        spacing(atom)

        inloop = inloop + 1
        conformer = conformer + 1
    print()

    conformer, atom = 1, atom + 1
