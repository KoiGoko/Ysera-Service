# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 10:12:30 2022

@author: xinjian

"""
from multiprocessing import Pool
from functools import partial
import numpy as np
import xarray as xr
import pandas as pd
import io,os
import yaml,time

# 定义函数，返回对应分辨率的经纬度，要求x1 小于 x2
def myint(x1,x2,res):
    return int(x1/res)*res,np.ceil(x2/res)*res


# 自定义函数，从较大的nc数据返回一定范围内的数值，形成新的nc文件
def readnc1(fname,dir_in,top,down,left,right,subname,keywords):
    """
    尝试读取nc文件部分数据,每次执行一个文件
    """
    with  xr.open_dataset(os.path.join(dir_in,subname,fname)) as ds1:
        ds2=ds1[keywords].loc[:,500:1000,top:down,left:right]
        # print(ds2)
        data1=ds2[:,:,:,:].values
        time1=ds2.time.values
        data={keywords:data1,'time':time1}
        del ds2
    return data

    #ds2.to_netcdf(os.path.join(dir_out,fname))
    # del ds2


def printup1(fname1,dir_out,timepy,level,z,t,wd,ws):
    '''
    Parameters
    ----------
    fname1 : 单个up文件名称
    dir_out: 文件输出努力
    timepy : 时间，py类型
    level、z 、t、wd、ws： 所有输出的np数组

    '''
    nlat=np.shape(z)[-2]
    nlon=np.shape(z)[-1]
    nh=len(level)
    stn_id = np.arange(2001,2001+nlat*nlon)

    up_format1='   %6.1f/%5.0f/%5.1f/%3i/%3i'
     #创建循环所需的经纬度矩阵列表
    ilatlon=[]
    for ilat in range(0,nlat):
         for ilon in range(0,nlon):
          ilatlon.append([ilat,ilon])

    #循环中的经纬度,根据fname1确定i的值
    i=int(fname1[2:5])-101
    jlat = ilatlon[i][0]
    jlon = ilatlon[i][1]

    f=io.StringIO()
    f.write('UP.DAT'+' '*10+'2.1'+' '*17+'Hour Start and End Times with Seconds' + "\n")
    f.write('   1'+ "\n")
    f.write('Produced by READ62 Version: 5.641  Level: 080407'+ "\n")
    f.write('NONE'+ "\n")
    f.write('UTC+0000'+ "\n")
    f.write((' '+'%5d'*8+'%5.0f%5d%5d') %(timepy[0].year,timepy[0].timetuple().tm_yday,timepy[0].hour,timepy[0].second,
                                          timepy[-1].year,timepy[-1].timetuple().tm_yday,timepy[-1].hour,
                                          timepy[-1].second,500,2,1)+"\n")
    f.write(' '+'    F'+'    F'+'    F'+'    F'+"\n")

    #时间循环
    for itime in range(len(timepy)):
        f.write('   '+'6201'+'  %8i'%stn_id[i]+('    %4i%4i%3i%3i%5i'*2)
                 %(timepy[itime].year,timepy[itime].month,timepy[itime].day,timepy[itime].hour,
                   timepy[itime].second,timepy[itime].year,timepy[itime].month,
                   timepy[itime].day,timepy[itime].hour,timepy[itime].second) +
                '  %5i' %nh+' %5i'%nh+'\n')    #写每一时刻的表头
        for ilevel in range(1,nh+1):
            f.write(up_format1 %(level[nh-ilevel],z[itime,nh-ilevel,jlat,jlon],t[itime,nh-ilevel,jlat,jlon],
                                 wd[itime,nh-ilevel,jlat,jlon],ws[itime,nh-ilevel,jlat,jlon]))
            if np.mod(ilevel,4)==0 or ilevel==nh:
                f.write('\n')
    with open(dir_out+'\\'+fname1,"w",encoding='utf8') as file:
        file.write(f.getvalue())
        

if __name__ == '__main__':

    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    dir_run=os.path.join(dir_sys['dir_out0'],grd['title'])

    dir_in=dir_sys['dir_ERA5']
    dir_out=os.path.join(dir_run,'1geomet')

    print('探空数据处理程序开始执行! %.2f'%time.time())

    (lat0,lon0,nx,ny,dx)=[grd['lat0'],grd['lon0'],grd['nx'],grd['ny'],grd['dx']]

    #为保证探空数据总数不超过99，每个方位最多9个点
    res = 0.25
    ry=min(ny*dx/2/110,res*4-0.05)
    rx=min(nx*dx/np.cos(np.pi*lat0/180)/110/2,res*4-0.05)

    top,down = lat0+ry,lat0-ry
    left,right = lon0-rx,lon0+rx

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


    with open(dir_out+'\\upinfo.txt','wt') as f:
        for i in range(1,nsta+1):
            f.write(('! US'+'%1d'+' ='+"'U%03d'"+'    %4d'+' %8.1f'+'%8.1f') %(i%10,i,2000+i,xy[i-1,0],xy[i-1,1]))
            f.write(('%8d !\n') %(-8))


    namelist=['u_component_of_wind','v_component_of_wind','temperature','geopotential']
    variable=['u','v','t','z']

    max_connections = min(os.cpu_count () //2,48)
    
    outlist=[[]]*4


    for index in range(len(namelist)):
        keywords=variable[index]
        fnames=os.listdir(os.path.join(dir_in,namelist[index]))

        with Pool(max_connections) as p:
            x=p.map(partial(readnc1,dir_in=dir_in,
                          top=top,down=down,left=left,right=right,
                          subname=namelist[index],keywords=keywords ),fnames)
        outlist[index]=x
        
    print('探空数据提取完成! %.2f'%time.time())
    
    ndim=[len(outlist[0])*24]
    ndim.extend(outlist[0][0]['u'].shape[1:])

    for i in range(4):  # 循环读取四个变量，并叠加为一个数组
        out=np.zeros(ndim,dtype='float32')
        for j in range(len(outlist[0])):
            temp=outlist[i][j][variable[i]]
            out[j*24:j*24+24,:,:,:]=temp
        locals()[variable[i]]=out
    z=z/9.8

    # 单独处理level
    with  xr.open_dataset(os.path.join(dir_in,namelist[-1],fnames[0])) as ds1:
        level=ds1['level'].values
        level=level[level>=500]
    # 对数据的时间进行叠加，并将时间转为np格式
    time_np=np.zeros(ndim[0],dtype='datetime64[s]')
    for j in range(len(outlist[0])):
        temp=outlist[0][j]['time'].astype('datetime64[s]')
        time_np[j*24:j*24+24]=temp

    time_pd = pd.to_datetime(time_np)
    timepy = time_pd.to_pydatetime()

    # caculate wind direction
    wd =  180.0 + np.arctan2(u, v)*180/np.pi
    # caculate wind speed
    ws = np.sqrt(u**2+v**2).astype(int)

    print('数据转换完成! %.2f'%time.time())
    ##输出
    upfnames = []
    for i in range(nsta):
          upfnames.append('up'+str(101+i)+'n.dat')
          
    # for i in range(nsta):
    #       upfname='up'+str(101+i)+'n.dat'
    #       printup1(upfname,dir_out,timepy,level,z,t,wd,ws)
    
    with Pool(8) as p:
              p.map(partial(printup1,dir_out=dir_out,timepy=timepy,
                            level=level,z=z,t=t,wd=wd,ws=ws),upfnames)

    print('数据输出完成! %.2f'%time.time())

