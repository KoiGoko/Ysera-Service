# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 16:46:32 2022

将每个事故序列抽样计算的格点结果，转换为剂量随距离的变化

生成CCDF曲线

刘新建  2022年10月3日

"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from  matplotlib import ticker 
import yaml,os,glob

# from functools import partial
# import pathos.multiprocessing

def cal_dose_dis(temp,dis,xp):
    """
    input : temp,抽样计算的剂量场网格
            dis,与temp二维形状一致的距离数组
            xp，统计的距离数组    
    Returns：out1，与xp形状一致的剂量数组，表示剂量随距离变化
    """
    nt=np.shape(temp)[0]
    out1=np.zeros([nt,len(xp)])
    for i in range(nt):
        temp1=temp[i,:,:]
        for j in range(len(xp)):
            if j==0:
                index=(dis<=xp[j])
            else:
                index=(dis<=xp[j]) & (dis>=xp[j-1])
                
            out1[i,j]=np.max(temp1[index])
            
    return out1


# for i in range(nt):
#     temp1=temp[i,:,:]
#     for j in range(len(xp)):
#         if j==0:
#             index=(dis<=xp[j])
#         else:
#             index=(dis<=xp[j]) & (dis>=xp[j-1])
            
#         out1[i,j]=np.max(temp1[index])
        

if __name__ == '__main__':
    
    with  open('绘图配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)
        
    dir_in=dir_sys['dir_in']
    dir_out=dir_sys['dir_out']
    
      
    # 
    
    fre=np.array([2.22E-07,2.57E-09,7.15E-09,4.13E-09,1.92E-09,5.81E-10,
                  6.29E-13,1.36E-11,3.28E-10,5.23E-09,9.61E-09])
    
    fnames=glob.glob(os.path.join(dir_in, '*.nc'))
    ns=len(fnames)     #对应事故源项数据 number source
    
    f1=xr.open_dataset(fnames[0])
    print(f1)
    
    
    # 获取基本的网格信息
    nx,ny,nt=f1.dims['x'],f1.dims['y'],f1.dims['time']
    
    x,y=f1['lon'].values,f1['lat'].values
    
    xp=x[x>0.1]     # 用于循环的数据点 xpositive
    
    xx,yy=np.meshgrid(x,y)
    dis=np.sqrt(xx**2+yy**2)
    
        
    # dose_limit=np.ones([ns,1])*0.05    #设定剂量限值
    
    # 为了与maccs程序对比，这里不区分方位，直接给出剂量随距离的变化

    f=xr.open_dataset(fnames[0])
    temp=f['dose_eff'].values.transpose([0,2,1])*1.0e-6
    
    out1=cal_dose_dis(temp,dis,xp)
        
    
    # out1[:,0]=np.max(out1,axis=1)          # 对第一列进行处理
    # out1[:,1]=np.max(out1[:,1:-1],axis=1)  # 对第二列进行处理
    
    out2=np.sort(out1, axis=1,)           # 粗暴的简单排序
    out2=out2[:,::-1]
    
    fig=plt.figure(figsize=(5,4), dpi=300)
    ax1 = fig.add_axes([0.15, 0.15, 0.75, 0.75])
    
    # plt.ticklabel_format(style='sci',scilimits=(0,0),axis='y')
    ax1.plot(xp,out2.T,linewidth=0.8)
    ax1.set_xlabel('dis(km)')
    ax1.set_ylabel('Dose(Sv)')
    ax1.set_xlim(0.5,30)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid('True',which='both',linewidth=0.5,alpha=0.5)
    ax1.set_title('dose vs distance')
    plt.savefig('dose_dis.png',dpi=300)
    plt.close(fig)
    
    ############排序后的曲线图###########################
    outs=np.sort(out2, axis=0)
    outs=np.sort(outs, axis=1)
    outs=outs[::-1,::-1]
    
    fig=plt.figure(figsize=(5,4), dpi=300)
    ax1 = fig.add_axes([0.15, 0.15, 0.75, 0.75])
    index=[round(nt*0.05),round(nt*0.5),round(nt*0.95),]
    yp=outs[index,:].T
    ax1.plot(xp,yp)
    ax1.fill_between(xp,yp[:,0],yp[:,2],facecolor='bisque',alpha=0.7)
    ax1.legend(['95%','50%','5%'],fontsize=7)
    ax1.set_xlabel('Distance(km)')
    ax1.set_ylabel('Dose(Sv)')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlim(0.5,30)
    ax1.grid('True',which='both',linewidth=0.4,alpha=0.5)
    ax1.set_title('dose vs distance')
    plt.savefig('dose_dis_sort.png',dpi=300)
    plt.close(fig)
    
    
    np.savez('out.npz',out1,out2,outs)




