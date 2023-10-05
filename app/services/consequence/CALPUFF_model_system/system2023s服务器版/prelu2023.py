#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 12:18:51 2023

@author: chengyouying
程序直接读取ESA 10米精度数据 计算全球任意一点土地利用数据
"""
import os,glob
from osgeo import gdal
import numpy as np
import yaml
import time
from osgeo import osr
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors

s = time.time()

def prelu(dir_tiff_input,dir_tiff_output,grd,dir_sys,fnames=None):
    (lon0,lat0,nx,ny,dx)=[grd['lon0'],grd['lat0'],grd['nx'],grd['ny'],grd['dx']]

    '''
    自定义函数部分
    '''

    # 自定义函数2，对tiff图像进行裁剪
    def clip_tif(dir_tiff_input, dir_tiff_output, fnames=None):
        tempfile1 = os.path.join(dir_tiff_output, 'temp.tif')

        rx = nx * dx / 2 * 1.1
        ry = ny * dx / 2 * 1.1

        top = lat0 + ry / 110
        down = lat0 - ry / 110
        left = lon0 - rx / np.cos(np.pi * lat0 / 180) / 110
        right = lon0 + rx / np.cos(np.pi * lat0 / 180) / 110


        del_fnames = []
        if fnames == None:
            fnames = []

            for i in np.arange((3*int(np.floor(down)/3)),(3*int(np.ceil((top)/3))+3),3):
                for j in np.arange( 3*int((np.floor(left)/3)),(3*int(np.ceil(right)/3)+3),3):
                    fname="ESA_WorldCover_10m_2020_v100_{N}{E}_Map.tif".\
                        format(N=('N%02d'%i if  i>=0 else 'S%02d'%abs(i)),
                               E=('E%03d'%j if  j>=0 else 'W%03d'%abs(j)))
                    path = os.path.join(dir_tiff_input, fname)
                    if os.path.exists(path) == False:
                        geotrans = [0, 1/12000, 0.0, 0, 0.0, -1/12000]
                        geotrans[0] = j
                        geotrans[3] = i + 3
                        path_new=os.path.join(dir_tiff_output, fname)
                        writeImage(path_new, geotrans)
                        fnames.append(path_new)
                        del_fnames.append(path_new)
                    else:
                        fnames.append(path)

        # 合并所有的文件R
        vrtfile = gdal.BuildVRT('temp1.vrt', fnames)
        ds = gdal.Warp(tempfile1, vrtfile,
                       format='Gtiff',
                       outputBounds=[left, down, right, top],
                       outputBoundsSRS='EPSG:4326',
                       xRes=dx/240,
                       yRes=dx/240,
                       creationOptions=['COMPRESS=LZW'],
                       resampleAlg='mode')

        del ds, vrtfile
        for path in del_fnames:
            os.remove(path)


     # 自定义函数3，对tiff图像进行转码，然后打印输出
    def tiff2dat(dir_in,dir_out):
         '''
         根据裁剪完的tiff，写成文本文件,保存在dir_out中
         '''
         dataset = gdal.Open(os.path.join(dir_in,'temp.tif'))

        # 读取数据范围
         band1 = dataset.GetRasterBand(1).ReadAsArray()

        # 数据类型转换
         s1=[10,20,30,40,50,60,70,80,90,95,100]
         s2=[40,30,30,20,10,70,90,50,60,60,80]

         band2  = np.where(band1 == 0,  50, band1)
         for i in np.arange(11):
            band2  = np.where(band1 == s1[i], s2[i], band2)

         print('数据类型转换完成！')

         # 读取投影坐标信息，生成经纬度数组
         mygeotranform=dataset.GetGeoTransform()
         lon=np.arange(np.shape(band1)[1])*mygeotranform[1]+mygeotranform[0]
         lat=np.arange(np.shape(band1)[0])*mygeotranform[5]+mygeotranform[3]
         [xx,yy]=np.meshgrid(lon,lat)

         band3=band2.reshape(-1,1)
         xx1=xx.reshape(-1,1)
         yy1=yy.reshape(-1,1)

         outdata=np.concatenate((band3,xx1,yy1),axis=1)

         cat =[10,20,30,40,50,60,70,80,90]

         with open(os.path.join(dir_out, "GenericLULC11_t.dat"), "w+") as fiLe:
             print('GENERIC.LANDUSE 1.0             LU, Longitude,  Latitude (free-format)', file=fiLe)
             print(2, file=fiLe)
             print('Prepared by User', file=fiLe)
             print('Longitude is positive to east,  Latitude is positive to north', file=fiLe)
             print('LL', file=fiLe)
             print('WGS-84 02-21-2003', file=fiLe)
             print('DEG', file=fiLe)
             print( 9, file=fiLe)

             for i in range(len(cat)):
                    print(cat[i], end='  ',file=fiLe)
             print('',file=fiLe)

             np.savetxt(fiLe,  outdata,  fmt=" %3d%14.5f %14.5f")

         print('离散土地利用数据文件输出完成!')


    # 自定义字符串替换函数
    def str_replace(info,keystr,newstr):
        '''
        将info包含关键字keystr的字符串，替换为newstr，并做适当调整
        '''
        for i in range(len(info)):
            if keystr in info[i]:
                temp=info[i].split('=')[0]+'= '+newstr+' !\n'
                info[i]=temp
                break
        return info

    # 批量对inp文件进行替换处理
    def inp_map_modify(dir_in,file_ori):
        '''
        将输入文件中涉及投影信息的参数进行替换,9个变量
        mygrid 包含读入的5个变量，程序内重新赋值，依次替换
        '''
        # (lon0,lat0,nx,ny,dx)=[grd['lon0'],grd['lat0'],grd['nx'],grd['ny'],grd['dx']]
        xref=-nx*dx/2
        yref=-ny*dx/2

        info=open(file_ori,  "r").readlines()

        info=str_replace(info,'(RLAT0)',"{:.4f}{N}".format(abs(lat0), N=('N' if  lat0>0 else 'S')))
        info=str_replace(info,'(RLON0)',"{:.4f}{E}".format(abs(lon0), E=('E' if  lon0>0 else 'W')))

        info=str_replace(info,'(RLAT1)',"{:.2f}{N}".format(30.0, N=('N' if  lat0>0 else 'S')))
        info=str_replace(info,'(RLAT2)',"{:.2f}{N}".format(60.0, N=('N' if  lat0>0 else 'S')))

        info=str_replace(info,'(NX)','{:d}'.format(int(nx)))
        info=str_replace(info,'(NY)','{:d}'.format(int(ny)))

        info=str_replace(info,'(XREFKM)','{:.2f}'.format(xref))
        info=str_replace(info,'(YREFKM)','{:.2f}'.format(yref))
        info=str_replace(info,'(DGRIDKM)','{:.3f}'.format(dx))

        with open(os.path.join(dir_in,"ctgproc.inp"),  "w") as f1:
            for templine in info:
                f1.write(templine)
        print('输入参数文件修改完成！')

    def process(dir_tiff_output):
            cmd1=dir_tiff_output+'\ctgproc_v7.0.0.exe'
            pwd=os.getcwd()
            os.chdir(dir_tiff_output)
            os.system(cmd1)
            os.chdir(pwd)


    def landusepic(dir_tiff_output,title):
     # 自定义函数，对tiff图像进行画图输出
        rgb=([0,100,0],[255,187,34],[255,255,76],[240,150,255],[250,0,0],[180,180,180],
              [240,240,240],[0,100,200],[0,150,160],[0,207,117],[250,230,160])

        rgb=np.array(rgb)/255.0
        cmap=colors.ListedColormap(rgb,name='ERA_color')
        bounds=[9,11,21,31,41,51,61,71,81,91,96,101]
        bounds2=[(bounds[i]+bounds[i+1])/2 for i in range(11)]
        norm = mpl.colors.BoundaryNorm(bounds,cmap.N)
        im =mpl.cm.ScalarMappable(cmap=cmap,norm=norm)

        dataset = gdal.Open(os.path.join(dir_tiff_output,'temp.tif'))
        band1 = dataset.GetRasterBand(1).ReadAsArray()
        band2  = np.where(band1 == 0, 80, band1)

        # 读取投影坐标信息，生成经纬度数组
        mygeotranform=dataset.GetGeoTransform()
        lon=np.arange(np.shape(band1)[1])*mygeotranform[1]+mygeotranform[0]
        lat=np.arange(np.shape(band1)[0])*mygeotranform[5]+mygeotranform[3]
        dataset = None

        fig = plt.figure(figsize=(6,4.9),dpi=200)
        ax1 = fig.add_axes([0.12, 0.1, 0.67, 0.83])
        ax1.imshow(band2,cmap=cmap, norm=norm)

        list1=np.linspace(0,np.size(lon)-1,5).astype('int')
        list1=list1.tolist()
        list11=lon[list1]
        x1= ['%.2f'%(x)  for x in list11 ]

        list2=np.linspace(0,np.size(lat)-1,5).astype('int')
        list2=list2.tolist()
        list21=lat[list2]
        y1= ['%.2f'%(x)  for x in list21 ]

        ax1.set_xticks(list1)
        ax1.set_yticks(list2)

        ax1.set_xticklabels(x1,fontsize=8)
        ax1.set_yticklabels(y1,fontsize=8)
        ax1.set_xlabel('longitude',fontsize=10)
        ax1.set_ylabel('latitude',fontsize=10)
        plt.title('land use of '+title,fontsize=10)

        ax2 = fig.add_axes([ax1.get_position().x1+0.02,ax1.get_position().y0,
                        0.03, ax1.get_position().height])
        cbar=plt.colorbar(im,cax=ax2,ticks=bounds2)
        cbar.set_ticklabels(['tree','shrubland','grassland','cropland','built-up','bare',
                             'snow & ice','water','wetland','mangroves','moss lichen'])
        plt.rcParams['font.size']=8

        plt.savefig(os.path.join(dir_tiff_output,'land use of '+title+'.png'),dpi=200)
        # plt.show()
        print('landuse pic save complete!')

    #自定义函数用来生成临时文件
    def writeImage(path, geotrans, proj=4326):
        data = np.zeros((36000, 36000))+80
        # 创建文件
        driver = gdal.GetDriverByName("GTiff")
        #两个3600分别是影像宽度和高度，1代表波段数，gdal.GDT_Int16是tiff的数据类型
        dataset = driver.Create(path, 36000, 36000, 1, gdal.GDT_Int16)
        dataset.SetGeoTransform(geotrans)  # 写入仿射变换参数
        #写入投影信息
        srs = osr.SpatialReference() #建立编码
        srs.ImportFromEPSG(proj)     #WGS84 lat/lon
        dataset.SetProjection(srs.ExportToWkt())  #把wkt格式的编码写入投影
        dataset.GetRasterBand(1).WriteArray(data)

    """
    调用函数，选择适当分辨率原始图像
    """
    # orgtif=choose_tif(grd['dx'],dir_tiff_input)

    """
    调用函数，对图像进行裁剪
    """
    if fnames==None:
        clip_tif(dir_tiff_input,dir_tiff_output)
    else:
        clip_tif(dir_tiff_input,dir_tiff_output,fnames)

    """
    调用函数，对图像进行渲染
    """
    landusepic(dir_tiff_output,grd['title'])

    '''
    #将tiff数值调整内容后输出到文本文件
    '''
    tiff2dat(dir_tiff_output,dir_tiff_output)

    """
    读取inp文件，修改地图投影等相关内容
    """
    inp_map_modify(dir_tiff_output,os.path.join(dir_sys['dir_model'],'ctgproc-ori.inp'))

    """
    执行程序自带程序,生成lu.dat文件
    """
    process(dir_tiff_output)


if __name__=='__main__':
    start = time.time()
    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    with open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    dir_run = os.path.join(dir_sys['dir_out0'], grd['title'])
    dir_out_lu= os.path.join(dir_run, '0geo\\lu')
    if not os.path.exists(dir_out_lu):
        os.makedirs(dir_out_lu)

    if 'dir_esa' in grd:
        dir_in_esa = grd['dir_esa']
        fnames=glob.glob(os.path.join(dir_in_esa,'*.tif'))
        prelu(dir_in_esa, dir_out_lu, grd,dir_sys, fnames)
    else:
        dir_in_esa=dir_sys['dir_esa']
        prelu(dir_in_esa, dir_out_lu, grd,dir_sys)
    print(time.time()-start)
