#!/stuff

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



""" IMPORT MODULES """



import glob # File selection wildcard *
import os # Change directories and prevent file overwrite
import re # Regular expressions (i.e. grep)
import shutil # Move files between directories
import subprocess as sp # Run shell commands
import sys # Error management



""" DEFINE FUNCTIONS """



def write_namelist():
    """
    Words

    """
    def get_molecule_params(parameter):
        """
        """
        loop = True
        while loop:
            out = input("Enter the molecule's " + parameter + ": ")
            try:
                int(out)
                return out
            except:
                print('\nERROR: Please enter an integer value.\n')

    nconf = get_molecule_params('number of conformers')
    natoms = get_molecule_params('number of atoms')
    charge = get_molecule_params('charge')
    multiplicity = get_molecule_params('multiplicity')

    loop = True
    forbidden_residues = [
    'ABY' ,'ACE' ,'ACX' ,'ADD' ,'ADE' ,'AGL' ,'ALA' ,'ALL' ,'AME' ,'AND' ,'ANY'     
    ,'APS' ,'ARG' ,'ASA' ,'ASB' ,'ASH' ,'ASN' ,'ASP' ,'ATD' ,'AVE' ,'AVG' ,'BCC'    
    ,'BCU' ,'BEG' ,'BGL' ,'BIO' ,'BSA' ,'BSB' ,'BUG' ,'CGL' ,'CHL' ,'CIM' ,'CIO'    
    ,'CIP' ,'CME' ,'CMU' ,'COO' ,'COR' ,'COS' ,'CRC' ,'CSA' ,'CSB' ,'CSD' ,'CYM'    
    ,'CYS' ,'CYT' ,'CYX' ,'DAE' ,'DAG' ,'DAL' ,'DAN' ,'DAP' ,'DCE' ,'DCN' ,'DCP'    
    ,'DEF' ,'DGD' ,'DGE' ,'DGL' ,'DGN' ,'DHA' ,'DHU' ,'DLM' ,'DMA' ,'DME' ,'DMF'    
    ,'DMG' ,'DMU' ,'DNA' ,'DSA' ,'DSB' ,'DTD' ,'DTE' ,'DTN' ,'DWG' ,'EGL' ,'END'    
    ,'EPW' ,'EQG' ,'ESA' ,'ESB' ,'ESP' ,'ESU' ,'FGL' ,'FOR' ,'FSA' ,'FSB' ,'GGL'    
    ,'GLH' ,'GLN' ,'GLU' ,'GLY' ,'GME' ,'GSA' ,'GSB' ,'GUA' ,'HCU' ,'HDU' ,'HEU'    
    ,'HGL' ,'HIA' ,'HID' ,'HIE' ,'HIP' ,'HIS' ,'HMC' ,'HNA' ,'HND' ,'HNE' ,'HOD'    
    ,'HOG' ,'HOH' ,'HPU' ,'HSA' ,'HSB' ,'HSG' ,'HWG' ,'HYP' ,'IGL' ,'ILE' ,'INO'    
    ,'INT' ,'ISA' ,'ISB' ,'IWG' ,'JAH' ,'JCC' ,'JCP' ,'JGL' ,'JMS' ,'JPC' ,'JSA'    
    ,'JSB' ,'JTR' ,'KGL' ,'KNK' ,'KSA' ,'KSB' ,'LEN' ,'LEO' ,'LEU' ,'LYH' ,'LYN'    
    ,'LYS' ,'MAC' ,'MAU' ,'MCU' ,'MEE' ,'MET' ,'MEU' ,'MEX' ,'MFC' ,'MMA' ,'MMC'    
    ,'MMG' ,'MMI' ,'MMU' ,'MOC' ,'MOD' ,'MOH' ,'MRA' ,'MRC' ,'MRG' ,'MRI' ,'MRP'    
    ,'MRU' ,'MSU' ,'MTA' ,'MTG' ,'NET' ,'NHE' ,'NLN' ,'NMA' ,'NME' ,'NOT' ,'NPT'    
    ,'NUM' ,'OAU' ,'OCU' ,'OEU' ,'OHB' ,'OHE' ,'OHG' ,'OLP' ,'OLS' ,'OLT' ,'OME'    
    ,'OMU' ,'OXT' ,'PAK' ,'PBG' ,'PDB' ,'PEA' ,'PEB' ,'PGA' ,'PGB' ,'PGR' ,'PGS'    
    ,'PHE' ,'PHU' ,'PKA' ,'PKB' ,'PLA' ,'PLB' ,'PMA' ,'PMB' ,'PNA' ,'PNB' ,'POM'    
    ,'PRE' ,'PRO' ,'PSU' ,'PTA' ,'PTB' ,'PTR' ,'QBD' ,'QBU' ,'QCD' ,'QCU' ,'QEA'    
    ,'QEB' ,'QGA' ,'QGB' ,'QGG' ,'QJD' ,'QJU' ,'QKA' ,'QKB' ,'QLA' ,'QLB' ,'QMA'    
    ,'QMB' ,'QMG' ,'QNA' ,'QNB' ,'QPD' ,'QPU' ,'QTA' ,'QTB' ,'QUG' ,'QVA' ,'QVB'    
    ,'QWA' ,'QWB' ,'QYA' ,'QYB' ,'RAN' ,'RCN' ,'RCW' ,'REA' ,'REB' ,'RGA' ,'RGB'    
    ,'RGE' ,'RGN' ,'RKA' ,'RKB' ,'RLA' ,'RLB' ,'RMA' ,'RMB' ,'RNA' ,'RNB' ,'ROH'    
    ,'RSH' ,'RSR' ,'RTA' ,'RTB' ,'RUE' ,'RUN' ,'SAU' ,'SCH' ,'SCU' ,'SEA' ,'SEB'    
    ,'SEP' ,'SER' ,'SEU' ,'SGA' ,'SGB' ,'SIA' ,'SJW' ,'SKA' ,'SKB' ,'SLA' ,'SLB'    
    ,'SMA' ,'SMB' ,'SMU' ,'SNA' ,'SNB' ,'SPA' ,'SPC' ,'SPF' ,'SPG' ,'STA' ,'STB'    
    ,'STU' ,'SUG' ,'TAA' ,'TAB' ,'TBT' ,'TDA' ,'TDB' ,'TEA' ,'TEB' ,'TER' ,'TFA'    
    ,'TFB' ,'TGA' ,'TGB' ,'THA' ,'THB' ,'THF' ,'THP' ,'THR' ,'THY' ,'TKA' ,'TKB'    
    ,'TLA' ,'TLB' ,'TMA' ,'TMB' ,'TME' ,'TMP' ,'TNA' ,'TNB' ,'TOA' ,'TOB' ,'TPF'    
    ,'TPO' ,'TQA' ,'TQB' ,'TRA' ,'TRB' ,'TRP' ,'TRU' ,'TTA' ,'TTB' ,'TUA' ,'TUB'    
    ,'TXA' ,'TXB' ,'TYP' ,'TYR' ,'TYU' ,'TZA' ,'TZB' ,'UBD' ,'UBU' ,'UCD' ,'UCU'    
    ,'UEA' ,'UEB' ,'UGA' ,'UGB' ,'UJD' ,'UJU' ,'UKA' ,'UKB' ,'ULA' ,'ULB' ,'UMA'    
    ,'UMB' ,'UME' ,'UNA' ,'UNB' ,'UPD' ,'UPU' ,'URA' ,'URE' ,'USE' ,'UTA' ,'UTB'    
    ,'UVA' ,'UVB' ,'UWA' ,'UWB' ,'UYA' ,'UYB' ,'VAL' ,'VBD' ,'VBU' ,'VCD' ,'VCU'    
    ,'VDW' ,'VEA' ,'VEB' ,'VGA' ,'VGB' ,'VJD' ,'VJU' ,'VKA' ,'VKB' ,'VLA' ,'VLB'    
    ,'VMA' ,'VMB' ,'VNA' ,'VNB' ,'VPD' ,'VPU' ,'VTA' ,'VTB' ,'VVA' ,'VVB' ,'VWA'    
    ,'VWB' ,'VYA' ,'VYB' ,'WAA' ,'WAB' ,'WAT' ,'WBA' ,'WBB' ,'WBD' ,'WBG' ,'WBU'    
    ,'WCA' ,'WCB' ,'WCD' ,'WCU' ,'WDA' ,'WDB' ,'WEA' ,'WEB' ,'WFA' ,'WFB' ,'WGA'    
    ,'WGB' ,'WHA' ,'WHB' ,'WHY' ,'WJA' ,'WJB' ,'WJD' ,'WJU' ,'WKA' ,'WKB' ,'WLA'    
    ,'WLB' ,'WMA' ,'WMB' ,'WMG' ,'WNA' ,'WNB' ,'WOA' ,'WOB' ,'WPA' ,'WPB' ,'WPD'    
    ,'WPU' ,'WQA' ,'WQB' ,'WRA' ,'WRB' ,'WTA' ,'WTB' ,'WUA' ,'WUB' ,'WVA' ,'WVB'    
    ,'WWA' ,'WWB' ,'WXA' ,'WXB' ,'WYA' ,'WYB' ,'WYG' ,'WZA' ,'WZB' ,'XEA' ,'XEB'    
    ,'XGA' ,'XGB' ,'XKA' ,'XKB' ,'XLA' ,'XLB' ,'XMA' ,'XMB' ,'XNA' ,'XNB' ,'XTA'    
    ,'XTB' ,'YAA' ,'YAB' ,'YDA' ,'YDB' ,'YEA' ,'YEB' ,'YFA' ,'YFB' ,'YGA' ,'YGB'    
    ,'YHA' ,'YHB' ,'YIL' ,'YKA' ,'YKB' ,'YLA' ,'YLB' ,'YMA' ,'YMB' ,'YNA' ,'YNB'    
    ,'YOA' ,'YOB' ,'YQA' ,'YQB' ,'YRA' ,'YRB' ,'YTA' ,'YTB' ,'YTV' ,'YUA' ,'YUB'    
    ,'YXA' ,'YXB' ,'YZA' ,'YZB' ,'ZAA' ,'ZAB' ,'ZAD' ,'ZAU' ,'ZDA' ,'ZDB' ,'ZDD'    
    ,'ZDU' ,'ZEA' ,'ZEB' ,'ZFA' ,'ZFB' ,'ZGA' ,'ZGB' ,'ZHA' ,'ZHB' ,'ZKA' ,'ZKB'    
    ,'ZLA' ,'ZLB' ,'ZMA' ,'ZMB' ,'ZNA' ,'ZNB' ,'ZOA' ,'ZOB' ,'ZQA' ,'ZQB' ,'ZRA'    
    ,'ZRB' ,'ZRD' ,'ZRU' ,'ZTA' ,'ZTB' ,'ZUA' ,'ZUB' ,'ZXA' ,'ZXB' ,'ZXD' ,'ZXU'    
    ,'ZZA' ,'ZZB']

    while loop:
        resname = input('Enter a three letter abbreviation for your molecule: ').upper()
        if len(resname) != 3:
            print('\nERROR: Please make sure your residue is only 3 letters long.\n')
        elif resname.isalpha() is False:
            print('\nERROR: Chosen abbreviation must contain only letters.\n')
        elif resname in forbidden_residues:
            print('\nERROR: Chosen abbreviation already exists in a standard residue library.')
        else:
            loop = False

    # Writes namelist.in file
    # Assumes file should be saved in directory from which the program
    # is run
    with open("namelist.in", 'w') as namelist:
        namelist.write('nconf\n')
        namelist.write(nconf + '\n')
        namelist.write('natoms\n')
        namelist.write(natoms + '\n')
        namelist.write('charge\n')
        namelist.write(charge + '\n')
        namelist.write('multiplicity\n')
        namelist.write(multiplicity + '\n')
        namelist.write('resname\n')
        namelist.write(resname + '\n\n')
        for i in range(conf_num):
            namelist.write(str(res_name) + str(i + 1) + '\n')



