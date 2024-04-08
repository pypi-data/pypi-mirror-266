from mtmaod.products.modis_grid_rslab import MODISGrid

if __name__ == "__main__":
    path = r"C:\Users\imutu\Desktop\MOD021KM_L.1000.2021001040500.H26V05.000000.h5"
    with MODISGrid.open(path) as ds:
        print(MODISGrid.list_datasets(ds))
        d = MODISGrid.read(ds, "/AngleData/SolarAzimuthAngle")
        dp = MODISGrid.read(ds, "/AngleData/SolarAzimuthAngle").dp
        data = MODISGrid.read(ds, "/AngleData/SolarAzimuthAngle")[:]
