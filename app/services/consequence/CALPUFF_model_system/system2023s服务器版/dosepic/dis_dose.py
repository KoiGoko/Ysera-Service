# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 16:46:32 2022
将每个事故序列抽样计算的格点结果，转换为剂量随距离的变化
刘新建  2022年10月3日
"""

import numpy as np
import xarray as xr
import matplotlib
import matplotlib.pyplot as plt
import yaml,os,glob,time


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


if __name__ == '__main__':

    print('开始统计数据结果')
    s=time.time()
    # 第一步，读取用户输入和系统路径配置文件，获取目录信息和计算点信息
    with  open('..\系统路径配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('..\用户输入信息.YAML', 'r', encoding='utf-8') as f:
        grd = yaml.load(f.read(), Loader=yaml.FullLoader)

    with  open('绘图配置.YAML', 'r', encoding='utf-8') as f:
        picinfo = yaml.load(f.read(), Loader=yaml.FullLoader)

    dir_run=os.path.join(dir_sys['dir_out0'],grd['title'])
    dir_out=os.path.join(dir_run,'9pic')
    
    dose_name=picinfo['dose_name']
    scale_factor=float(picinfo['scale_factor'])  # 剂量修正因子

    fnames=glob.glob(os.path.join(dir_run,'8dose','*.nc'))

    ns=len(fnames)     #对应事故源项数据 number source

    with xr.open_dataset(fnames[0]) as f1:
        print(f1)
        # 获取基本的网格信息
        nx,ny,nt=f1.dims['x'],f1.dims['y'],f1.dims['time']
        x,y=f1['lon'].values,f1['lat'].values

    xp=x[x>0.1]     # 用于循环的数据点 xpositive

    xx,yy=np.meshgrid(x,y)
    dis=np.sqrt(xx**2+yy**2)

    # 为了与maccs程序对比，这里不区分方位，直接给出剂量随距离的变化
    for  k in range(ns):
        with xr.open_dataset(fnames[k]) as f:
            temp=f[dose_name].values.transpose([0,2,1])*scale_factor*1.0e-6

        out1=cal_dose_dis(temp,dis,xp)

        # out1[:,0]=np.max(out1,axis=1)          # 对第一列进行处理
        out2=np.sort(out1, axis=1,)           # 粗暴的简单排序
        out2=out2[:,::-1]

        plt.rcParams["font.sans-serif"]=["Microsoft YaHei"] #设置字体
        plt.rcParams["axes.unicode_minus"]=False #该语句解决图像中的“-”负号的乱码问题

        fig=plt.figure(figsize=(5,4), dpi=96)
        ax1 = fig.add_axes([0.15, 0.15, 0.75, 0.75])

        # plt.ticklabel_format(style='sci',scilimits=(0,0),axis='y')
        ax1.plot(xp,out2.T,linewidth=0.8)
        ax1.set_xlabel('dis(km)')
        ax1.set_ylabel('Dose(Sv)')
        ax1.set_xlim(round(xp[0],1),round(xp[-1],1))
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        
        ax1.set_xticks([1,2,3,5,7,10,20,30])
        ax1.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax1.set_xlim(round(xp[0],1),round(xp[-1],1))
        ax1.grid('True',which='both',linewidth=0.5,alpha=0.5)
        ax1.set_title('dose vs distance')
        plt.savefig(os.path.join(dir_out,'source'+str(k+1)+'-dose_dis.png'),dpi=300)
        plt.close(fig)

        ############排序后的曲线图###########################
        outs=np.sort(out2, axis=0)
        outs=np.sort(outs, axis=1)
        outs=outs[::-1,::-1]

        fig=plt.figure(figsize=(5,4), dpi=96)
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
        ax1.set_xticks([1,2,3,5,7,10,20,30])
        ax1.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax1.set_xlim(round(xp[1],1),round(xp[-1],1))
        # ax1.set_ylim(0.0001,1)
        ax1.grid('True',which='both',linewidth=0.4,alpha=0.5)
        ax1.set_title('dose vs distance')
        plt.savefig(os.path.join(dir_out,'source'+str(k+1)+'dose_dis_sort.png'),dpi=300)
        plt.close(fig)

    print('统计绘图计算用时:%5.1f'% (time.time()-s))



