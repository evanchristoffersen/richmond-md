#!/usr/bin/env python

""" 

"""



import glob # File selection wildcard *
import os # Change directories and prevent file overwrite
import re # Regular expressions (i.e. grep)
import shutil # Move files between directories
import subprocess as sp # Run shell commands
import sys # Error management

# from . import namelist
import namelist


__authors__ = 'Evan Christoffersen', 'Konnor Jones'
# __license__
# __version__



def detectfile(f='namelist.in'):
    """ Searches the current working directory for the specified file 
    (defaults to "namelist.in". If file isn't found, the user is given 
    the opportunity to write namelist.in.

    PARAMETERS
    ----------
    f : string
        Filename (defaults to "namelist.in")

    RETURNS
    -------
    True : if file isn't found but the user chooses to make it
    False : if file isn't found and user chooses not to make it
    None : if file is found

    """
    if os.path.isfile(f) is False:
        while True:
            print('File "namelist.in" is missing from the directory.')
            q = input('Would you like to build it [y or n]: ')
            if q == 'Y' or q == 'y':
                return True
            elif q == 'N' or q == 'n':
                return False
            else:
                input('\nERROR: {} is not an option. Try again.\n'.format(q))
    else:
        return

def writefile(f='namelist.in'):
    """ Writes the "namelist.in" file from scratch to working directory
    based on user input. Returns None.
    
    PARAMETERS
    ----------
    f : string
        Filename (defaults to "namelist.in")

    """
    # List containing existing residue abbreviations in Amber's library
    # Using one of these abbreviations causes amber to default to that 
    # residue rather than the molecule the user is interested in
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

    def get_params(param, negative = False):
        """ Gets integer values from the user, checking the integer's 
        sign and that it isn't a different type. 

        PARAMETERS
        ----------
        param : string
            The desired parameter you wish to prompt from the user.
        negative : Boolean
            True -> negative integer values are allowed
            False -> negative integer values are not allowed (default)

        RETURNS
        -------
        out : string
            Integer value from user as string type

        """
        while True:
            try:
                out = int(input("Enter the " + param + ": "))
                if int(out) < 0 and negative == False:
                    print('\nERROR: Enter a positive integer value.\n')
                else:
                    return str(out)
            except:
                print('\nERROR: Enter an integer value.\n')

    # Prevents overwrite of file if namelist.in already exists
    if os.path.isfile(f) is True:
        raise Exception('File "namelist.in" already exists!\n')

    print()
    nconf = get_params('number of conformers')
    natoms = get_params('number of atoms')
    chrg = get_params('molecular charge',True)
    mult = get_params('molecular multiplicity')

    # Checks residue abbreviation for length of 3 characters, alphabet 
    # characters only, and against existing residue abbreviations
    loop = True
    while loop:
        resname = input(
            'Enter a three letter abbreviation for your molecule: ').upper()
        if len(resname) != 3:
            print('\nERROR: Residue must be exactly three letters in length.\n')
        elif resname.isalpha() is False:
            print('\nERROR: Residue must contain only letters.\n')
        elif resname in forbidden_residues:
            print('\nERROR: Residue already exists in a standard library.\n')
        else:
            loop = False

    # Writes namelist.in file to working directory
    with open(f, 'w') as namelist:
        namelist.write('nconf\n')
        namelist.write(nconf + '\n')
        namelist.write('natoms\n')
        namelist.write(natoms + '\n')
        namelist.write('charge\n')
        namelist.write(chrg + '\n')
        namelist.write('multiplicity\n')
        namelist.write(mult + '\n')
        namelist.write('resname\n')
        namelist.write(resname + '\n\n')
        for i in range(int(nconf)):
            i += 1
            namelist.write(resname + str(i) + '\n')

