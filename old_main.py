#!/usr/bin/env python

cwd = os.getcwd()

namelist = read_namelist('namelist.in')
job = namelist[0]["jobtype"]

#  JOB TYPE 1

if job == "1":

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