def read_namelist(f="namelist.in"):
    """ Reads in the parameters and conformer names from "namelist.in"
    Designed to work on a modified version of namelist.in in which the
    multiplicity and charge are given on separate lines. Also note, this
    function does NOT check that "namelist.in" is properly formatted, so
    double check formatting before use.

    PARAMETERS
    ----------
    f : string The path/filename containing the data to be imported.
        Defaults to "namelist.in" if no argument is given.

    RETURNS
    -------
    params : dictionary
        Contains the different job parameters, i.e.:
        [0] = job type,
        [1] = number of conformers,
        [2] = number of atoms,
        [3] = charge
        [4] = multiplicity
        [5] = 3 letter residue prefix
    confnames : list
        Contains the conformer names.

    """
    # Checks that "namelist.in" exists
    if os.path.isfile(f) is not True:
        raise FileNotFoundError('File {} is missing!\n'.format(f))

    # Opens namelist.in and appends each line to a list while stripping
    # newline "\n" characters
    namelist=[]
    with open(f, 'r') as file:
        for line in file:
            namelist.append(line.strip('\n'))

    # Makes a separate list for just the conformer names and removes all
    # empty items from the list of conformer names
    confnames = namelist[12:]
    confnames[:] = [x for x in confnames if x]

    # Renames the first element to "jobtype" and creates a dictionary 
    # for the different parameters
    namelist=[x.replace(namelist[0], 'jobtype') for x in namelist]
    del namelist[12:]
    params=dict(zip(namelist[::2], namelist[1::2]))
    return params,confnames


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






