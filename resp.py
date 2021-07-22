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



def fortran_format(n):
    """ Formats a string of digits to look like the scientific
    notation in fortran.

    PARAMETERS
    ----------
    n : string
        The number that needs to be converted to fortran's scientific
        notation. Must be convertable to a float type for function to
        work (i.e. string must not contain any letters).

    RETURNS
    -------
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


def write_esp_dat(conf):
    """ This function uses the contents of the "conformer_resp.out" file
    to write the corresponding "conformer_esp.dat" file. Depending on
    the size of the conformer and the size of its resp.out file, this
    function may take a few seconds to run per conformer. Returns None.

    PARAMETERS
    ----------
    conf : string
        The three letter prefix + integer conformer index used to
        identify the different conformers.

    """
    # Make sure the "_resp..out" file exists, and that the "_esp.dat" 
    # file will not be overwritten
    if os.path.isfile(conf + '_resp.out') is not True:
        raise Exception('File {} is missing!'.format(conf + '_resp.out'))
    if os.path.isfile(conf + '_esp.dat') is True:
        raise Exception('File {} already exists!'.format(conf + '_esp.dat'))

    # Retrieves the two ngrid values from the resp.out file (the number
    # of atoms in the molecule, and the number of points involved in
    # the electstatic potential fit). Subtracts the number of atoms from 
    # the number of points, and then appends the number of atoms to the 
    # front of the result. This modified ngrid value is written to the 
    # esp.dat file.
    ngrid = []
    with open(conf + '_resp.out', 'r') as f, \
         open(conf + '_esp.dat', 'a') as esp:
        for line in f:
            if re.search('NGrid ', line):
                lines = line.split()
                ngrid.append(line.split()[2])
        ngrid_esp = ngrid[0] + str(int(ngrid[1]) - int(ngrid[0]))
        spacing = 4 + len(ngrid_esp)
        # Four empty spaces must always lead this number, but this 
        # number is not consistently the same length
        esp.write('{v:>{s}}\n'.format(v=ngrid_esp,s=spacing))

    # Conversion factor from Angstroms to Bohrs
    cnv_factor = 0.529177249

    # Retrieves the "Atomic Centers" from the "_resp.out" file and 
    # writes them to the "_esp.dat" file in fortran scientific notation
    atomic_centers = []
    with open(conf + '_resp.out', 'r') as f, \
         open(conf + '_esp.dat', 'a') as esp:
        for line in f:
            if re.search('Atomic Center ', line):
                atomic_centers.append(line.split()[5:8])
        for i in range(0,len(atomic_centers)):
            x = fortran_format(float(atomic_centers[i][0]) / cnv_factor)
            y = fortran_format(float(atomic_centers[i][1]) / cnv_factor)
            z = fortran_format(float(atomic_centers[i][2]) / cnv_factor)
            esp.write('{:>32}{:>16}{:>16}\n'.format(x, y, z))

    # Writes the "ESP Fit Center" and "Fit" values from the "_resp.out" 
    # file to two temporary files, respectively, after first confirming 
    # that the files don't already exist. Trying to store this much data
    # in memory (i.e. in a list) could be risky.
    try: os.remove('tmp00.txt')
    except: pass
    try: os.remove('tmp01.txt')
    except: pass

    with open(conf + '_resp.out', 'r') as f, \
         open('tmp00.txt', 'w') as b, \
         open('tmp01.txt', 'w') as c:
        for line in f:
            if re.search('ESP Fit', line):
                b.write(line)
            if re.search('Fit    ', line):
                c.write(line)

    # Formats and writes the content of the temporary files to the 
    # "_esp.dat" file. First column is the "Fit" value, followed by the
    # "ESP Fit Center" values in the remaining three columns.
    with open('tmp00.txt', 'r') as b, \
         open('tmp01.txt', 'r') as c, \
         open(conf + '_esp.dat', 'a') as esp:
        for line_b, line_c in zip(b, c):
            esp_fit = line_b.split()
            fit = line_c.split()
            w = fortran_format(float(fit[2]))
            x = fortran_format(float(esp_fit[6]) / cnv_factor)
            y = fortran_format(float(esp_fit[7]) / cnv_factor)
            z = fortran_format(float(esp_fit[8]) / cnv_factor)
            esp.write('{:>16}{:>16}{:>16}{:>16}\n'.format(w, x, y, z))

    # Removes the temporary files from the directory
    os.remove('tmp00.txt')
    os.remove('tmp01.txt')
    return None


def check_convergence(f='punch'):
    """ This function compares the values in the "q0" column of a
    "punch" file to the "qopt" column. When all q0 = qopt, this
    indicates that the resp fitting has converged.

    PARAMETERS
    ----------
    f : string
        Filename (should always just be "punch")

    RETURNS
    -------
    True : if converged
    False : if not converged

    """
    # Check if a punch file exists
    if os.path.isfile(f) is not True:
        raise FileNotFoundError('File {} is missing!\n'.format(f))

    # Open punch file and save lines to memory (isolate items indexed
    # at '2' and '3' where applicable
    punch = []
    with open(f, 'r') as punchfile:
        for line in punchfile:
            punch.append(line.split()[2:4])

    # Delete the first 11 lines and the last 5 lines
    del punch[:11]
    del punch[-6:]

    # Make separate lists for the q0 and qopt values
    q0 = []
    qopt = []
    for q in punch:
        q0.append(q[0])
        qopt.append(q[1])

    # Determine convergence
    if q0 == qopt is True:
        return True
    else:
        return False


def write_resp_in(nconfs,iqopt,ihfree,qwt,f='resp.in'):
    """
    UNFINISHED
    """
    if os.path.isfile(f) is True:
        raise Exception('File {} already exists!\n'.format(f))

    with open(f, 'a') as outfile:
        # Writes the header options
        outfile.write("Resp charges for organic molecule\n\n")
        outfile.write(" &cntrl\n\n")
        outfile.write(" nmol = {},\n".format(nconfs))
        outfile.write(" ihfree = {},\n".format(ihfree))
        outfile.write(" iqopt = {},\n".format(iqopt))
        outfile.write(" qwt = 0.00{},\n\n".format(qwt))
        outfile.write(" &end\n")

        # Writes the first three lines of each molecule table
        for i in range(0,nconf):
            outfile.write("    1.0\n")
            outfile.write("{}".format(conf[i]))
            outfile.write("    charge    numberofatoms")

            # Writes the atom identities and restrictions for each molecule
            for j in range(0,numberofatoms):
                outfile.write("    atomidentity[j]    0")
            outfile.write("\n")

        # Writes the table of conformers and atoms
        conf = 1
        atom = 1
        for i in range(0,natom):
            outfile.write('\n{n:>5d}\n'.format(n=nconf))
            for j in range(0,nconf):
                outfile.write('{n:>5d}{m:>5d}'.format(n=conf,m=atom))
                conf += 1
            conf = 1
            atom += 1


def write_leap_in(resname,f='leap.in'):
    """ Writes the leap.in file from scratch.
    UNFINISHED
    """
    if os.path.isfile(f) is True:
        raise Exception('File {} already exists!\n'.format(f))
    with open(f, 'a') as outfile:
        outfile.write("set default IPOL 1\n\n")
        outfile.write("source leaprc.ff02pol.r1\n\n")
        outfile.write("loadamberparams {}.frcmod\n\n".format(resname))
        outfile.write("x = loadmol2 Temp.mol2\n\n")
        outfile.write("check x\n")
        outfile.write("saveAmberParmPol x prmtop prmcrd\n\n")
        outfile.write("quit")
    return None


def write_sander_in():
    """ Writes the sander.in file from scratch.
    UNFINISHED
    """
    if os.path.isfile(f) is True:
        raise Exception('File {} already exists!\n'.format(f))
    with open(f, 'a') as outfile:
        outfile.write("Title\n")
        outfile.write(" &cntrl\n")
        outfile.write("  irest=0,ntx=1,\n")
        outfile.write("  imin=1,maxcyc=1,\n")
        outfile.write("  ntc=1,ntf=1,\n")
        outfile.write("  cut=999.0,\n")
        outfile.write("  ntpr=100,ntwx=0,ntwv=0,ntwe=0,\n")
        outfile.write("  ipol=1,iesp=1,\n")
        outfile.write("  igb=0,ntb=0,\n")
        outfile.write(" &end\n")
        outfile.write(" &ewald\n")
        outfile.write("  indmeth=1\n")
        outfile.write(" &end")
    return None


def resp_menu():
    """
    UNFINISHED
    """
    def print_resp_menu():
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

    detect_namelist_in()
    namelist = read_namelist_in()
    resname = namelist[0]["resname"]
    chrg = namelist[0]["charge"]
    mult = namelist[0]["multiplicity"]
    nconf = int(namelist[0]["nconf"])

    while True:
        print_resp_menu()
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

