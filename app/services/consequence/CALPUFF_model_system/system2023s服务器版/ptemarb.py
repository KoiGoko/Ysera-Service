# -*- coding: utf-8 -*-
"""
Created on Feb,2,2023
@author: xinjian
"""

import pandas as pd
import os,sys
import yaml,time

def getdate(dir_met):    # 从up文件获取年份
    with open(dir_met+'\\up101n.dat') as f:
        for i in range(6):
            temp=f.readline()
        return temp.split()[:1][0]


if __name__ == '__main__':

    s=time.time()
    print('源项文件开始处理! %s'%time.strftime('%Y-%m-%d %H:%M:%S'))

    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    dir_run=os.path.join(dir_sys['dir_out0'],grd['title'])

    dir_out=os.path.join(dir_run,'4release')
    dir_met=os.path.join(dir_run,'1geomet')

    (lat0,lon0,nx,ny,dx)=[grd['lat0'],grd['lon0'],grd['nx'],grd['ny'],grd['dx']]
    rinfo=grd['rinfo']

    if (len(rinfo) !=7 ):
        print('点源输入信息有误！，请检查')
        sys.exit(0)

    # sname=["'KR-85'","'I-131'","'CS-137'"]
    sname=["'KR-85'"]
    ns=len(sname)
    mol=[40]*ns

    # 获取计算的时间（up101.dat文件中读取）,简单都设置为整年释放
    yearup=getdate(dir_met)
    timerunb=pd.to_datetime(yearup+'0102')
    timerune=pd.to_datetime(yearup+'1231')

#输出

    lat0s="{:.4f}{N}".format(abs(lat0), N=('N' if  lat0>=0 else 'S'))
    lon0s="{:.4f}{E}".format(abs(lon0), E=('E' if  lon0>=0 else 'W'))
    lat1s='30.0'+lat0s[-1]
    lat2s='60.0'+lat0s[-1]

    # 生成文件名列表
    # fnames=['ptemarb'+'%04d'%i+'.dat' for i in range(1,nt+1)]
    fname='ptemarb.dat'

    with open(dir_out+'\\'+fname,"w",encoding='utf8')  as f:
        f.write('%-16s%-16s%-64s\n'% ('PTEMARB.DAT','2.1',grd['title']+'  point source'))
        f.write('   1' + "\n")
        f.write('NONE' + "\n")
        f.write('LCC'+'\n')
        f.write('%-16s'*4%(lat0s,lon0s,lat1s,lat2s)+'\n')
        f.write('%6.4f  %6.4f\n'%(0,0))
        f.write('%-8s%-12s\n'%('WGS-84','02-21-1984'))
        f.write('  KM'+'\n'+'UTC+0800' + "\n")
        # 输出日期
        # f.write('%4d  %3d  %2d  %4d     %4d  %3d  %2d  %4d\n'%())
        f.write(timerunb.strftime('%Y  %j  %H  %S       '))
        f.write(timerune.strftime('%Y  %j  %H  %S')+'\n')

        f.write('%-4d%-4d\n'%(1,ns))
        f.write(('%-12s'*ns+'\n')%(tuple(sname)))
        f.write(('%10.3f'*ns+'\n')%(tuple(mol)))
        # 释放物质标题
        f.write('%-12s'%("'"+grd['title']+"'"))
        f.write('%10.3f%10.3f%10.3f%10.3f%10.2f%6.2f%6.2f%6.2f\n'%
                tuple(rinfo[:5]+[0,0,0]))

        f.write(timerunb.strftime('%Y  %j  %H  %S       '))
        f.write(timerune.strftime('%Y  %j  %H  %S')+'\n')

        f.write('%-12s'%("'"+grd['title']+"'"))
        f.write('%7.2f%7.2f%10.2f%10.2f'%tuple([300,1]+rinfo[-2:]))
        f.write(('%10.2e'*ns+'\n')%(tuple([1.0]*ns)))

    print('源项文件输出完成,用时：%.2fs!'% (time.time()-s))





