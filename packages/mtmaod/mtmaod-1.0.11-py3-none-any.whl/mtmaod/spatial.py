import numpy as np


def is_point_in_gring(plat: float, plon: float, gringlat: np.ndarray, gringlon: np.ndarray):
    if (min(gringlat) <= plat <= max(gringlat)) and (min(gringlon) <= plon <= max(gringlon)):
        return True
    else:
        return False


def query_index_of_spatial_nearest_point(plat: float, plon: float, dlat: np.ndarray, dlon: np.ndarray):
    dlat = np.array(dlat)
    dlon = np.array(dlon)
    # 检测是否为全NaN数组
    if np.all(np.isnan(dlat)) or np.all(np.isnan(dlon)):
        return -1, -1, -1
    # 计算距离
    temp_res_array = (np.array(dlat) - plat) ** 2 + (np.array(dlon) - plon) ** 2
    # 获取最小值的索引
    temp_idx = np.nanargmin(temp_res_array)
    lat_idx, lon_idx = np.unravel_index(temp_idx, temp_res_array.shape)
    # 返回索引和距离值(平方和)
    return lat_idx, lon_idx, temp_res_array[lat_idx, lon_idx]
