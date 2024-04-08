from osgeo import gdal


path = r"C:\Users\imutu\Desktop\MOD021KM.A2021001.0405.061.2021001130625.hdf"
datasets = gdal.Open(path)
SubDatasets = datasets.GetSubDatasets()
SubDatasetsNum =  len(datasets.GetSubDatasets())
#  获取hdf中的元数据
Metadata = datasets.GetMetadata()
#  获取元数据的个数
MetadataNum = len(Metadata)
#  输出各子数据集的信息
print("元数据一共有{0}个: ".format(MetadataNum))
for key,value in Metadata.items():
    print('{key}:{value}'.format(key = key, value = value))