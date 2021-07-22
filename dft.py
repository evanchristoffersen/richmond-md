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



def write_geom_input(f,resname,conf,chrg,mult,nodes,mem):
    """ Creates the "conformer_geom.inp" file, using the information
    loaded from the "namelist.in" file. Loads molecular coordinates from
    the .xyz file format (REQUIRED). Returns None.

    PARAMETERS
    ----------
    f : string
        Filename (the .inp file written by this function)
    resname : string
        Three letter residue prefix
    conf : string
        Three letter residue prefix + integer (conformer index number)
    chrg : integer
        Molecular charge
    mult : integer
        Molecular multiplicity
    nodes : integer
        The NProcShared for the geometry optimization
    mem : integer
        The memory dedicated to the geometry optimization

    """
    # Check if file exists (prevents overwrite)
    if os.path.isfile(f) is True:
        raise Exception('File {} already exists!\n'.format(f))

    # Writes a new file (the "conformer_geom.inp" file) and appends to 
    # it all of the header information needed for the calculation
    coords = os.path.join(cwd,conformer + '.xyz')
    with open(f, 'a') as outfile, open(coords, 'r') as xyz:
        outfile.write("%NProcShared={}\n".format(nodes))
        outfile.write("%mem={}GB\n".format(mem))
        outfile.write("%rwf=/tmp/{0}_opt/,-1\n".format(conf))
        outfile.write("%chk=/tmp/{1}_opt/{1}_opt.chk\n".format(resname,conf))
        outfile.write("#T B3LYP/6-311++G(2d,2p) OPT(Tight) scf(tight)\n\n")
        outfile.write(" Gaussian09 opt calc of conf00000 using B3LYP/6-311++G(2d,2p)\n\n")
        outfile.write("{0} {1}\n".format(chrg,mult))

    # Loads the molecular geometry into a list called "coords"
    coords = []
    xyz = os.path.join(cwd,conformer + '.xyz')
    with open(xyz, 'r') as coordinatefile:
        for line in coordinatefile:
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
    with open(f, 'a') as outfile:
        for i in range(0,len(coords)):
            a = format(coords[i][0],'<3s')
            x = format(float(coords[i][1]),'15.5f')
            y = format(float(coords[i][2]),'15.5f')
            z = format(float(coords[i][3]),'15.5f')
            outfile.write('{}{}{}{}'.format(a, x, y, z))
            outfile.write('\n')
        outfile.write('\n')
    return None


def write_resp_input(f,resname,conf,chrg,mult,nodes,mem):
    """ Creates the "conformer_resp.inp" file, using the information
    loaded from the "namelist.in" file. Loads molecular coordinates from
    the .xyz file format (xyz is REQUIRED format). Returns None.

    PARAMETERS
    ----------
    f : string
        Filename (the .inp file written by this function)
    resname : string
        Three letter residue prefix
    conf : string
        Three letter residue prefix + integer (conformer index number)
    chrg : integer
        Molecular charge
    mult : integer
        Molecular multiplicity
    nodes : integer
        The NProcShared for the geometry optimization
    mem : integer
        The memory dedicated to the geometry optimization

    """
    # Check if file exists (prevents overwrite)
    if os.path.isfile(f) is True:
        raise Exception('File {} already exists!\n'.format(f))

    # Writes a new file (the "conformer_resp.inp" file) and appends to 
    # it all of the header information needed for the calculation
    with open(f, 'a') as outfile:
        outfile.write("%NProcShared=12\n")
        outfile.write("%mem=12GB\n")
        outfile.write("%chk=/tmp/{0}/{1}_resp.chk\n".format(resname,conf))
        outfile.write("#P B3LYP/c-pVTZ scf(tight,MaxCycles=1000) Pop=MK IOp(6/33=2,6/41=10,6/42=17)\n\n")
        outfile.write("Gaussian09 single point electrostatic potential calculation at B3LYP/c-pVTZ\n\n")
        outfile.write("{0} {1}\n".format(chrg,mult))

    # Loads the molecular geometry into a list called "coords"
    coords = []
    xyz = os.path.join(cwd,conformer + '.xyz')
    with open(xyz, 'r') as coordinatefile:
        for line in coordinatefile:
            lines = line.split()
            coords.append(lines)

    # Removes the first two header lines of the molecular geometry file 
    # (xyz format ONLY) and removes any additional lines containing more
    # or less than just four items, the atom, and its x, y, and z 
    # coordinates
    del coords[0]
    del coords[0]
    for i in range(0,len(coords)):
        if len(coords[i]) != 4:
            del coords[i]

    # Reopens the "conformer_resp.inp" file and appends the formatted 
    # molecular geometry coordinates to the file
    with open(f, 'a') as outfile:
        for i in range(0,len(coords)):
            a = format(coords[i][0],'<3s')
            x = format(float(coords[i][1]),'15.5f')
            y = format(float(coords[i][2]),'15.5f')
            z = format(float(coords[i][3]),'15.5f')
            outfile.write('{}{}{}{}'.format(a, x, y, z))
            outfile.write('\n')
        outfile.write('\n')
    return None


def write_submission_script(f,resname,inptype):
    """ Creates the .pbs submission script for "_geom.inp" or
    "_resp.inp" files. Returns None.

    PARAMETERS
    ----------
    f : string
        Filename (the .pbs file written by this function)
    resname : string
        Three letter prefix for the molecule
    inptype : string
        "geom" or "resp" designator for whether this generates a .pbs
        file for a corresponding "_geom.inp" or "_resp.inp" file.

    """
    # Check if file exists (prevents overwrite)
    if os.path.isfile(f) is True:
        raise Exception('File {} already exists!\n'.format(f))
    # Append header to .pbs submission file
    with open(f, 'a') as f:
        f.write("#!/bin/bash\n")
        f.write("#SBATCH --partition=preempt \n")
        f.write("#SBATCH --nodes=1\n")
        f.write("#SBATCH --ntasks-per-node=12\n")
        f.write("#SBATCH --export=ALL\n")
        f.write("#SBATCH --time=0-24:00:00\n")
        f.write("#SBATCH --error={0}_opt.err\n\n".format(resname,inptype))
        f.write("test -d /tmp/{0}_opt || mkdir -v /tmp/{0}_opt\n\n".format(resname,inptype))
        f.write("module load gaussian\n\n")
        f.write("g09 < {0}_{1}.inp > {0}_{1}.out\n\n".format(resname,inptype))
        f.write("cp -pv /tmp/{0}_opt/{0}_opt.chk .\n\n".format(resname))
        f.write("rm -rv /tmp/{0}_opt\n\n".format(resname))
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


