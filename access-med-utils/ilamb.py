from pathlib import Path
import glob
import os
import xarray

rootpath = {
    "CMIP6": ["/g/data/fs38/publications/CMIP6", "/g/data/oi10/replicas/CMIP6"],
    "CMIP5": ["/g/data/r87/DRSv3/CMIP5", "/g/data/al33/replicas/CMIP5/combined", "/g/data/rr3/publications/CMIP5/output1"]
}

mip_vars ={
    'Emon':['cSoil'],
    'Lmon':['cVeg','gpp','lai','nbp','ra','rh','tsl'],
    'Amon':['evspsbl','hfls','hfss','hurs','pr','rlds','rlus','rsds','rsus','tasmax','tasmin','tas'],
    'Omon':['hfds'],
    }

def get_CMIP6_path(institute = "*", dataset = "*", exp = "*", ensemble = "*", mip="*"):
    return f"CMIP/{institute}/{dataset}/{exp}/{ensemble}/{mip}"

def get_CMIP5_path(institute = "*", dataset = "*", exp = "*", ensemble = "*", mip="*"):
    return f"{institute}/{dataset}/{exp}/mon/*/{mip}/{ensemble}"


get_path_function = {
    "CMIP6": get_CMIP6_path,
    "CMIP5": get_CMIP5_path
}

def add_model_to_tree(ilamb_root, dataset, project, exp, ensemble):
    """
    """
    print(f"Adding {dataset} to the ILAMB Tree")
    model_root = f"{ilamb_root}/MODELS/{dataset}/{exp}/{ensemble}"
    Path(model_root).mkdir(parents=True, exist_ok=True)

    for mip, vars in mip_vars.items():
        models = []
        for path in rootpath[project]:
            search_path = os.path.join(path, get_path_function[project](dataset=dataset, exp=exp, ensemble=ensemble, mip=mip))
            models += glob.glob(search_path)
        if models:
            model = models[0]
            for var in vars:
                if project == "CMIP6":
                    files = glob.glob(model+f"/{var}/**/latest/*.nc")
                if project == "CMIP5":
                    files = glob.glob(model+f"/*/{var}/*.nc")
                if not files:
                    continue
                if len(files) == 1:
                    try:
                        Path(f"{model_root}/{var}.nc").unlink()
                    except:
                        pass
                    Path(f"{model_root}/{var}.nc").symlink_to(f"{files[0]}")
                if len(files) > 1:
                    with xarray.open_mfdataset(files, use_cftime=True, combine_attrs='drop_conflicts') as f:
                        f.to_netcdf(f"{model_root}/{var}.nc")
    return