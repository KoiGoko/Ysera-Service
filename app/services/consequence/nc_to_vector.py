import gzip
import pickle

import netCDF4
import numpy as np
import os
from fastapi import File, UploadFile, FastAPI
from fastapi.responses import FileResponse
import shutil
from app.cors.handle_cors import handle_cors

app = FastAPI()


def create_upload_file():
    file_dir = 'dose01.nc'
    nc = netCDF4.Dataset(file_dir)
    print(nc.variables.keys())
    dose_eff = nc.variables['dose_eff'][:].astype(np.float32)
    return dose_eff


if __name__ == '__main__':
    create_upload_file()