def readfile(f="namelist.in"):
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
        [0] = number of conformers,
        [1] = number of atoms,
        [2] = charge
        [3] = multiplicity
        [4] = 3 letter residue prefix
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
    confnames = namelist[10:]
    confnames[:] = [x for x in confnames if x]

    del namelist[10:]
    params=dict(zip(namelist[::2], namelist[1::2]))
    return params,confnames

def write_esp_dat(conf):
    """ This function uses the contents of the {}_resp.out file to write
    the corresponding {}_esp.dat file for each conformer. Depending on
    the size of the conformer and the size of its resp.out file, this
    function may take a few seconds to run per conformer. Returns None.

    --- PARAMETERS ---
    conf : string
        The three letter prefix + integer conformer index used to
        identify the different conformers.

    """
    # Conversion factor from Angstroms to Bohrs
    cnv_factor = 0.529177249

    ngrid_raw = []
    atomic_centers = []
    # ulimit -n : maximum number of files that can be open simultaneously
    # "ESP Fit" and "Fit" values are written to temporary files. Seemed risky
    # storing tens of thousands of values in memory
    try:
        with open(conf + '_resp.out', 'r') as f, \
             open(conf + '_esp.dat', 'w') as out \
             open('tmp00.txt', 'w') as b, \
             open('tmp01.txt', 'w') as c:
            for line in f:
                if re.search('NGrid ', line):
                    ngrid_raw.append(line.split()[2])
                elif re.search('Atomic Center ', line):
                    atomic_centers.append(line.split()[5:8])
                elif re.search('ESP Fit', line):
                    b.write(line)
                elif re.search('Fit    ', line):
                    c.write(line)
                else:
                    pass

            ngrid_out = ngrid_raw[0] + str(int(ngrid_raw[1]) - int(ngrid_raw[0]))
            # Four empty spaces must always lead ngrid_out in {}_esp.dat
            spacing = 4 + len(ngrid_out)
            out.write('{v:>{s}}\n'.format(v=ngrid_out,s=spacing))

            for i in range(0,len(atomic_centers)):
                x = fortran_format(float(atomic_centers[i][0]) / cnv_factor)
                y = fortran_format(float(atomic_centers[i][1]) / cnv_factor)
                z = fortran_format(float(atomic_centers[i][2]) / cnv_factor)
                out.write('{:>32}{:>16}{:>16}\n'.format(x, y, z))

    except OSError:
        print('File {}_resp.out cannot be read.\n'.format(conf))
        print('File creation skipped for {}_esp.dat\n'.format(conf))

    except:
        print('Unexpected error during {}_esp.dat file creation.\n'.format(conf))
        raise

    else:
        with open('tmp00.txt', 'r') as b, \
             open('tmp01.txt', 'r') as c, \
             open(conf + '_esp.dat', 'a') as out:
            for line_b, line_c in zip(b, c):
                esp_fit = line_b.split()
                fit = line_c.split()
                w = fortran_format(float(fit[2]))
                x = fortran_format(float(esp_fit[6]) / cnv_factor)
                y = fortran_format(float(esp_fit[7]) / cnv_factor)
                z = fortran_format(float(esp_fit[8]) / cnv_factor)
                out.write('{:>16}{:>16}{:>16}{:>16}\n'.format(w, x, y, z))

        # Removes the temporary files from the directory
        os.remove('tmp00.txt')
        os.remove('tmp01.txt')
        return None


def check_punch_convergence(f='punch'):
    """ This function compares the values in the "q0" column of a
    "punch" file to the "qopt" column. When all q0 = qopt, this
    indicates that the resp fitting has converged.

    --- PARAMETERS ---
    f : string
        Filename (should always just be "punch")

    --- RETURNS ---
    True : if converged
    False : if not converged

    """
    # Open punch file and save lines to memory (isolate items indexed
    # at '2' and '3' where applicable
    punch = []
    try:
        with open(f, 'r') as punchfile:
            for line in punchfile:
                punch.append(line.split()[2:4])
    except:
        raise

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


