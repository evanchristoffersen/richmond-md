#!/usr/bin/env python 

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



def main_menu():
    """
    UNFINISHED
    """
    def print_menu():
        title = "RESP FITTING MENU"
        formatting = int( (78 - len(title)) / 2 ) * "-"
        print(formatting, title, formatting, "\n")
        print("1. Submit error minimization geometry optimizations to Gaussian.")
        print("2. Check geometry optimizations for correct termination.")
        print("3. Submit single point electrostatic potential calculations to Gaussian.")
        print("4. Check electrostatic potential calculations for correct termination.")
        print("5. ")
        print("6. Return to the main menu.\n")
        print(79 * "-", "\n")

    namelistchk = namelist.detectfile()
    if namelistchk == True:
        namelist.writefile()
    elif namelistchk == False:
        print('\nThe file "namelist.in" is needed to proceed.')
        print('Exiting program...')
        raise SystemExit
    else:
        pass

    namelist = namelist.readfile()
    resname = namelist[0]["resname"]
    chrg = namelist[0]["charge"]
    mult = namelist[0]["multiplicity"]
    nconf = int(namelist[0]["nconf"])

    def get_choice():
        """
        """
        while True:
            print_menu()
            choice = input("Enter your choice [1-6]: ")
            print()

            if choice == "1":
                for i in range(nconf):
                    conformer = namelist[1][i]
                    write_submission_script(
                        conformer+"_geom.pbs", conformer, "geom")
                    write_geom_input(
                        conformer+"_geom.inp", resname, conformer, chrg, mult, 4, 8)
                    if os.path.isdir(conformer) is False: os.mkdir(conformer)
                    for f in glob.glob(conformer+'*pbs'): shutil.move(f, conformer)
                    for f in glob.glob(conformer+'*inp'): shutil.move(f, conformer)
                return

            elif choice == "2":

                # for i in range
                # check_termination()
                return

            elif choice == "3":
                for i in range(nconf):
                    conformer = namelist[1][i]
                    write_submission_script(
                        conformer+"_resp.pbs", conformer, "resp")
                    write_resp_input(
                        conformer+"_resp.inp", resname, conformer, chrg, mult, 4, 8)
                    if os.path.isdir(conformer) is False: os.mkdir(conformer)
                    for f in glob.glob(conformer+'*pbs'): shutil.move(f, conformer)
                    for f in glob.glob(conformer+'*inp'): shutil.move(f, conformer)
                return

            elif choice == "4":
                return

            elif choice == "5":
                return

            elif choice == "6":
                return main_menu()
            else:
                input('ERROR: {} is not an option. Try again.\n'.format(choice))

