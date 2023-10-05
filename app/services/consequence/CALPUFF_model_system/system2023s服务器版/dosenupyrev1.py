# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 15:04:00 2022

@author: xinjian"""

import xarray as xr
import datetime
import time,os,yaml,glob
import pandas as pd
import numpy as np

#***********************************************************
def read_source(dir_source):
    """
    读取事故源项
    """
    source=pd.read_excel(io=dir_source,sheet_name=None)
    sname=list(source.keys()) 
    for sname1 in sname:
        tempdf=source[sname1]
        tempdf=tempdf.sort_values(by='nuclides')
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
    将剂量转换因子根据源项数据进行合并
    '''
    br=2.3e-4;
    (nnuclide,nts) = np.shape(source1)
    
    # 用于保存核素合并的DCF
    DCF2_air,DCF2_grd,DCF2_in,DCF2_th=4*[np.zeros_like(source1)]
    
    DCF2_red,DCF2_lung,DCF2_skin=3*[np.zeros_like(source1)]

    '''
    后续可考虑改为数组乘法，不用循环
    '''
    for i in range(nts):
        DCF2_air[:,i]= DCF_inp[:,0]*source1[:,i]
        DCF2_grd[:,i]= DCF_inp[:,1]*source1[:,i]*vg1[:]*(168-i+1)
        DCF2_in[:,i] = DCF_inp[:,2]*source1[:,i]*br
        DCF2_th[:,i] = DCF_inp[:,3]*source1[:,i]*br

        # 急性剂量对应的DCF
        DCF2_red[:,i]= DCF_inp[:,4]*source1[:,i]*br
        DCF2_lung[:,i]= DCF_inp[:,5]*source1[:,i]*br
        DCF2_skin[:,i]= DCF_inp[:,6]*source1[:,i]
 
    #对核素求和，变成只随时间变化的一维数组
    DCF_eff=DCF2_air.sum(0)+DCF2_grd.sum(0)+DCF2_in.sum(0)
    DCF_th=DCF2_th.sum(0)
    
    DCF_red=DCF2_red.sum(0)
    DCF_lung=DCF2_lung.sum(0)
    DCF_skin=DCF2_skin.sum(0)
       
    return DCF_eff,DCF_th,DCF_red,DCF_lung,DCF_skin

def read_xq(dir_xq):
    """
    读入整年的大气弥散因子，并转换为cp数组
    """
   
    with xr.open_mfdataset(dir_xq,concat_Rdim='t',combine='nested') as ds:
        xq=ds['KR-85'].data
        # xq=np.array(xq)
        xygrid=ds['XYGRID'].data[0,:].compute()
        xqtime=ds['TIME'].data.compute()
        print(ds)
        
    return xq,xqtime,xygrid


def dose_cal(source1,xq,xqtime,xygrid,DCF_eff,DCF_th,dir_out,outfile):
    '''
    基于单个事故源项，计算对应剂量，并输出结果文件
    '''
    s=time.time()
    nts=np.shape(source1)[1]     # 源项对应的小时数，num_time_source
    dt=3
    (nty,ny,nx)=np.shape(xq)    # 整年弥散因子数据
    nt=int((nty-nts)/dt) # 抽样后计算次数
    
    # 一次抽样的剂量计算数组
    Dose1_eff=np.zeros([nts,ny,nx]).astype(np.float32)
    Dose1_th=np.zeros([nts,ny,nx]).astype(np.float32)
    
    # 全年抽样的剂量数组
    Dose_eff1= np.zeros([nt,ny,nx]).astype(np.float32)
    Dose_th1 = np.zeros([nt,ny,nx]).astype(np.float32)
    
    
    # 将剂量转换因子进行扩充，变成三维数组
    
    DCF1_eff=np.expand_dims(DCF_eff,axis=(1,2))
    DCF1_eff=np.tile(DCF1_eff,(1,ny,nx))
    
    DCF1_th=np.expand_dims(DCF_th,axis=(1,2))
    DCF1_th=np.tile(DCF1_th,(1,ny,nx))

    
    for k in np.arange(nt):
        kk=k*dt
        xq1=xq[kk:nts+kk,:,:]    
    
        Dose1_eff=xq1*DCF1_eff
        Dose1_th=xq1*DCF1_th
        
        # 对120小时的剂量进行时间和途径叠加求和
        Dose_eff1[k,:,:]= Dose1_eff.sum(0)
        Dose_th1[k,:,:] = Dose1_th.sum(0)
    
    
    # # 将计算结果输出到文件
    # Dose_eff1 = np.float32(np.asnumpy(Dose_eff1))
    # Dose_th1  = np.float32(np.asnumpy(Dose_th1))
    
    # 定义时间
    start1=str(xqtime[0,0])+'%(day)03d'%{'day':xqtime[0,1]}+'%(hour)02d'%{'hour':xqtime[0,2]}
    freq1='%(dt)dH'%{'dt':dt}
    start1=datetime.datetime.strptime(start1,"%Y%j%H")
    mytime=pd.date_range(start=start1,periods=nt,freq=freq1)
    
    # 定义x，y
    x1=np.linspace(xygrid[4],-xygrid[4],int(xygrid[0]*xygrid[-1]-1))
    y1=np.linspace(xygrid[5],-xygrid[5],int(xygrid[1]*xygrid[-1]-1))
    
    dsout=xr.Dataset(
        data_vars=dict(
            dose_eff=(['time','y','x'],Dose_eff1),
            dose_th=(['time','y','x'],Dose_th1),
            ),
        coords=dict(
            lon=(['x'],x1),
            lat=(['y'],y1),
            time=mytime,
            ),
        attrs=dict(description='eff dose and th dose')
        )
    
    dsout.to_netcdf(os.path.join(dir_out,outfile))    
    
    e = time.time()
    print('time for calculating:%(time).2f'%{'time':e-s})
    return


def acutedose_cal(source1,xq,xqtime,xygrid,DCF_red,DCF_lung,DCF_skin,dir_out,outfile):
    '''
    基于单个事故源项，计算对应剂量，并输出结果文件
    '''
    s=time.time()
    nts=np.shape(source1)[1]     # 源项对应的小时数，num_time_source
    dt=3
    (nty,ny,nx)=np.shape(xq)    # 整年弥散因子数据
    nt=int((nty-nts)/dt) # 抽样后计算次数
    
    # 一次抽样的剂量计算数组
    Dose1_red=np.zeros([nts,ny,nx]).astype(np.float32)
    Dose1_lung=np.zeros([nts,ny,nx]).astype(np.float32)
    Dose1_skin=np.zeros([nts,ny,nx]).astype(np.float32)
    
    # 全年抽样的剂量数组

    Dose_red1= np.zeros([nt,ny,nx]).astype(np.float32)
    Dose_lung1 = np.zeros([nt,ny,nx]).astype(np.float32)
    Dose_skin1= np.zeros([nt,ny,nx]).astype(np.float32)
    
    # 将剂量转换因子进行扩充，变成三维数组
    
    DCF1_red=np.expand_dims(DCF_red,axis=(1,2))
    DCF1_red=np.tile(DCF1_red,(1,ny,nx))
    
    DCF1_lung=np.expand_dims(DCF_lung,axis=(1,2))
    DCF1_lung=np.tile(DCF1_lung,(1,ny,nx))
    
    DCF1_skin=np.expand_dims(DCF_skin,axis=(1,2))
    DCF1_skin=np.tile(DCF1_skin,(1,ny,nx))

    
    for k in np.arange(nt):
        kk=k*dt
        xq1=xq[kk:nts+kk,:,:]    
    
        Dose1_red=xq1*DCF1_red
        Dose1_lung=xq1*DCF1_lung
        Dose1_skin=xq1*DCF1_skin  
        
        # 对120小时的剂量进行时间和途径叠加求和
        Dose_red1[k,:,:]= Dose1_red.sum(0)
        Dose_lung1[k,:,:] = Dose1_lung.sum(0)
        Dose_skin1[k,:,:] = Dose1_skin.sum(0)
    
    
    # 将计算结果输出到文件
    # Dose_red1 = np.float32(np.asnumpy(Dose_red1))
    # Dose_lung1  = np.float32(np.asnumpy(Dose_lung1))
    # Dose_skin1  = np.float32(np.asnumpy(Dose_skin1))
    
    # 定义时间
    start1=str(xqtime[0,0])+'%(day)03d'%{'day':xqtime[0,1]}+'%(hour)02d'%{'hour':xqtime[0,2]}
    freq1='%(dt)dH'%{'dt':dt}
    start1=datetime.datetime.strptime(start1,"%Y%j%H")
    mytime=pd.date_range(start=start1,periods=nt,freq=freq1)
    
    # 定义x，y
    x1=np.linspace(xygrid[4],-xygrid[4],int(xygrid[0]*xygrid[-1]-1))
    y1=np.linspace(xygrid[5],-xygrid[5],int(xygrid[1]*xygrid[-1]-1))
    
    dsout=xr.Dataset(
        data_vars=dict(
            dose_red=(['time','y','x'],Dose_red1),
            dose_lung=(['time','y','x'],Dose_lung1),
            dose_skin=(['time','y','x'],Dose_skin1),
            ),
        coords=dict(
            lon=(['x'],x1),
            lat=(['y'],y1),
            time=mytime,
            ),
        attrs=dict(description='acute dose')
        )
    
    dsout.to_netcdf(os.path.join(dir_out,outfile))    
    e = time.time()
    print('time for calculating:%(time).2f'%{'time':e-s})
    return

if __name__ == '__main__':


    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)
        
    with  open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    dir_run=os.path.join(dir_sys['dir_out0'],grd['title'])
    
    """
    读取剂量转换因子，vg，lamta，对DCF进行初步计算
    """   
    s=time.time()
    dir_source=glob.glob(os.path.join(dir_run,'7source','*sour*.xlsx'))[0]
    source=read_source(dir_source)
    sname=list(source.keys())    
        
    dir_DCF=glob.glob(os.path.join(dir_run,'7source','selectDCF.csv'))[0]   
    (DCFinp,vg,lamta)=read_DCF(dir_DCF)
    
    dir_xq=glob.glob(os.path.join(dir_run,'6xq','*.nc'))
    dir_xq.sort()
    (xq,xqtime,xygrid)=read_xq(dir_xq)
    e = time.time()
    print('time for reading:%(time).2f'%{'time':e-s})
    dir_out=os.path.join(dir_run,'8dose')

    
    for i in range(len(source)):
        outfile1='dose%(i)02d.nc'%{'i':i+1}
        outfile2='acutedose%(i)02d.nc'%{'i':i+1}       
        source1=np.array(source[sname[i]].iloc[:,1:]).astype(np.float32)
        source1=np.array(source1)        
        (DCF_eff,DCF_th,DCF_red,DCF_lung,DCF_skin)=cal_dcf2(source1,DCFinp,vg)
        dose_cal(source1,xq,xqtime,xygrid,DCF_eff,DCF_th,dir_out,outfile1)
        
        if grd['acutedose']==1:
            acutedose_cal(source1,xq,xqtime,xygrid,DCF_red,DCF_lung,DCF_skin,dir_out,outfile2)
    



