from mtmaod.products.mod09 import MOD09
import psutil, os
import numpy as np
from pprint import pprint as print

path = r"C:\Users\imutu\Desktop\MOD09GA.A2021001.h24v04.061.2021012061136.hdf"

ds = MOD09.open(path)
band_names = MOD09.list_datasets(ds, full=True)
print(band_names)

band = "sur_refl_b02_1"
data = MOD09.read(ds, band)[:]
print(data)
print((data.dtype, data.shape))
# band_aod = "Optical_Depth_Land_And_Ocean"
# data_aod = MOD09.read(ds, band_aod)[:]
# print(data_aod.dtype, data_aod.shape)

# data_lat = MOD09.read(ds, MOD09.Band_Latitude)[:]
# print(data_lat.dtype, data_lat.shape)

# data_lon = MOD09.read(ds, MOD09.Band_Longitude)[:]
# print(data_lon)
# print(data_lon.dtype, data_lon.shape)

# print(u'当前进程的内存使用：%.4f GB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 / 1024))