def write_resp_in(f='resp.in',nconfs,iqopt,ihfree,qwt):
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


def write_leap_in(f='leap.in',resname):
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

    loop = True

    while loop:
        print_resp_menu()
        choice = input("Enter your choice [1-6]: ")

        if choice == "1":
            loop = False
            return
        elif choice == "2":
            loop = False
            return
        elif choice == "3":
            loop = False
            return
        elif choice == "4":
            loop = False
            return
        elif choice == "5":
            loop = False
            return
        elif choice == "6":
            loop = False
            return main_menu()
        else:
            input("Not an option. Press any key to try again.\n")
        
def main_menu():
    """
    UNFINISHED
    """
    def print_main_menu():
        title = "MAIN MENU"
        formatting = int( (78 - len(title)) / 2 ) * "-"
        print(formatting, title, formatting, "\n")
        print("I want to...")
        print("1. Build conformer libraries and run electronic structure calculations.")
        print("2. Build the force fields for MD simulations (RESP fitting).")
        print("3. Read more about what this program does.")
        print("4. Exit the program.\n")
        print(79 * "-", "\n")

    loop = True

    while loop:
        print_main_menu()
        choice = input("Enter your choice [1-4]: ")

        if choice == "1":
            loop = False
            # get_dft_menu_choice()
            return
        elif choice == "2":
            loop = False
            return resp_menu()
        elif choice == "3":
            help(main_menu)
        elif choice == "4":
            loop = False
            raise SystemExit
        else:
            input("Not an option. Press any key to try again.\n")





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
    Returns True if converged or False if not yet converged.

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


