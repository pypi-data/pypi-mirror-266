from mtmaod.products.aeronet import LEVReader
import pandas as pd

if __name__ == "__main__":
    # 读取数据
    lev_file_path = r"19930101_20210102_Beijing.levl5"
    reader = LEVReader(lev_file_path, header=6)  # header为LEV文件的表头行索引, 默认文件第6行(从0开始)为表头行

    # Note: LEVReader实例的df变量即为读取的数据, LEVReader实例的方法若不指定dataframe参数, 则默认使用读取的df变量作为数据源
    # 筛选高质量数据
    df = reader.filter_high_quality_aod_rows()

    # 插值550nm波段的AOD, 当使用"scipy_curvefit" 或 "cubic+scipy"方法时, 调用多核CPU, 需要在"if __name__ == '__main__'"环境中使用
    df["AOD_550nm"] = reader.interp_aod_xxxnm(df, method="numpydeg2_polyfit", wavelength=550)

    # 对比不同AOD插值方法在500nm波段的表现
    reader.compare(dataframe=reader.df, filter_high_quality=True, wavelength=500)

    # 更新reader实例的df变量
    reader.df = df

    # 只保留AOD列
    df_aod = reader._only_keep_aod_column(df)

    # 插值到指定时间，构造时间戳数据框，注意时间戳的单位为秒
    # LEVReader的时区为UTC，因此依照时间插值时要注意产品的时区也应当是UTC时区的时间戳
    timestamps = pd.DataFrame.from_dict({"timestamp": [i.timestamp() + 900 for i in df.index]})
    # df_interp = reader.interp_aod_xxxtime(df["AOD_550nm"], objtime=timestamps, method="average")
    timestamps[["AOD_550nm", "counts"]] = reader.interp_aod_xxxtime(
        df["AOD_550nm"], objtime=timestamps, method="average"
    )
    print(timestamps)
    pass
