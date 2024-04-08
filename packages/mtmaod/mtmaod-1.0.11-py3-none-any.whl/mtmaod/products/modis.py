import numpy as np
import pandas as pd
from mtmaod.utils.pyhdf import PyHDF, SDS
from mtmaod.utils.netCDF4 import NetCDF4

from ._template import (
    SatelliteProductDataPyHDF,
    SatelliteProductReaderPyHDF,
    SatelliteProductReaderNetCDF4,
    SatelliteProductDataNetCDF4,
)


# ===================================================================================================
class MXD02Data(SatelliteProductDataPyHDF):

    def scale_and_offset(self, data: np.ndarray):
        infos: dict = self.infos()
        radiance_scales = MXD02Data.value_set_decimal(infos.get("reflectance_scales", 1), decimal=None)
        radiance_offsets = MXD02Data.value_set_decimal(infos.get("reflectance_offsets", 0), decimal=None)
        fill_value = infos.get("_FillValue")
        data = data.astype(np.float64)
        data[data == fill_value] = np.nan
        return radiance_scales * (data - radiance_offsets)


class MXD02Reader(SatelliteProductReaderPyHDF):
    Product_File_Time_Format = "[.]A%Y%j[.]%H%M[.]"
    LinkedDataClass = MXD02Data

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = PyHDF.read(fp, dataset_name, *args, **kwargs)
        DataClass = MXD02Reader.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)

    @staticmethod
    def table_scales_and_offsets(fp, *args, **kwargs):

        bands = ["EV_1KM_RefSB", "EV_1KM_Emissive", "EV_250_Aggr1km_RefSB", "EV_500_Aggr1km_RefSB"]
        columns = [
            "band_names",
            "reflectance_scales",
            "reflectance_offsets",
            "radiance_scales",
            "radiance_offsets",
            "corrected_counts_scales",
            "corrected_counts_offsets",
        ]
        indexes_string = "1,2,3,4,5,6,7,8,9,10,11,12,13lo,13hi,14lo,14hi,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36"
        indexes = indexes_string.split(",")
        df_list = []
        for band in bands:
            info = MXD02Reader.read(fp, band, *args, **kwargs).infos()
            info["band_names"] = info.get("band_names").split(",")
            _info = {k: info[k] for k in columns if k in info}
            df_list.append(pd.DataFrame(_info))
        return pd.concat(df_list, ignore_index=True).set_index("band_names").loc[indexes, :]


# ===================================================================================================
class MXD04L2Reader(SatelliteProductReaderPyHDF):
    Product_File_Time_Format = "[.]A%Y%j[.]%H%M[.]"
    LinkedDataClass = SatelliteProductDataPyHDF
    Band_Latitude = "Latitude"
    Band_Longitude = "Longitude"

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = PyHDF.read(fp, dataset_name, *args, **kwargs)
        DataClass = MXD04L2Reader.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)


# ===================================================================================================
class MXD09Reader(SatelliteProductReaderPyHDF):
    Product_File_Time_Format = "[.]A%Y%j[.]"
    LinkedDataClass = SatelliteProductDataPyHDF

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = PyHDF.read(fp, dataset_name, *args, **kwargs)
        DataClass = MXD09Reader.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)


# ===================================================================================================
class MXDLabGridReader(SatelliteProductReaderNetCDF4):
    Product_File_Time_Format = "[.]%Y%j%H%M%S[.]"  # MOD021KM_L.1000.2021001040500.H26V05.000000.h5
    LinkedDataClass = SatelliteProductDataNetCDF4

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = NetCDF4.read(fp, dataset_name, *args, **kwargs)
        DataClass = MXDLabGridReader.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)


# ===================================================================================================
class MCD19A2Reader(SatelliteProductReaderPyHDF):
    Product_File_Time_Format = "MCD19A2[.]A%Y%j[.]"
    LinkedDataClass = SatelliteProductDataPyHDF

    @staticmethod
    def read(fp, dataset_name, *args, isRaw=False, **kwargs):
        dp = NetCDF4.read(fp, dataset_name, *args, **kwargs)
        DataClass = MCD19A2Reader.LinkedDataClass
        return DataClass(dp, isRaw=isRaw)

    @staticmethod
    def list_orbit_times(fp):
        return [i for i in fp.attributes()["Orbit_time_stamp"].split(" ") if i]
