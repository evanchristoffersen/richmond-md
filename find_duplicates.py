
import glob
import os

import rmsd

# METHOD 1
xyzfiles = []
os.chdir('mydir')
for file in glob.glob("*.xyz"):
    xyzfiles.append(file)

# METHOD 2
xyzfiles = []
for file in os.listdir('mydir'):
    if file.endswith("*xyz"):
        xyzfiles.append(file)

xyzfiles = []
for file in os.listdir('./'):
    if file.endswith('xyz'):
        xyzfiles.append(file)

def rmsd_test(filelist=xyzfiles):
    foo = []
    for i in range(0,len(filelist)-1):
        for j in range(i+1,len(filelist)-1):
            save_stdout = sys.stdout
            result = StringIO()
            sys.stdout = result
            # returns none type
            # number viewed in stdout cannot be saved as a variable or appended
            # easily to a list.
            # it's akin to trying: foo = print('bar') and expecting foo to then
            # return 'bar'. It won't work. foo will return None
            rmsd.main([filelist[i],filelist[j]])
            sys.stdout = save_stdout
            foo.append(result.getvalue())
            result.close()
    # Note: it may actually be safer to write values to a temporary file. Even
    # just 100 conformers returns a list close to 6000 items long. Or maybe
    # only keep track of values with an rmsd below a certain threshold.
    return foo
