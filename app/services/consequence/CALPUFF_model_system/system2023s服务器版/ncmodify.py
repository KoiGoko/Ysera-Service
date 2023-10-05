# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 08:37:28 2023

@author: xinjian
"""
import xarray as xr
import datetime
import time,os,yaml,glob
import pandas as pd
import numpy as np

def read_xq(dir_xq):
    """
    读入一个大气弥散因子数据，并删除前24小时结果
    """
    with xr.open_dataset(dir_xq) as ds:
        # print(ds)
        ds1=ds.drop_isel(t=range(24))

    dir_xq1=dir_xq.replace('grid_','')

    ds1.to_netcdf(dir_xq1)
    return

if __name__ == '__main__':


    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    dir_in=os.path.join(dir_sys['dir_out0'],grd['title'],'6xq')

    dir_xqs=glob.glob(os.path.join(dir_in,'*.nc'))
    dir_xqs.sort()

    for i in range(1,len(dir_xqs)):
        read_xq(dir_xqs[i])
        os.remove(dir_xqs[i])

    os.rename(dir_xqs[0],dir_xqs[0].replace('grid_',''))








