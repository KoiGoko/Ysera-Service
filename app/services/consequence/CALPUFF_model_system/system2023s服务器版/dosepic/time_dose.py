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
from PIL import Image
#***********************************************************
def read_source(dir_source):
    """
    读取事故源项
    """
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
    # dir_DCF='selectDCF.csv'
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
                DCF2[k,:,i]= DCF_inp[:,k]*source1[:,i]*(168-i+1)
            else:
                DCF2[k,:,i]= DCF_inp[:,k]*source1[:,i]*br


    #对核素求和，变成只随时间变化的一维数组
    DCF_eff=DCF2[:3].sum(axis=(0,1))
    DCF_th=DCF2[3].sum(0)
    DCF_red=DCF2[4].sum(0)
    DCF_lung=DCF2[5].sum(0)
    DCF_skin=DCF2[6].sum(0)

    return DCF_eff,DCF_th,DCF_red,DCF_lung,DCF_skin

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


def cal_dose_1(xq1,DCF_input,flag=None):
    '''
    基于单个事故源项，计算对应时间段的剂量，DCF为列表
    里面包含一个或者多个剂量转换因子，可以计算对应的剂量
    '''

    DCFs=list(DCF_input)
    no=len(DCFs)    # 计算剂量种类（器官）数目 num organ

    # 一次抽样的剂量计算数组，器官，时间，ny，nx
    Dose1=np.zeros([no,nts,ny,nx]).astype(np.float32)

    # 将每种类型的剂量转换因子进行维度扩充，变成三维数组
    for i in range(no):
        DCFs[i]=np.expand_dims(DCFs[i],axis=(1,2))
        Dose1[i,:,:,:]=xq1*DCFs[i]

    if flag==None:
        # 对所有时段的剂量进行时间求和
        Dose_sum = Dose1.sum(1)
        return Dose_sum
    else:
        return Dose1


def xy2info(xy):
    xy=xygrid
    nx,ny=int(xy[0]),int(xy[1])
    nest=int(xy[6])
    nx=nx*nest-1
    ny=ny*nest-1
    info=np.asarray([[nx,ny],[xy[4],-xy[4]],[xy[5],-xy[5]]])
    return info

