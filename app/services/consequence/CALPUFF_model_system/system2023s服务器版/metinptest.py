# coding=UTF8
'''
对calmetInp文件进行批量修改并运行
by  liuxinjian 2022.06.26
'''
from functools import partial
import os,glob,copy
import time
import pandas as pd
from multiprocessing import Pool
from os import path
import yaml


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


def str_insert(info, keystr, insert_list,*args):
    '''
    将info包含关键字keystr的字符串位置，插入新的list，并可灵活设置偏移行数
    '''
    offset=(0 if len(args)==0 else args[0])   # 偏移行数初始化

    for i in range(len(info)):  # 寻找插入的位置
        if keystr in info[i]:
            break

    for line1 in insert_list:       # 循环插入内容
        if not line1.endswith('\n'):
            line1=line1+'\n'

        info.insert(i+offset,line1)
        i+=1
    return info

def mapgrd(info,grd):
    '''
    对地图投影信息进行更新，共9个参数
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

    return info

def print_inp(dir_out,fname,info):
    '''
    dir_out，fnames 输出的目录和文件名(可多个)
    info：输出的内容，list形式
    '''
    with open(dir_out + '\\' + fname, 'w') as f:
            for line in info:
                if not line.endswith('\n'):
                     line=line+'\n'
                f.write(line)
    return


def run_met1(fname, dir_metinp, dir_metout, dir_exe):
    '''
    输入一个calmet.inp的名字，目录等信息，执行一个算例
    '''
    command = dir_exe + '\\calmetl.exe ' + path.join(dir_metinp, fname)
    while True:
        os.system(command)
        with open(path.join(dir_metout, fname[0:8] + "lst"), 'r') as f:
            content = f.readlines()[-1]
            if "CPU" in content:
                break
    return

def getyear(dir_met):    # 从up文件获取年份
    with open(dir_met+'\\up101n.dat') as f:
        for i in range(6):
            temp=f.readline()
        return int(temp[0:6])

def getfileinfo(dir_met):
    '''
      读取geo.dat，up.dat,surf.dat的列表
      读取upinfo.txt和surfinfo.txt中的信息,
    '''
    geofile=glob.glob(dir_met+'\\ge*.dat')
    fn0=glob.glob(dir_met+'\\up*.dat')
    upfiles=[]
    for i in range(len(fn0)):
        temp='UP'+str(i+1)+'.DAT'+'     input    ' + str(i+1)+\
            '  ! UPDAT='+ fn0[i] + ' !  !END!'+'\n'
        upfiles.append(temp)

    surffile=glob.glob(dir_met+'\\surf*.dat')

    fn1=glob.glob(dir_met+'\\up*.txt')
    with open(fn1[0]) as f:
        upinfo=f.readlines()

    fn2=glob.glob(dir_met+'\\sur*.txt')
    with open(fn2[0]) as f:
        surfinfo=f.readlines()

    return geofile,upfiles,upinfo,surffile,surfinfo


if __name__ == '__main__':
    s=time.time()
    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    # 读入原始calmet.inp文件
    with  open(path.join(dir_sys['dir_model'],'cmet-ori.inp')) as f:
        info=f.readlines()

    #修改投影和网格信息
    info=mapgrd(info,grd)

    # 修改时区
    info=str_replace(info,' (ABTZ)','UTC+0800')
    '''
    对目录和时间等参数初始化
    '''
    dir_run=os.path.join(dir_sys['dir_out0'],grd['title'])
    dir_met=path.join(dir_run,'1geomet')
    dir_metinp=path.join(dir_run,'2metinp')
    dir_metout=path.join(dir_run,'3metout')

    fn_metout=glob.glob(dir_metout+'\\*.inp')

    # 从up文件获取年份，并生成整年时间序列
    year=getyear(dir_met)

    timerun=pd.date_range(start=str(year)+'0102',end=str(year)+'1231',freq='D')
    timepy=timerun.to_pydatetime()

    num_met=len(timepy)  # cmet.inp文件个数

    (geofile,upfiles,upinfo,surffile,surfinfo)=getfileinfo(dir_met)


    info = str_replace(info,'GEO.DAT',geofile[0])
    info = str_replace(info,'SRFDAT',surffile[0])

    info = str_replace(info,'(NUSTA)',str(len(upfiles)))
    info = str_replace(info,'(NSSTA)',str(len(surfinfo)))

    #依次插入探空，地面文件信息
    info=str_insert(info, 'Subgroup (b)', upfiles,6)
    info=str_insert(info, 'INPUT GROUP: 7', surfinfo,10)
    info=str_insert(info, 'INPUT GROUP: 8', upinfo,9)

    # 循环修改时间，输出文件，并输出
    timewordb=['(IBYR)','(IBMO)','(IBDY)','(IBHR)','(IBSEC)']
    timeworde=['(IEYR)','(IEMO)','(IEDY)','(IEHR)','(IESEC)']

    for i in range(num_met-1):
        info1=copy.deepcopy(info)

        info1=str_replace(info1,'METLST',dir_metout+'\\CMET%03d.LST'%(i+1))
        info1=str_replace(info1,'METDAT',dir_metout+'\\CMET%03d.DAT'%(i+1))

        timeb=timepy[i].strftime('%Y %m %d %H %S').split()
        timee=timepy[i+1].strftime('%Y %m %d %H %S').split()

        for j in range(5):
            info1=str_replace(info1,timewordb[j],timeb[j])
            info1=str_replace(info1,timeworde[j],timee[j])

        # 将修改后的inp文件输出
        print_inp(dir_metinp,'CMET%03d.INP'%(i+1),info1)

    # 并行计算
    fnames = os.listdir(dir_metinp)

    # max_connections = os.cpu_count()//2
    with Pool(8) as p:
        p.map(partial(run_met1, dir_metinp=dir_metinp,\
                      dir_metout=dir_metout,dir_exe=dir_sys['dir_exe']), fnames)

    print(time.time()-s)





