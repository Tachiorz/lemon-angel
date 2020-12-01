import filecmp
import glob
import os

for fname in glob.glob('*.TXT'):
    print(f"\nCompiling {fname}\n-------------------------\n")
    os.system(f"python txt2cla.py {fname}")

exit()
# compare with backed up CLAs
for fname in glob.glob('*.CLA'):
    if not filecmp.cmp(fname, 'backup/' + fname):
        raise Exception(fname + "doesn't match")
