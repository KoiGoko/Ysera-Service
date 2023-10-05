# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 21:49:41 2022

@author: xinjian
"""

import os,glob
import shutil
import yaml
from prelu2023 import prelu
from preter2023 import preter
import pregeo


if __name__ == '__main__':

    """
    程序初始化，建立目录，拷贝必要数据，返回相关目录和用户输入信息
    """
    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)


    cwd=os.getcwd()
    dir_run=os.path.join(dir_sys['dir_out0'],grd['title'])

    # 第二步，建立程序运行目录，如果已经存在，直接删除覆盖
    if  os.path.exists(dir_run):
        shutil.rmtree(dir_run)
    os.makedirs(dir_run)

    dir_subs=['0geo\\ter','1geomet','2metinp','3metout',
           '4puffinp','4release','5puffout','6xq','7source','8dose','9pic']
    os.chdir(dir_run)
    for dir1 in dir_subs:
        os.makedirs(dir1)
    os.chdir(cwd)

     # 第三步，将系统准备的lu和geo计算文件夹复制到算例目录
    shutil.copytree(dir_sys['dir_model']+'\\geo', dir_run+'\\0geo\\geo')
    shutil.copytree(dir_sys['dir_model']+'\\lu', dir_run+'\\0geo\\lu')


    """
    对地形高程数据进行处理
    """
    dir_in_ter=dir_sys['dir_ter']
    dir_out_ter=os.path.join(dir_run,'0geo\\ter')

    if 'dir_ter' in grd:
        dir_in_ter = grd['dir_ter']
        fnames=glob.glob(os.path.join(dir_in_ter,'*.tif'))
        preter(dir_in_ter, dir_out_ter, grd,fnames)
    else:
        dir_in_ter=dir_sys['dir_ter']
        preter(dir_in_ter, dir_out_ter, grd)

    """
    对土地利用数据进行处理
    """
    dir_out_lu=os.path.join(dir_run,'0geo\lu')

    if 'dir_esa' in grd:
        dir_in_esa = grd['dir_esa']
        fnames=glob.glob(os.path.join(dir_in_esa,'*.tif'))
        prelu(dir_in_esa, dir_out_lu, grd,dir_sys, fnames)
    else:
        dir_in_esa=dir_sys['dir_esa']
        prelu(dir_in_esa, dir_out_lu, grd,dir_sys)

    """
    对geo文件进行处理
    """
    dir_in_geo=os.path.join(dir_sys['dir_model'],'makegeo-ori.inp')
    dir_out_geo=os.path.join(dir_run,'0geo\geo')

    shutil.copy(os.path.join(dir_out_ter,'ter.dat'), dir_out_geo)
    shutil.copy(os.path.join(dir_out_lu,'lulc.dat'), dir_out_geo)

    pregeo.pregeo(dir_in_geo,dir_out_geo,grd)

    shutil.copy(os.path.join(dir_out_geo,'geo.dat'),
                os.path.join(dir_run,'1geomet'))