def time2num(time1):
    '''
    将用户输入的时间转换为弥散计算对应的序号
    输入时间必须为datetime类型
    '''
    timerun=pd.date_range(start='2020-01-02 00:00',periods=nta,freq='H')
    timepy=timerun.to_pydatetime()

    dt=np.abs(timepy-time1)
    mindt=np.min(dt)
    index=np.where(dt==mindt)
    nn=index[0][0]
    return nn

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
    dir_tif=os.path.join(dir_out,picinfo['dir_tif'])
    
    scale_factor=float(picinfo['scale_factor'])  # 剂量修正因子
    source_id=int(picinfo['source_id'])  # 确定计算的源项序号
    
    """
    读取剂量转换因子，vg，lamta，对DCF进行初步计算
    """
    s=time.time()
    print('剂量计算程序开始执行! %.2f'% s)
    dir_source=glob.glob(os.path.join(dir_run,'7source','*sour*.xlsx'))[0]
    dir_DCF=glob.glob(os.path.join(dir_run,'7source','selectDCF.csv'))[0]

    # 调用函数读取源项表

    
    source=read_source(dir_source)
    sname=list(source.keys())
    source1=np.array(source[sname[source_id]].iloc[:,1:]).astype(np.float32)
    nts=np.shape(source1)[1]    # 源项对应的小时数，num_time_source

    # 调用函数读取剂量转换因子
    (DCFinp,vg,lamta)=read_DCF(dir_DCF)
    myDCF2=cal_dcf2(source1,DCFinp,vg)

    if grd['acutedose']!=1:
        calDCF=myDCF2[:2]
    else:
        calDCF=myDCF2
    print('剂量转换因子处理完成！')

    """
    获取大气弥散因子列表，初始化剂量数组
    """
    dir_xq=glob.glob(os.path.join(dir_run,'6xq','*.nc'))
    dir_xq.sort()
    xqa,xqtime,xygrid=read_xqa(dir_xq)   # 获取整年大气弥散因子

    (nta,ny,nx)=np.shape(xqa)

    usertime=pd.to_datetime(picinfo['dateb']).to_pydatetime()
    nn=time2num(usertime)

    nxm, nym, dxkm, dykm, xorigkm, yorigkm, meshdn=list(xygrid)
    nx,ny=(np.int32(nxm*meshdn-1),np.int32(nym*meshdn-1,))

    x = np.linspace(xorigkm,-xorigkm, nx)
    y = np.linspace(yorigkm,-yorigkm, nx)
    XX,YY = np.meshgrid(x, y)

    start1='%4d-%03d-%02d'%(tuple(xqtime[nn,:3]))
    start1=datetime.datetime.strptime(start1,"%Y-%j-%H")
    mytime=pd.date_range(start=start1,periods=nts,freq='H')

    xq1=xqa[nn:nn+nts,:,:]
    xq1=xq1.transpose(0,2,1)
    doses = cal_dose_1(xq1,calDCF,1)

    # doses=doses.transpose(0,1,3,2)

    print('剂量计算用时:%5.1f'% (time.time()-s))

    '''
    画图部分
    '''

    print('开始绘制图像')
    s=time.time()

    img = plt.imread(dir_tif)

    # colors=['blue','brown','red','lightsalmon','orange','gold',
    #         'yellow','yellowgreen','turquoise','deepskyblue','hotpink']

    plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
    plt.rcParams["axes.unicode_minus"]=False #该语句解决图像中的“-”负号的乱码问题

    cmap = plt.cm.jet
    cmap2 = truncate_colormap(cmap, 0.4, 1, 20)
    levels=np.linspace(1,6,11)
    fig = plt.figure(figsize=(8,8),dpi=96)  #白色画布
    ax1 = fig.add_axes([0.09, 0.09, 0.85, 0.85])
    ax1.imshow(img, extent=[xorigkm,-xorigkm,yorigkm,-yorigkm])

    ax1.set_xticks([])     #关闭坐标轴刻度
    ax1.set_yticks([])

    #添加同心圆
    ax2 = fig.add_axes(ax1.get_position().bounds)
    ax2.set_facecolor('none')
    ax2.set_xticks([])     #关闭坐标轴刻度
    ax2.set_yticks([])

    ax2.set_xlim(xorigkm,-xorigkm)
    ax2.set_ylim(yorigkm,-yorigkm)

    distance = np.linspace(0,-xorigkm,5)
    for idis in range(len(distance)):
        circle = Circle((0, 0), radius=distance[idis],
                        facecolor="None", edgecolor="white",
                        label='a circle',linestyle='-',linewidth=1.2)
        ax2.add_patch(circle)
    plt.show()
    
    nts1=min(nts,24)
    for k in range(0,nts1):
        dose1=np.log10(doses[1,k,:,:]*scale_factor)
        # dose1=np.log10(xq1[k,:,:])
        ax3 = fig.add_axes(ax2.get_position().bounds)
        ax3.set_facecolor('none')
        ax3.set_xlim(xorigkm,-xorigkm)
        ax3.set_ylim(yorigkm,-yorigkm)

        ax3.set_xticks(np.linspace(xorigkm,-xorigkm,7))
        ax3.set_yticks(np.linspace(yorigkm,-yorigkm,7))
        plt.title('烟团轨迹变化')

        ax3.set_xlabel('X / km',fontproperties='Times New Roman',fontsize=14)
        ax3.set_ylabel('Y / km',fontproperties='Times New Roman',fontsize=14)
        h2=ax3.contourf(XX,YY,dose1,cmap=cmap2,alpha=0.5)
        tt=ax3.text(0.38,0.95,mytime[k].strftime('%Y-%m-%d, %H:%M'),fontsize=14, c='y',transform = ax3.transAxes)
        plt.pause(0.5)
        plt.savefig(os.path.join(dir_out,str(k+1).zfill(3)+'烟团轨迹变化图'+mytime[k].strftime('%Y-%m-%d-%H')+'.png'),dpi=200)
        if k<nts1-1:
            tt.remove()
            ax3.remove()

    #将图片拼接成gif
    imgFiles = list(glob.glob(os.path.join(dir_out,'0*.png')))
    images = [Image.open(fn) for fn in imgFiles]
    im = images[0]
    filename =os.path.join(dir_out, '烟团轨迹变化图'+mytime[0].strftime('%Y-%m-%d-%H')+'.gif')
    im.save(fp=filename, format='gif', save_all=True, append_images=images[1:], duration=500)


