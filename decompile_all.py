import glob
import os
for fname in glob.glob('*.CLA'):
    print(f"\nDecompiling {fname}\n-------------------------\n")
    os.system(f"python cla2txt.py {fname} | tee {fname}.TXT")