def main():
    """ This is the main program.
    UNFINISHED
    """


cwd = os.getcwd()

namelist = read_namelist('namelist.in')
job = namelist[0]["jobtype"]

#  JOB TYPE 1

if job == "1":
    resname = namelist[0]["resname"]
    chrg = namelist[0]["charge"]
    mult = namelist[0]["multiplicity"]
    nconf = int(namelist[0]["nconf"])

    # Make .inp and .pbs files for geom and resp calculations and move them
    # into their own directories
    for i in range(0,nconf):
        conformer = namelist[1][i]
        write_submission_script(conformer+"_geom.pbs",conformer,"geom")
        write_submission_script(conformer+"_resp.pbs",conformer,"resp")
        write_geom_input(conformer+"_geom.inp",resname,conformer,chrg,mult, 4, 8)
        write_resp_input(conformer+"_resp.inp",resname,conformer,chrg,mult, 4, 8)
        os.mkdir(conformer)
        for f in glob.glob(conformer+'*pbs'):
            shutil.move(f, conformer)
        for f in glob.glob(conformer+'*inp'):
            shutil.move(f, conformer)

    # Submits the pbs files in each directory
    for i in range(0,nconf):
        conformer = namelist[1][i]
        os.chdir(conformer)
        sp.check_call("sbatch -A richmondlab *geom.pbs", shell=True)
        os.chdir(cwd)

