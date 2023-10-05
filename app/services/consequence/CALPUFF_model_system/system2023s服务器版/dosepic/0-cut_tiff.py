#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读取目录中的tiff文件，并按照一定范围来裁剪
"""

import os,glob
from osgeo import gdal
from pyproj import Transformer
from  pyproj  import  CRS
import numpy as np
import yaml
import time

s = time.time()

def cut_tiff(dir_in,dir_out_tiff):
    # 根据输入文件经纬度和网格，计算图片尺寸
    (lon0,lat0,nx,ny,dx)=[grd['lon0'],grd['lat0'],grd['nx'],grd['ny'],grd['dx']]
    rx=dx*nx/2*1000
    ry=dx*ny/2*1000

    #读取目录下的tif和tiff文件
    oritiff=glob.glob(os.path.join(dir_in,'*.tif*'))

    epsg = 32700 - np.round((45 + lat0) / 90) * 100 + np.round((183 + lon0) / 6)
    utmzone = 'EPSG:%d' % (epsg)
    crs=CRS.from_epsg(4326)
    crs_cs=CRS.from_epsg(epsg)
    transformer= Transformer.from_crs(crs,crs_cs)
    UTM0_east,UTM0_north=transformer.transform(lat0,lon0)

    top = UTM0_north +ry
    down = UTM0_north-ry
    left = UTM0_east - rx
    right = UTM0_east + rx

    ds = gdal.Warp(dir_out_tiff, oritiff,
                          format='Gtiff',
                          outputBounds=[left, down, right, top],
                          dstSRS=utmzone,
                          creationOptions=['COMPRESS=LZW'])
    del ds

if __name__ == '__main__':

    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('..\系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('..\用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('绘图配置.YAML', 'r', encoding='utf-8') as f:
        picinfo = yaml.load(f.read(), Loader=yaml.FullLoader)

    dir_run=os.path.join(dir_sys['dir_out0'],grd['title'])
    dir_out=os.path.join(dir_run,'9pic',picinfo['dir_tif'])

    dir_in=picinfo['dir_tif_in']

    cut_tiff(dir_in,dir_out)


