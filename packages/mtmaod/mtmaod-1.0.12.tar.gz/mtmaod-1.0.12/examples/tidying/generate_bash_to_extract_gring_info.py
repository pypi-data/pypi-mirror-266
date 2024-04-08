data_dir = "data"
f = open("gen_bash_scripts_gring.sh", "w")
print("Generating bash scripts (MODIS HDF)...")
for product in ["MOD04_L2", "MYD04_L2", "MOD04_3K", "MYD04_3K"]:
    for year in range(2011, 2022):
        _pyscript = "get_gring_coordinates_from_modis_hdf.py"
        _path = f"{data_dir}/{product}/{year}/**/*.hdf"
        _out = f"{data_dir}/{product}/{year}/info_gring.csv"
        _log = f"out_gring_{product}_{year}.log"
        f.write(f'nohup python3 {_pyscript} --path "{_path}" --out "{_out}" > {_log} 2>&1 &\n')
print("Generating bash scripts (VIIRS NC)...")
for product in ["AERDB_L2_VIIRS_SNPP", "AERDT_L2_VIIRS_SNPP"]:
    for year in range(2011, 2022):
        _path = f"{data_dir}/{product}/{year}/**/*.nc"
        _out = f"{data_dir}/{product}/{year}/info_gring.csv"
        _log = f"out_gring_{product}_{year}.log"
        f.write(f'nohup python3 {_pyscript} --path "{_path}" --out "{_out}" > {_log} 2>&1 &\n')
f.close()
