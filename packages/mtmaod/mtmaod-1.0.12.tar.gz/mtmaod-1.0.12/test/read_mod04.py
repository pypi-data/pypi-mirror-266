from mtmaod.products.mod04 import MOD04
import psutil, os
import numpy as np

path = r"E:\software\project\20230117185746\download\MOD04_L2.A2023263.0410.061.2023263132925\MOD04_L2.A2023263.0410.061.2023263132925.hdf"

ds = MOD04.open(path)
band_names = MOD04.list_datasets(ds)
print(band_names)

band_aod = "Optical_Depth_Land_And_Ocean"
data_aod = MOD04.read(ds, band_aod)[:]
print(data_aod.dtype, data_aod.shape)

data_lat = MOD04.read(ds, MOD04.Band_Latitude)[:]
print(data_lat.dtype, data_lat.shape)

data_lon = MOD04.read(ds, MOD04.Band_Longitude)[:]
print(data_lon)
print(data_lon.dtype, data_lon.shape)

print(u'当前进程的内存使用：%.4f GB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 / 1024))