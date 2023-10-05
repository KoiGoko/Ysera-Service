# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 15:04:00 2022
@author: xinjian"""

import xarray as xr
import datetime
import time,os,yaml,glob
import pandas as pd
import numpy as np
from multiprocessing import Pool,shared_memory
from functools import partial
from multiprocessing.managers import SharedMemoryManager

#***********************************************************
def read_source(dir_source):
    """
    读取事故源项
    """
    # dir_source=r'E:\examples\xzs\7source\source_hualong.xlsx'
    source=pd.read_excel(io=dir_source,sheet_name=None)
    sname=list(source.keys())
    for sname1 in sname:
        tempdf=source[sname1]
        tempdf=tempdf.sort_values(by=tempdf.columns[0])
        tempdf.index=range(len(tempdf))
        source[sname1]=tempdf

    return source


def read_DCF(dir_DCF):
    '''
    #读入挑选的剂量转换因子文件，分别读入沉积速率、衰变常数和DCF
    # 根据需要，目前暂考虑3种急性剂量
    '''

    myDCF=pd.read_csv(dir_DCF)

    vg=np.array(myDCF['Vg(m/s)']).astype(np.float32)
    lamta=np.array(myDCF['lamta(1/h)']).astype(np.float32)
    DCFinp=np.array(myDCF.loc[:,['air','ground','inhaled','thyroid',
                             'red_marr','lungs','skin']]).astype(np.float32)

    return DCFinp,vg,lamta

def cal_dcf2(source1,DCF_inp,vg1):
    '''
    将剂量转换因子根据源项数据进行合并,依次为
    air,grd,in,th,red,lung,skin
    输出将air,grd,in合并为eff
    '''
    br=2.3e-4;
    (nnuclide,nts) = np.shape(source1)

    DCF2=np.zeros([7,nnuclide,nts])    # 用于保存核素合并的DCF
    for k in range(7):
        for i in range(nts):
            if k==0 or k==6:
                DCF2[k,:,i]= DCF_inp[:,k]*source1[:,i]
            elif k==1:
                DCF2[k,:,i]= DCF_inp[:,k]*source1[:,i]*vg1[:]*(168-i+1)
            else:
                DCF2[k,:,i]= DCF_inp[:,k]*source1[:,i]*br

    #对核素求和，变成只随时间变化的一维数组
    DCF_eff=DCF2[:3].sum(axis=(0,1))
    DCF_th=DCF2[3].sum(0)
    DCF_red=DCF2[4].sum(0)
    DCF_lung=DCF2[5].sum(0)
    DCF_skin=DCF2[6].sum(0)

    return (DCF_eff,DCF_th,DCF_red,DCF_lung,DCF_skin)


def read_xqa(dir_xqs):
    """
    读入整年大气弥散因子，并转换为cp数组
    """
    with xr.open_mfdataset(dir_xqs,concat_dim='t',combine='nested') as ds:
        # print(ds)
        xq=ds['KR-85'].values
        xygrid=ds['XYGRID'].values
        xqtime=ds['TIME'].values

    return xq,xqtime,xygrid[0,:]


def cal_dose_1(index,DCF_input,par):
    '''
    基于单个事故源项，计算对应时间段的剂量，DCF_input为元组
    里面包含一个或者多个剂量转换因子，可以计算对应器官/途径的剂量

    par 为list，给出xqa的数组维度，数据类型，共享内存名称
    '''

    DCFs=list(DCF_input)
    no=len(DCFs)    # 计算剂量种类（器官）数目 num organ
    nts=np.shape(DCFs[0])[0]

    # 共享内存变量的处理
    shape_arr1,dtype_arr1,name1=par[0],par[1],par[2]

    shm2 = shared_memory.SharedMemory(name=name1, create=False)
    # Create the np.ndarray from the buffer of the shared memory
    xqshare = np.ndarray(shape_arr1, dtype_arr1, buffer=shm2.buf)

    xq1=xqshare[index:index+nts,...]
    ny,nx=np.shape(xq1)[1:]

    # shm2.close()      # 共享内存关闭

    # 一次抽样的剂量计算数组，器官，时间，ny，nx
    Dose1=np.zeros([no,nts,ny,nx]).astype(np.float32)

    # 将每种类型的剂量转换因子进行维度扩充，变成三维数组
    for i in range(no):
        DCFs[i]=np.expand_dims(DCFs[i],axis=(1,2))
        Dose1[i,:,:,:]=xq1*DCFs[i]

    # 对所有时段的剂量进行时间求和
    Dose_sum = Dose1.sum(1)
    return Dose_sum


def save_dose(dose,dir_out1,acute=None):

    # 定义时间序列
    start1='%4d%03d%02d'%(tuple(xqtime[0,:3]))
    start1=datetime.datetime.strptime(start1,"%Y%j%H")
    nt=len(range(0, nta-nts,3))
    mytime=pd.date_range(start=start1,periods=nt,freq='3H')

    # 定义x，y
    x1=np.linspace(xygrid[4],-xygrid[4],int(xygrid[0]*xygrid[-1]-1)).astype('float32')
    y1=np.linspace(xygrid[5],-xygrid[5],int(xygrid[1]*xygrid[-1]-1)).astype('float32')

    dname=['dose_eff','dose_th','dose_red','dose_lung','dose_skin']

    dsout=xr.Dataset(
        coords=dict(
            lon=(['x'],x1),
            lat=(['y'],y1),
            time=mytime,
            ),
        attrs=dict(description='eff dose and th dose')
        )

    for i in range(np.shape(dose)[0]):
        dsout[dname[i]]=(['time','y','x'],dose[i,:,:,:])

    dsout.to_netcdf(dir_out1)

    return

if __name__ == '__main__':

    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    dir_run=os.path.join(dir_sys['dir_out0'],grd['title'])

    dir_out=os.path.join(dir_run,'8dose')

    """
    读取剂量转换因子，vg，lamta，对DCF进行初步计算
    """
    s=time.time()
    print('剂量计算程序开始执行! %s'% time.strftime('%Y-%m-%d %H:%M:%S'))

    dir_source=glob.glob(os.path.join(dir_run,'7source','*sour*.xlsx'))[0]
    source=read_source(dir_source)
    sname=list(source.keys())
    source0=np.array(source[sname[0]].iloc[:,1:]).astype(np.float32)
    nts=np.shape(source0)[1]    # 源项对应的小时数，num_time_source


    dir_DCF=glob.glob(os.path.join(dir_run,'7source','selectDCF.csv'))[0]
    (DCFinp,vg,lamta)=read_DCF(dir_DCF)

    """
    获取大气弥散因子列表，初始化剂量数组
    """
    dir_xq=glob.glob(os.path.join(dir_run,'6xq','*.nc'))
    dir_xq.sort()
    xqa,xqtime,xygrid=read_xqa(dir_xq)   # 获取整年大气弥散因子

    """
    获取数组网格，抽样次数等信息
    """
    (nta,ny,nx)=np.shape(xqa)
    nt=int((nta-nts)/3) # 抽样后计算次数
    max_cpu = min(os.cpu_count()//2,60)      # 定义cpu核数

    # 将整年大气弥散因子数据设置为共享内存，子进程可以使用
    with SharedMemoryManager() as smm:

        # 开辟共享内存空间 大小等于numpy数组字节大小
        shm_xq = smm.SharedMemory(size=xqa.nbytes)
        # 在共享内存空间当中创建numpy数组
        shm_arr1 = np.ndarray(xqa.shape, dtype=xqa.dtype, buffer=shm_xq.buf)

        # 拷贝xqa数组 到共享内存空间当中创建的数组
        np.copyto(shm_arr1, xqa)

        with Pool(max_cpu) as p:
            for i in range(len(source)):
                #1 定义输出文件名称
                outfile1='dose%(i)02d.nc'%{'i':i+1}
                source1=np.array(source[sname[i]].iloc[:,1:]).astype(np.float32)

                #2 处理剂量转换因子
                myDCF2=cal_dcf2(source1,DCFinp,vg)
                if grd['acutedose']!=1:
                    calDCF=myDCF2[:2]
                else:
                    calDCF=myDCF2

                #3 生成循环的序列，并行计算剂量
                index1=range(0, nta-nts,3)
                dose1=p.map(partial(cal_dose_1,DCF_input=calDCF,
                                    par=[xqa.shape,xqa.dtype,shm_xq.name]),index1)

                dose1=np.asarray(dose1).transpose(1,0,2,3)
                save_dose(dose1,os.path.join(dir_out, outfile1))

                print('源项剂量计算完成,用时：%.2fs!'% (time.time()-s))
