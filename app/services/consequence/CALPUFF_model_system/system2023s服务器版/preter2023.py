#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 23:47:31 2022
@author: chengyouying
在上一个版本的基础上修改坐标系获取的方式为EPSG编号
程序直接读取ALOS 30米精度数据 计算全球任意一点地面高程数据
使用函数调用的方式来完成，同时考虑用户自定义输入。
"""

from osgeo import gdal,osr
import os,glob
import numpy as np
from scipy import interpolate
import datetime,time,yaml
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib as mpl

def preter(path_inp,path_out,grd,fnames=None):


    (lon0, lat0, nx, ny, dx) = [grd['lon0'], grd['lat0'], grd['nx'], grd['ny'], grd['dx']]

    epsg = 32700 - np.round((45 + lat0) / 90) * 100 + np.round((183 + lon0) / 6)
    utmzone = 'EPSG:%d' % (epsg)

    rx = nx * dx / 2 * 1.1
    ry = ny * dx / 2 * 1.1
    top = lat0 + ry / 110
    down = lat0 - ry / 110
    left = lon0 - rx / np.cos(np.pi * lat0 / 180) / 110
    right = lon0 + rx / np.cos(np.pi * lat0 / 180) / 110

    def writeImage(path, geotrans,proj=4326):

        driver = gdal.GetDriverByName("GTiff")
        #两个3600分别是影像宽度和高度，1代表波段数，gdal.GDT_Int16是tiff的数据类型
        dataset = driver.Create(path, 3600, 3600, 1, gdal.GDT_Int16)

        dataset.SetGeoTransform(geotrans)  # 写入仿射变换参数
        data = np.zeros((3600, 3600),dtype='int16')

        #写入投影信息
        srs = osr.SpatialReference() #建立编码
        srs.ImportFromEPSG(proj)     #WGS84 lat/lon
        dataset.SetProjection(srs.ExportToWkt())  #把wkt格式的编码写入投影
        dataset.GetRasterBand(1).WriteArray(data)

    tempfile1 = os.path.join(path_out, 'temp1.tif')
    del_fnames = []
    if fnames == None:
        fnames = []
        for i in np.arange((np.floor(down)), (np.ceil(top) + 1)):
            for j in np.arange((np.floor(left)), (np.ceil(right) + 1)):
                fname = "ALPSMLC30_{N}{E}_DSM.tif". \
                    format(N=('N%03d' % i if i >= 0 else 'S%03d' % abs(i)),
                           E=('E%03d' % j if j >= 0 else 'W%03d' % abs(j)))
                path = os.path.join(path_inp, fname)

                if os.path.exists(os.path.join(path_inp, fname)) == False:
                    geotrans = [0, 1/3600, 0.0, 0, 0.0, -1/3600]
                    geotrans[0] = j
                    geotrans[3] = i + 1
                    path_new=os.path.join(path_out, fname)
                    writeImage(path_new, geotrans)
                    fnames.append(path_new)
                    del_fnames.append(path_new)
                else:
                    fnames.append(path)


    vrtfile = gdal.BuildVRT('temp1.vrt', fnames)

    ds = gdal.Warp(tempfile1, vrtfile,
                   format='Gtiff',
                   outputBounds=[left, down, right, top],
                   outputBoundsSRS='EPSG:4326',
                   xRes=dx*1000/2,
                   yRes=dx*1000/2,
                   dstSRS=utmzone,
                   creationOptions=['COMPRESS=DEFLATE'],
                   resampleAlg='average')

    z = ds.ReadAsArray()  # 获取数据栅格数据
    nyz,nxz=np.shape(z)
    x1 = np.linspace(-nxz*dx*0.5,nxz*dx*0.5,nxz)
    y1 = np.linspace(-nyz*dx*0.5,nyz*dx*0.5,nyz)

    x2 = np.linspace(-nx * dx / 2, nx * dx / 2, nx)
    y2 = np.linspace(-ny * dx / 2, ny * dx / 2, ny)

    x3=np.linspace(-nx*dx/2,nx*dx/2,nx*2)  # 加密后用于画图
    y3=np.linspace(-ny*dx/2,ny*dx/2,ny*2)


    # 插值 kind：插值方式，有三种可选，分别是'linear'（线性插值）、'cubic'（三次样条插值）、'quintic'（五次样条插值）
    newfunc = interpolate.interp2d(x1, y1, z, kind='linear')
    ter = newfunc(x2, y2)
    ter = np.where(ter < 0, 0, ter)

    # 处理画图的数值
    terpic=newfunc(x3,y3)
    terpic=np.where(terpic<0,0,terpic)

    fileName = os.path.join(path_out, 'ter.dat')

    with open(fileName, 'wt') as file:
        file.write('TERREL.DAT      2.0             Header structure with coordinate parameters      ' + '\n')
        file.write('   2' + '\n')
        file.write('Produced by TERREL Version: 3.69  Level: 110330                                   ' + '\n')
        file.write('Internal Coordinate Transformations  ---  COORDLIB   Version: 1.99   Level: 070921' + '\n')
        file.write('LCC     ' + '\n')

        lat0s = "{:.4f}{N}".format(lat0, N=('N' if lat0 >= 0 else 'S'))
        lon0s = "{:.4f}{E}".format(lon0, E=('E' if lon0 >= 0 else 'W'))
        lat1s = '30.0'+lat0s[-1]
        lat2s = '60.0'+lat0s[-1]

        file.write('%-16s'*4 % (lat0s,lon0s,lat1s,lat2s) + '\n')

        file.write(' 0.00000000E+00 0.00000000E+00' + '\n')
        now = datetime.datetime.now()
        file.write('WGS-84  %02d-%02d-%4d' % (now.day, now.month, now.year) + '\n')
        file.write('%7d%7d%12.3f%12.3f%10.3f%10.3f'%(nx,ny,-nx*dx/2,-ny*dx/2,dx,dx)+'\n')
        file.write('KM  M  ' + '\n')
        file.write('W_E N_S ' + '\n')
        for i in range(0, ny):
            for j in range(0, nx):
                if (j + 1) % 10 == 0 or j + 1 == nx:
                    file.write('%8.1f' % ter[i][j] + '\n')
                else:
                    file.write('%8.1f' % ter[i][j])

    del ds, vrtfile
    for fname in del_fnames:
        os.remove(fname)

    # 将地形高程数据进行渲染输出

    # 自定义函数，从系统自带的cmap中截取
    def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
        new_cmap = colors.LinearSegmentedColormap.from_list(
            'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
            cmap(np.linspace(minval, maxval, n)), n)
        return new_cmap

    cmap = plt.cm.jet
    cmap2 = truncate_colormap(cmap, 0.2, 0.85, 40)

    norm = mpl.colors.Normalize(np.min(terpic),np.max(terpic))
    im =mpl.cm.ScalarMappable(cmap=cmap2,norm=norm)

    fig = plt.figure(figsize=(6,5),dpi=200)
    ax1 = fig.add_axes([0.1, 0.1, 0.75, 0.8])
    ax1.imshow(terpic,cmap=cmap2, norm=norm,extent =[x3[0], x3[-1], y3[0],y3[-1]])

    list1=np.linspace(x3[0],x3[-1],5)
    xtick= ['%.2f'%(x)  for x in list1]

    list2=np.linspace(y3[0],y3[-1],5)
    ytick= ['%.2f'%(x)  for x in list2]

    ax1.set_xticks(list1)
    ax1.set_yticks(list2)

    ax1.set_xticklabels(xtick,fontsize=8)
    ax1.set_yticklabels(ytick,fontsize=8)

    ax1.set_xlabel('x',fontsize=10)
    ax1.set_ylabel('y',fontsize=10)
    plt.title('terrain of '+grd['title'],fontsize=10)

    ax2 = fig.add_axes([ax1.get_position().x1+0.02,ax1.get_position().y0,
                    0.03, ax1.get_position().height])
    plt.colorbar(im,cax=ax2)
    plt.rcParams['font.size']=8

    plt.savefig(os.path.join(path_out,'ter of '+grd['title']+'.png'),dpi=200)



if __name__=='__main__':
    start = time.time()
    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    with open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    dir_run = os.path.join(dir_sys['dir_out0'], grd['title'])
    dir_out = os.path.join(dir_run, '0geo\\ter')

    if  not os.path.exists(dir_out):
        os.makedirs(dir_out)

    if 'dir_ter' in grd:
        dir_in = grd['dir_ter']
        fnames=glob.glob(os.path.join(dir_in,'*.tif'))
        preter(dir_in, dir_out, grd,fnames)
    else:
        dir_in=dir_sys['dir_ter']
        preter(dir_in, dir_out, grd)

    print(time.time()-start)



