import glob
import os
for fname in glob.glob('*.TXT'):
    print(f"\nCompiling {fname}\n-------------------------\n")
    os.system(f"python txt2cla.py {fname}")
