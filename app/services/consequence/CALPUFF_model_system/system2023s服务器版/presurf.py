# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 11:57:06 2022

@author: xinjian
"""

from multiprocessing import Pool
from functools import partial
import shutil
import numpy as np
import xarray as xr
import pandas as pd
import os,io
import yaml,time,datetime

# 定义函数，返回对应分辨率的经纬度，要求x1 小于 x2
def myint(x1,x2,res):
    return int(x1/res)*res,np.ceil(x2/res)*res

# 自定义函数，从较大的nc数据返回一定范围内的数值，形成新的nc文件
def readnc1(fname,dir_in,dir_out,top,down,left,right):
    """
    尝试读取nc文件部分数据,每次执行一个文件
    """ 
    keywords=fname.split('#')[1]
    fname0=fname.split('#')[0]
    with  xr.open_dataset(os.path.join(dir_in,fname0)) as ds1:
        ds2=ds1[keywords].loc[:,top:down,left:right]
        ds2.to_netcdf(os.path.join(dir_out,fname0))
    del ds2
    
    
    
if __name__ == '__main__':
    
    print('地面气象数据准备程序开始执行! %.2f'%time.time())
    
    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)
        
    with  open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    dir_run=os.path.join(dir_sys['dir_out0'],grd['title'])
        
    dir_in=dir_sys['dir_ERA5']+'\\surfdata'
    dir_out=os.path.join(dir_run,'1geomet')        

                
    (lat0,lon0,nx,ny,dx)=[grd['lat0'],grd['lon0'],grd['nx'],grd['ny'],grd['dx']]
          
    dir_temp=os.path.join(dir_out,'temp')
    if not os.path.exists(dir_temp):
        os.makedirs(dir_temp)     
     
    res = 0.25
    top  = lat0+ny*dx/2/110
    down = lat0-ny*dx/2/110
    left = lon0-nx*dx/np.cos(np.pi*top/180)/110/2
    right= lon0+nx*dx/np.cos(np.pi*top/180)/110/2
    
     # 将经纬度靠近0.25度的数值
    (down,top)=myint(down, top, res)
    (left,right)=myint(left,right,res)
     
     # 产生序列，循环计算距离
    nlon=round((right-left)/res)+1
    nlat=round((top-down)/res)+1     
    
    nsta = nlon*nlat
    stn_id = np.arange(2001,2001+nsta)
    
    xy=np.zeros((nsta,2))
    for j in range(nlat):
        for i in range(nlon):
            xy[j*nlon+i,0]=(left+i*res-lon0)*110*np.cos(np.pi*lat0/180)
            xy[j*nlon+i,1]=(top-j*res-lat0)*110
    


    ####地面的输出   ! SS1   ='S001'    2001       -6.4     6.9        -8    10  !
    with open(os.path.join(dir_out,'surfpara.txt'),'wt') as f:
        for i in range(1,nlon*nlat+1):
            f.write(('! SS'+'%1d'+' ='+"'S%03d'"+'    %5d'+' %8.1f'+'%8.1f') 
                    %(i%10,i,2000+i,xy[i-1,0],xy[i-1,1]))
            f.write(('%8d%8.1f !\n') %(-8,10))
    
     
    ncnames=['2m_temperature','10m_u','10m_v','cloud_base_height',
              'relative_humidity','surface_pressure','total_cloud_cover']
    variable=['t2m','u10','v10','cbh','r','sp','tcc']
    ncnames2=[]
    for  i in range(len(ncnames)):
        ncnames2.append(ncnames[i]+'.nc'+'#'+variable[i])
    
    # max_connections = os.cpu_count()//2      
    with Pool(7) as p:
        p.map(partial(readnc1,dir_in=dir_in,dir_out=dir_temp,  
              top=top,down=down,left=left,right=right),ncnames2)
        

    print('地面数据提取完成! %.2f'%time.time())    
    # #整合数据   
    u10_ds = xr.open_dataset(os.path.join(dir_temp,'10m_u.nc'))
    v10_ds = xr.open_dataset(os.path.join(dir_temp,'10m_v.nc'))
    t2m_ds = xr.open_dataset(os.path.join(dir_temp,'2m_temperature.nc'))
    sp_ds  = xr.open_dataset(os.path.join(dir_temp,'surface_pressure.nc'))
    rh_ds  = xr.open_dataset(os.path.join(dir_temp,'relative_humidity.nc'))
    tcc_ds = xr.open_dataset(os.path.join(dir_temp,'total_cloud_cover.nc'))
    cbh_ds = xr.open_dataset(os.path.join(dir_temp,'cloud_base_height.nc'))
    
    # 取出具体数值
    u = u10_ds.u10[:,:,:].values
    v = v10_ds.v10[:,:,:].values
    t2m = t2m_ds.t2m[:,:,:].values
    sp = sp_ds.sp[:,:,:].values/100
    
    # 针对个别算例进行数据质量控制，后续进行扩展
    sp[np.isnan(sp)]=900
    sp[sp<600]=900
    
    rh = rh_ds.r[:,:,:].values
    tcc =tcc_ds.tcc[:,:,:].values*10
    cbh = cbh_ds.cbh[:,:,:].values/0.3048/100  ##混合层厚度
    cbh[np.where(cbh<10)]=10
    cbh[np.isnan(cbh)]=40
    
    time_np = u10_ds.time.values
     
    # caculate wind direction
    wd =  180.0 + np.arctan2(u, v)*180/np.pi
    # caculate wind speed
    ws = np.sqrt(u**2+v**2)    
    
    tp=np.zeros(np.shape(ws))
    
    # 根据时区进行转换
    time_pd = pd.to_datetime(time_np)
    timebtc = time_pd.to_pydatetime()+datetime.timedelta(hours=8)
    
    del u10_ds,v10_ds,t2m_ds,sp_ds,rh_ds,tcc_ds,cbh_ds
    print('地面数据转换完成! %.2f'%time.time())
    
    shutil.rmtree(dir_temp)
    
#输出
    header_format='%6i%4i%4i%6i%6i%4i%4i%6i%5i\n'
    data_format1='%4i%4i%4i%5i   %4i%4i%4i%5i   \n'
    data_format2=' %8.3f %8.3f %4i %4i %8.3f %4i %8.3f %4i\n'

    f=io.StringIO()    
    f.write('SURF.DAT        2.1             Hour Start and End Times with Seconds' + "\n")  
    f.write('   1' + "\n")
    f.write('Produced by SMERGE Version: 5.651  Level: 080407' + "\n")
    f.write('NONE' + "\n")
    f.write('UTC+0800' + "\n")
    
    f.write(header_format %(timebtc[0].year,timebtc[0].timetuple().tm_yday,
                            timebtc[0].hour, timebtc[0].second,timebtc[-1].year,
                            timebtc[-1].timetuple().tm_yday,timebtc[-1].hour, 3600,nsta))
    for i in range(len(stn_id)):
          f.write('%8i\n' %(stn_id[i]))
          
    for k in range(len(timebtc)):
    
        f.write(data_format1 %(timebtc[k].year,timebtc[k].timetuple().tm_yday,timebtc[k].hour,0,
                                timebtc[k].year,timebtc[k].timetuple().tm_yday,timebtc[k].hour,3600))
        for m in range(nlat):
            for n in range(nlon):  
                f.write(data_format2 %(ws[k,m,n],wd[k,m,n],cbh[k,m,n],tcc[k,m,n],
                                        t2m[k,m,n],sp[k,m,n],rh[k,m,n],tp[k,m,n]))    

    with open(dir_out+'\\surfnew.dat',"w",encoding='utf8')  as file:
        file.write(f.getvalue())
        
    print('地面气象数据输出完成! %.2f'%time.time())
    

    
    
    
    