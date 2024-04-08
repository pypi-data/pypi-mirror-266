import glob
import os
import shutil

data_dir = "data"
for product in ["MOD04_L2", "MYD04_L2", "MOD04_3K", "MYD04_3K"]:
    for filepath in sorted(list(glob.glob(f"{data_dir}/{product}/*/*.hdf", recursive=True))):
        filename = os.path.basename(filepath)
        dirname = os.path.dirname(filepath)
        day = filename.split(".")[1][-3:]
        objdir = os.path.join(dirname, day)
        if not os.path.exists(objdir):
            os.mkdir(objdir)
        shutil.move(filepath, os.path.join(objdir, filename))
        print(filename, day)

for product in ["AERDB_L2_VIIRS_SNPP", "AERDT_L2_VIIRS_SNPP"]:
    for filepath in sorted(list(glob.glob(f"{data_dir}/{product}/*/*.nc", recursive=True))):
        filename = os.path.basename(filepath)
        dirname = os.path.dirname(filepath)
        day = filename.split(".")[1][-3:]
        objdir = os.path.join(dirname, day)
        if not os.path.exists(objdir):
            os.mkdir(objdir)
        shutil.move(filepath, os.path.join(objdir, filename))
        print(filename, day)
