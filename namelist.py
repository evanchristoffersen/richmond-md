#!/usr/bin/env python

""" A collection of functions for detecting, reading, and writing the
namelist.in file.

"""

import os # Change directories and prevent file overwrite

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