#  JOB TYPE 2

elif job == "2":

    # Generate esp.dat files
    for i in range(0,nconf):
        write_esp_dat(namelist[1][i])

    # Concatenate all esp.dat files
    sp.check_call("cat *esp.dat > espot", shell=True)

    # END STEP 6 --- START STEP 7

    # Build the first resp.in file
    write_resp_in('resp.in',nconfs,'1','1','00')

    # END STEP 7 --- START STEP 8

    # Run the resp fit for the first time
    # -q qin not required since iqopt = 1
    sp.check_call("resp -O -i resp.in -o resp.out -e espot", shell=True)

    # Check punch file to make sure everything is working

    # Duplicate qout as qin (output charge file becomes the input charge
    # file for the next resp fit)
    sp.check_call("cp qout qin", shell=True)

    # Rename punch, qout, espot files to punch##, qout##, espot## so that
    # the files are backed up and don't get overwritten
    os.rename('punch', 'punch{}'.format(0))
    os.rename('qout', 'qout{}'.format(0))
    os.rename('espot', 'espot{}'.format(0))

    """
    STEP 9 SHOULD BE DONE MANUALLY?

    # END STEP 8 --- START STEP 9

    try:
        sp.check_call(
            "cp /packages/amber/12/dat/leap/parm/parm99.dat ./", \
             shell=True)
    except:
        raise FileNotFoundError('Could not find parm99.dat file!\n')

    # Check the parameters with one of (the first in this case) mol files
    sp.check_call(
        "parmchk -i {}1.mol2 -o {}.frcmod -f mol2 -p parm99.dat".format(
            resname), shell=True)

    # Checks the parameters automatically
    with open(resname + '.frcmod', 'r') as f:
        for line in f:
            if re.search('ATTN', line):
                raise Exception('ATTN Error detected in .frcmod file!\n')
    """


    """
    Job type = 2 steps:

    DONE-- Create RESP directory
    DONE-- Move files to the RESP directory
    DONE-- Change the current directory to RESP
    DONE-- Create esp.dat files for each conformer
    DONE-- Concatenate all esp.dat files into espot
    DONE-- For the first resp fit, edit resp.in so iqopt = 1 and for each
           conformer, list the atoms and the restrictions for the charge and
           create the matrix at the bottom of the file
    DONE-- Run the resp fit

    Get the charges for the first molecular unit from qout and copy them into
    qnext

    DONE-- Make a copy of qout and name the file qin

    Rename punch, qout, and espot to punch#, qout#, and espot# so everything is
    backed up

    Run job type = 3 to get updated .mol2 file (I don't think this is
    necessary. If anything, we just need to run a single command - the
    antechamber command I think...)

    DONE-- Copy the parm99.dat file into the RESP folder

    BY HAND ? Check the parameters with one of the mol2 files

    BY HAND ? Find suitable replacment parameters in parm99.dat or gaff.dat

    BY HAND ? Edit the [ABC].frcmod file with the new parameters

    Edit the leap.in files so it knows to get the modified parameter file

    """

    resp_dir = os.mkdir('RESP')

    for files in os.listdir():
        if filename.endswith('_resp.out'):
            shutil.move(files, resp_dir)
        if filename.endswith('.mol2'):
            shutil.move(files, resp_dir)

    cwd = os.chdir('RESP')

    for i in range(0,nconf):
        conf = resname + str(i + 1)
        write_esp_dat(conf)

    esp_filelist = []
    cwd = os.getcwd()
    # Create a list of [ABC]_esp.dat files that is sorted based on the
    # number in the file name.
    for files in os.listdir(cwd):
        if filename.endswith("_esp.dat"):
            esp_filelist.append(filename)
        esp_filelist = sorted(esp_filelist, key=lambda x:
                      int("".join([i for i in x if i.isdigit()])
                         )
                     )

    # Concatenate all esp.dat files into the espot file.
    with open('espot', 'w') as espot:
        for i in esp_filelist:
            with open(os.path.join(cwd,i)) as infile:
                for line in infile:
                    espot.write(line)

