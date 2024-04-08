import os
import glob
import argparse

import pandas as pd
import netCDF4 as nc

parser = argparse.ArgumentParser(description="Get Ging Coordinates From VIIRS NC Files")
parser.add_argument("--path", help="Pathname pattern string of VIIRS NC Files")
parser.add_argument("--out", help="Path of Output File")


def get_gring_from_viirs_nc(path):
    # 使用netcdf4读取nc文件
    fp = nc.Dataset(path, mode="r")
    # 从属性信息中提取坐标信息
    longitude_gring = fp.GRingPointLatitude
    latitude_gring = fp.GRingPointLongitude
    # 将坐标信息转换为浮点数
    longitude_gring = [float(i) for i in longitude_gring]
    latitude_gring = [float(i) for i in latitude_gring]
    return longitude_gring + latitude_gring


def batch_read_hdf_to_generate_hv_csv(paths: list):
    if not isinstance(paths, list):
        raise TypeError("Parameter(paths) must be list")
    grings = {}
    paths = sorted(paths)
    for path in paths:
        print(path)
        # 获取文件名称
        filename = os.path.basename(path)
        coordinates = get_gring_from_viirs_nc(path)
        grings[filename] = coordinates
    # 将字典转换为DataFrame
    if len(grings) == 0:
        return pd.DataFrame()
    df = pd.DataFrame.from_dict(grings, orient="index").reset_index()
    df.columns = ["filename", "lon1", "lon2", "lon3", "lon4", "lat1", "lat2", "lat3", "lat4"]
    df.sort_values(["filename"], inplace=True)
    return df


if __name__ == "__main__":
    args = parser.parse_args()
    # 获取文件列表
    path_re_str = args.path
    out_path = args.out
    paths = list(glob.glob(path_re_str, recursive=True))
    print(f"文件数量: {len(paths)}")  # 输出文件数量
    # 读取文件，生成out文件
    df = batch_read_hdf_to_generate_hv_csv(paths)
    df.to_csv(out_path, index=False)
