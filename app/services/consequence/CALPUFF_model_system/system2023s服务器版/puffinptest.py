 # -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 20:29:53 2022
@author: xinjian
对calpuffInp文件进行批量修改并运行
"""
from functools import partial
import os,glob,copy,time,datetime
import numpy as np
import pandas as pd
from multiprocessing import Pool
from os import path
import yaml


# 自定义字符串替换函数
def str_replace(info,keystr,newstr):
    '''
    将info包含关键字keystr的字符串，替换为newstr，并增加结尾及换行符号
    '''
    for i in range(len(info)):
        if keystr in info[i]:
            temp=info[i].split('=')[0]+'= '+newstr+' !\n'
            temp=temp.replace('*','!')
            info[i]=temp
            break
    return info


def insert(info, keystr, insert_list,offset=0,cutlines=0):
    '''
    将info包含关键字keystr的字符串位置，插入新的list
    并可灵活设置偏移行数,插入后需要删除的行数
    '''

    for i in range(len(info)):  # 寻找插入的位置
        if keystr in info[i]:
            break
    i+=offset   # 考虑偏移量

    for line1 in insert_list:       # 循环插入内容
        if not line1.endswith('\n'):
            line1=line1+'\n'

        info.insert(i+1,line1)
        i+=1

    if cutlines>0:
        del info[i:i+cutlines]

    return info

def mapgrd(info,grd):
    '''
    对地图投影信息进行更新，共9+4=13个参数
    '''
    (lon0,lat0,nx,ny,dx)=[grd['lon0'],grd['lat0'],grd['nx'],grd['ny'],grd['dx']]
    xref=-nx*dx/2
    yref=-ny*dx/2

    info=str_replace(info,'(RLAT0)',"{:.4f}{N}".format(abs(lat0), N=('N' if  lat0>0 else 'S')))
    info=str_replace(info,'(RLON0)',"{:.4f}{E}".format(abs(lon0), E=('E' if  lon0>0 else 'W')))

    info=str_replace(info,'(XLAT1)',"{:.2f}{N}".format(30.0, N=('N' if  lat0>0 else 'S')))
    info=str_replace(info,'(XLAT2)',"{:.2f}{N}".format(60.0, N=('N' if  lat0>0 else 'S')))

    info=str_replace(info,'(NX)','{:d}'.format(int(nx)))
    info=str_replace(info,'(NY)','{:d}'.format(int(ny)))

    info=str_replace(info,'(XORIGKM)','{:.2f}'.format(xref))
    info=str_replace(info,'(YORIGKM)','{:.2f}'.format(yref))
    info=str_replace(info,'(DGRIDKM)','{:.2f}'.format(dx))

    info=str_replace(info,'(IECOMP)','{:d}'.format(int(nx)))   #calpuff.inp 文件特有四个参数
    info=str_replace(info,'(JECOMP)','{:d}'.format(int(ny)))

    info=str_replace(info,'(IESAMP)','{:d}'.format(int(nx)))
    info=str_replace(info,'(JESAMP)','{:d}'.format(int(ny)))
    return info

def print_inp(dir_out,fname,info):
    '''
    dir_out，fnames 输出的目录和文件名(可多个)
    info：输出的内容，list形式
    '''
    with open(dir_out + '\\' + fname, 'w') as f:
            for line in info:
                f.write(line)

def run_puff1(fname, dir_puffout, dir_exe):
    '''
    输入一个calpuff.inp的名字，目录等信息，执行一个算例
    '''
    command = dir_exe + '\\calpuffl.exe ' + fname

    while True:
        os.system(command)
        with open(path.join(dir_puffout,
                  fname.split('\\')[-1].split('.')[0]+".lst"), 'r') as f:
            content = f.readlines()[-1]
            if "CPU" in content:
                break
    return

def getyear(dir_met):    # 从up文件获取年份
    with open(dir_met+'\\up101n.dat') as f:
        for i in range(6):
            temp=f.readline()
        return int(temp[0:6])

if __name__ == '__main__':
    s=time.time()
    print('calpuff输入文件生成开始 %s'%time.strftime('%Y-%m-%d %H:%M:%S'))

    #第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    # 读入原始calpuff.inp文件
    with  open(path.join(dir_sys['dir_model'],grd['puff_ori_file'])) as f:
        info=f.readlines()

    '''
    对目录初始化
    '''
    dir_run=os.path.join(dir_sys['dir_out0'],grd['title'])
    dir_met=path.join(dir_run,'1geomet')
    dir_metout=path.join(dir_run,'3metout')

    dir_puffinp=path.join(dir_run,'4puffinp')
    dir_puffout=path.join(dir_run,'5puffout')

    dir_release=path.join(dir_run,'4release')

    '''
    先修改与时间无关的参数
    '''
    info=mapgrd(info,grd)      #修改投影和网格信息
    info=str_replace(info,'(XBTZ)','-8.')      # 修改时区
    # info=str_replace(info,'(NVL1)','0')      # 修改内置源项个数
    # info=str_replace(info,'(NVL2)','1')      # 修改外部源项个数
    info=str_replace(info,'(NPT1)','0')      # 修改内置源项个数
    info=str_replace(info,'(NPT2)','1')      # 修改外部源项个数

    '''
    需为最后一次运行留下足够的时间，如120小时,为了后续方便，将timerun 扩充5天
    '''
    year=getyear(dir_met)      # 从up文件获取时间
    timerun=pd.date_range(start=str(year)+'0102',end=str(year)+'1230',freq='5D')
    timepy=timerun.to_pydatetime()
    timepy=np.append(timepy,pd.to_datetime('2020-12-30').to_pydatetime())
    # 此处截止到30号，计算中可直接加1
    time_mod=datetime.timedelta(days=1)

    num_puff=len(timepy)-1  # cpuff.inp文件个数
    puff_day=5

    fn_metout=glob.glob(dir_metout+'\\*.DAT')   # metout文件夹获取met.dat文件列表
    fn_metout.sort()

    if len(fn_metout)<1:
        fn_metout=[]  # 一般应从文件夹中获取met文件列表
        for i in range(num_puff):
            temp1=dir_metout+'\\cmet%03d.dat'%(i+1)
            fn_metout.append(temp1)


    #通过循环，依次修改相关变量，与时间相关的参量
    timewordb=['(IBYR)','(IBMO)','(IBDY)','(IBHR)','(IBMIN)','(IBSEC)']
    timeworde=['(IEYR)','(IEMO)','(IEDY)','(IEHR)','(IEMIN)','(IESEC)']

    for index in range(num_puff):

        info1=copy.deepcopy(info)
        # 依次修改输出文件和lst文件
        info1=str_replace(info1,'PUFLST',dir_puffout+'\\CPUFF%04d.LST'%(index+1))
        info1=str_replace(info1,'CONDAT',dir_puffout+'\\CPUFF%04d.CON'%(index+1))


        # 修改源项文件
        info1=str_replace(info1,'PTDAT  =',dir_release+'\\ptemarb.dat')

        # none   input   ! METDAT= **!  !END!
        # 模拟开始对应的天数，注意met001实际从第一年的二天开始,数组从0开始

        start1=timepy[index].timetuple().tm_yday
        fn_metout1=fn_metout[start1-2:start1+puff_day-1]  #需要比puff_day多一天
        fn_metout2=copy.deepcopy(fn_metout1)

        # 修改气象文件数目
        info1=str_replace(info1,'NMETDAT =',"{:2d}".format(len(fn_metout2)))
        for i,line in enumerate(fn_metout1):
            fn_metout2[i]='none   input   ! METDAT= '+line+' !  !END!'

        info1=insert(info1, 'Subgroup (0a)',fn_metout2,6)

        timeb=timepy[index].strftime('%Y %m %d %H %M %S').split()
        timee=(timepy[index+1]+time_mod).strftime('%Y %m %d %H %M %S').split()

        for j in range(6):
            info1=str_replace(info1,timewordb[j],timeb[j])
            info1=str_replace(info1,timeworde[j],timee[j])
        # 将修改后的inp文件输出
        print_inp(dir_puffinp,'CPUFF%04d.INP'%(index+1),info1)

    print('calpuff输入文件生成完成用时:%.2f'% (time.time()-s))

    s=time.time()
    print('calpuff计算开始 %s'%time.strftime('%Y-%m-%d %H:%M:%S'))
    # #并行计算
    fnames = glob.glob(dir_puffinp+'\\*.inp')

    max_cpu = min(os.cpu_count ()//2,60)      # 定义cpu核数

    with Pool(max_cpu) as p:
        p.map(partial(run_puff1, dir_puffout=dir_puffout,\
                      dir_exe=dir_sys['dir_exe']), fnames)

    # # 单进程计算
    # for fname in fnames:
    #     run_puff1(fname, dir_puffout, dir_exe=dir_sys['dir_exe'])

    print('calpuff计算用时:%5.1f'% (time.time()-s))




