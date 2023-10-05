# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 15:04:00 2022

@author: xinjian"""

import xarray as xr
import datetime
import time,os,yaml,glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.colors as colors

#########################################################################

def read_uv(dir_uv,timeb,nhour=120):
    """
    程序用来读入风速分速分量，并转换为数组
    input：dir_uv，所有met文件列表，利用glob生成
           usertime，用户输入的时间，转为pd的时间
           nhour,读取met数据的长度，默认为120h
     output：数组，时间，网格
     
    为了更加精准匹配时间，将数组的挑选放在函数内
    后续可将met的输出序号直接改为日期，便于识别定位
    """
    
    timee=timeb+pd.Timedelta(hours=nhour)   # 用户需要的结束时间
    n1=timeb.dayofyear
    n2=timee.dayofyear
    
    if n2<=len(dir_uv)+1:
        dir_uv2=dir_uv[n1-2:n2-1]   # met文件列表顺序与时间天数刚好差2, 第0个代表第二天
    else:
        print*('输入时间超出calmet计算时间')
        
    with xr.open_mfdataset(dir_uv2,concat_dim='it',combine='nested') as ds:
        # print(ds)
        
        time_met=ds['time'].values
        # 为了便于确定时间，将时间单位均统一到pandas格式
        time0=pd.to_datetime(str(time_met[0,0]),format='%Y%j%H')+pd.Timedelta(str(time_met[0,1])+'s')
        time1=pd.to_datetime(str(time_met[1,0]),format='%Y%j%H')+pd.Timedelta(str(time_met[1,1])+'s')
        dt=time1-time0
        time_met=pd.date_range(time0,freq=dt,periods=time_met.shape[0])
        
        index= (time_met<=timee) & (time_met>=timeb)   # 获取用户之间时间范围的bool数组
        
        #利用index数组，截取相关变量并输出
        u_met=ds['u_wind'].loc[index,0,:,:].values
        v_met=ds['v_wind'].loc[index,0,:,:].values
        grid_met=ds['XYGRID'].values[0,:]
        time_met=time_met[index]
        
        # u_met=u_met.tranpose(0,2,1)     # 将坐标方向设置为x,y
        # v_met=v_met.tranpose(0,2,1)
     
    return u_met,v_met,time_met,grid_met

#################################################################################

def read_xq(dir_xq,timeb,nhour=120):
    
    """
    读入一个大气弥散因子文件，并转换为数组
    input：dir_xq，所有弥散因子文件列表，利用glob生成
           usertime，用户输入的时间，转为pd的时间
           nhour,读取met数据的长度，默认为120h
     output：数组，时间，网格
     
    后续可将xq的输出序号直接改为日期，便于识别定位
    """
    timee=timeb+pd.Timedelta(hours=nhour)   # 用户需要的结束时间
    n1=timeb.dayofyear
    n2=timee.dayofyear
    
    if n2<=365:
        dir_xq2=dir_xq[n1//5:n2//5+1]   # xq文件每个代表5天
    else:
        print*('输入时间超出弥散因子计算时间')

    with xr.open_mfdataset(dir_xq2,concat_dim='t',combine='nested') as ds:
        print(ds)
        
        time_xq=ds['TIME'].values
        # 为了便于确定时间，将时间单位均统一到pandas格式
        time0='%4d-%03d-%02d'%(tuple(time_xq[0,:3]))
        time0=pd.to_datetime(time0,format='%Y-%j-%H')+pd.Timedelta(str(time_xq[0,-1])+'s')
        time1='%4d-%03d-%02d'%(tuple(time_xq[1,:3]))
        time1=pd.to_datetime(time1,format='%Y-%j-%H')+pd.Timedelta(str(time_xq[1,-1])+'s')
        
        dt=time1-time0
        time_xq=pd.date_range(time0,freq=dt,periods=time_xq.shape[0])
        
        index= (time_xq<=timee) & (time_xq>=timeb)   # 获取用户之间时间范围的bool数组
        
        xq=ds['KR-85'].loc[index,:,:].values
        xygrid=ds['XYGRID'].values[0,:]
        time_xq=time_xq[index]
        
    return xq,time_xq,xygrid

#################################################################################

def grid2xy(gridin):
    '''
    将输入的grid数据，整理为二维数组，注意区分met和xq的不同
    '''
    grid=gridin.copy()
    nx,ny=int(grid[0]),int(grid[1])
    
    if grid.shape[0] ==5:   # met对应的网格
        x1=np.linspace(grid[3]/1000,-grid[3]/1000,nx)
        y1=np.linspace(grid[4]/1000,-grid[4]/1000,ny)
        
    else:                   # xq对应的网格
        nest=int(grid[-1])
        nx=nx*nest-1
        ny=ny*nest-1
        x1=np.linspace(grid[4],-grid[4],nx)
        y1=np.linspace(grid[5],-grid[5],ny)

    return x1,y1



def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)), n)
    return new_cmap

if __name__ == '__main__':


    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('..\系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('..\用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('绘图配置.YAML', 'r', encoding='utf-8') as f:
        picinfo = yaml.load(f.read(), Loader=yaml.FullLoader)

    dir_run=os.path.join(dir_sys['dir_out0'],grd['title'])
    dir_out=os.path.join(dir_run,'9pic')
    # dir_tif=os.path.join(dir_out,picinfo['dir_tif'])
    
    usertime=pd.to_datetime(picinfo['dateb'])  # 用户输入时间
    
    """
    获取uv文件列表
    """
    dir_uv=glob.glob(os.path.join(dir_run,'3metuv','*.nc'))
    dir_uv.sort()
    
    u_met,v_met,time_met,grid_met=read_uv(dir_uv,usertime,nhour=50)   # 获取met文件的uv分量
    x1,y1=grid2xy(grid_met)
    
    """
    获取大气弥散因子列表
    """
    dir_xq=glob.glob(os.path.join(dir_run,'6xq','*.nc'))
    dir_xq.sort()
    
    xq,time_xq,grid_xq=read_xq(dir_xq,timeb=usertime,nhour=50)   # 获取整年大气弥散因子
    x2,y2=grid2xy(grid_xq)

    # (nta,ny,nx)=np.shape(xqa)

    # usertime=pd.to_datetime(picinfo['dateb']).to_pydatetime()
    # nn=time2num(usertime)

    # nxm, nym, dxkm, dykm, xorigkm, yorigkm, meshdn=list(xygrid)
    # nx,ny=(np.int32(nxm*meshdn-1),np.int32(nym*meshdn-1,))

    # x = np.linspace(xorigkm,-xorigkm, nx)
    # y = np.linspace(yorigkm,-yorigkm, nx)
    # XX,YY = np.meshgrid(x, y)

    # nts=96
    # start1='%4d-%03d-%02d'%(tuple(xqtime[nn,:3]))
    # start1=datetime.datetime.strptime(start1,"%Y-%j-%H")
    # mytime=pd.date_range(start=start1,periods=nts,freq='H')




    # '''
    # 画图部分
    # '''

    # print('开始绘制图像')
    # s=time.time()

    # img = plt.imread(dir_tif)

    # # colors=['blue','brown','red','lightsalmon','orange','gold',
    # #         'yellow','yellowgreen','turquoise','deepskyblue','hotpink']

    # plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
    # plt.rcParams["axes.unicode_minus"]=False #该语句解决图像中的“-”负号的乱码问题


    thin=3
    cmap = plt.cm.jet
    cmap2 = truncate_colormap(cmap, 0.4, 1, 20)
    levels=np.linspace(-7,-2,10)
    fig = plt.figure(figsize=(8,8),dpi=96)  #白色画布
    
    
    ax2 = fig.add_axes([0.09, 0.09, 0.85, 0.85])
    ax2.quiver(x1[::thin], y1[::thin], u_met[0,::thin,::thin], v_met[0,::thin,::thin])
    ax2.set_xlim(x1[0],x1[-1])
    ax2.set_ylim(y1[0],y1[-1])
    ax2.set_xticks([])     #关闭坐标轴刻度
    ax2.set_yticks([])
    
    ax3 = fig.add_axes(ax2.get_position().bounds)
    ax3.set_facecolor('none')
    ax3.set_xlim(x2[0],x2[-1])
    ax3.set_ylim(y2[0],y2[-1])
    
    xq1=np.log10(xq[0,:,:]*1e-6)
    h2=ax3.contourf(x2,y2,xq1,levels=levels,cmap=cmap2,alpha=0.5)
    
    # for k in range(0,8):
    #     dose1=np.log10(doses[1,k,:,:])
    #     # dose1=np.log10(xq1[k,:,:])
    #     ax3 = fig.add_axes(ax2.get_position().bounds)
    #     ax3.set_facecolor('none')
    #     ax3.set_xlim(xorigkm,-xorigkm)
    #     ax3.set_ylim(yorigkm,-yorigkm)

    #     ax3.set_xticks(np.linspace(xorigkm,-xorigkm,7))
    #     ax3.set_yticks(np.linspace(yorigkm,-yorigkm,7))
    #     plt.title('烟团轨迹变化')
    
    
    # ax1.imshow(img, extent=[xorigkm,-xorigkm,yorigkm,-yorigkm])

    # ax1.set_xticks([])     #关闭坐标轴刻度
    # ax1.set_yticks([])

    # #添加同心圆
    # ax2 = fig.add_axes(ax1.get_position().bounds)
    # ax2.set_facecolor('none')
    # ax2.set_xticks([])     #关闭坐标轴刻度
    # ax2.set_yticks([])

    # ax2.set_xlim(xorigkm,-xorigkm)
    # ax2.set_ylim(yorigkm,-yorigkm)

    # distance = np.linspace(0,80,5)
    # for idis in range(len(distance)):
    #     circle = Circle((0, 0), radius=distance[idis],
    #                     facecolor="None", edgecolor="white",
    #                     label='a circle',linestyle='-',linewidth=1.2)
    #     ax2.add_patch(circle)
    # plt.show()

    # for k in range(0,8):
    #     dose1=np.log10(doses[1,k,:,:])
    #     # dose1=np.log10(xq1[k,:,:])
    #     ax3 = fig.add_axes(ax2.get_position().bounds)
    #     ax3.set_facecolor('none')
    #     ax3.set_xlim(xorigkm,-xorigkm)
    #     ax3.set_ylim(yorigkm,-yorigkm)

    #     ax3.set_xticks(np.linspace(xorigkm,-xorigkm,7))
    #     ax3.set_yticks(np.linspace(yorigkm,-yorigkm,7))
    #     plt.title('烟团轨迹变化')

    #     ax3.set_xlabel('X / km',fontproperties='Times New Roman',fontsize=14)
    #     ax3.set_ylabel('Y / km',fontproperties='Times New Roman',fontsize=14)
    #     h2=ax3.contourf(XX,YY,dose1,cmap=cmap2,alpha=0.5)
    #     tt=ax3.text(0.38,0.95,mytime[k].strftime('%Y-%m-%d, %H:%M'),fontsize=14, c='y',transform = ax3.transAxes)
    #     plt.pause(0.5)
    #     if k<8:
    #         tt.remove()
    #         ax3.remove()

    # plt.savefig(os.path.join(dir_out,'烟团轨迹变化图'+'.png'),dpi=200)


