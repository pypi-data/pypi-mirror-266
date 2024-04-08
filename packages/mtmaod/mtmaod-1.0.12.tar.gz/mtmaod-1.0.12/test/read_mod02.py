from mtmaod.products.mod02 import MOD02, PyHDF
import psutil, os
import numpy as np

path = r"C:\Users\imutu\Desktop\MOD021KM.A2021001.0405.061.2021001130625.hdf"

ds = MOD02.open(path)
band_names = MOD02.list_datasets(ds)
print(band_names)

band_1KM_RefSB = "EV_1KM_RefSB"
data_1KM_RefSB = MOD02.read(ds, band_1KM_RefSB)
table = MOD02.table_scales_and_offsets(ds)
# band_aod = "Optical_Depth_Land_And_Ocean"
# data_aod = MOD04.read(ds, band_aod)[:]
# print(data_aod.dtype, data_aod.shape)

# data_lat = MOD04.read(ds, MOD04.Band_Latitude)[:]
# print(data_lat.dtype, data_lat.shape)

# data_lon = MOD04.read(ds, MOD04.Band_Longitude)[:]
# print(data_lon)
# print(data_lon.dtype, data_lon.shape)

# print(u'当前进程的内存使用：%.4f GB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 / 1024))

pass