# Tried to run the program to test job type ==1, but the program will not run
# --Python doesn't like ' in the code
""" JOB TYPE 3 """
elif job == "3":

    # For each conformer:

        ' mv ABC#_esp.dat esp.dat '

        '
        antechamber -o Temp.mol2 -fo mol2 -c rc -cf qnext -at amber -fi
            mol2 -i ABC#.mol2 -rn ABC

            -o    : output file name
            -fo   : output file format
            -c    : charge method
            -cf   : charge file name
            -at   : atom type (gaff [default], amber, bcc, sybyl)
            -fi   : input file format
            -i    : input file name
            -rn   : residue name (overrides input file [default = MOL])
            -help : gives full flag menu for antechamber

            -i, -o, -fi, -fo MUST appear. All other flags are optional.
        '

        '
        tleap -s -f leap.in

            -s : ignore leaprc startup file
            -f : source file
        '

        '
        sander -O -i sander.in -o sander.out -c prmcrd -p prmtop

            -O : overwrite output files
            -i : input control data for the min/md run
            -o : output user readable state infor and diagnostics (-o
            stdout will send output to stdout (to the terminal) instead of
            to a file)
            -c : input initial coordinates and (optionally) velocities and
            periodic box size
            -p : input molecular topology, force field, periodic box type,
            atom and residue names
        '

        ' rm ANTECHAMBER* ATOMTYPE.INF leap.log mdinfo prmcrd sander.out
           restrt '

        ' mv Temp.mol2 ABC#.mol2 '

        ' mv esp.dat ABC#_esp.dat '

        ' mv prmtop ABC#.top '

        ' mv esp.induced ABC#_esp.induced '

        ' mv esp.qm-induced ABC#_esp.qm-induced '

    sp.check_call("mv {}_esp.dat esp.dat".format(conf))

    sp.check_call(\
        'antechamber -o Temp.mol2 -fo mol2 -c rc -cf qnext -at amber \
        -fi mol2 -i {}.mol2 -rn {}'.format(conf,resname)

# Use sp.check_call("bash cmd", shell=True)
# Note: sp.check_call() and sp.run() should ALWAYS be
# preferred over sp.call(), sp.Popen(), os.system(), and
# os.popen().

""" UNRECOGNIZED JOB TYPE """
else:
    raise ValueError('Unacceptable job type chosen. Check namelist.in \
    file and try again.\n')



""" START PROGRAM """



if __name__=="__main__":
    main()
