# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 16:46:32 2022
@author: 86139
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import yaml,os,glob
import time
import matplotlib.colors as colors

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)), n)
    return new_cmap


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

dose_name=picinfo['dose_name']
dose_limit=picinfo['dose_level'][0]/1000
scale_factor=float(picinfo['scale_factor'])  # 剂量修正因子

#%%read nc
fnames=glob.glob(os.path.join(dir_run,'8dose','*.nc'))

fname1=fnames[0]
with xr.open_dataset(fname1) as vinfo:
    print(vinfo)
    num_hour = len(vinfo.time)

    #从nc中读取经纬度信息
    info = np.matrix([[len(vinfo.lon),len(vinfo.lat)],[min(vinfo.lon).values,max(vinfo.lon).values],
                      [min(vinfo.lat).values,max(vinfo.lat).values]])
#确定网格信息
xline = np.linspace(info[1,0],info[1,1],int(info[0,0]))
yline = np.linspace(info[2,0],info[2,1],int(info[0,1]))
xx,yy = np.meshgrid(xline,yline)
dx = xline[1]-xline[0]

ns=len(fnames)     #对应事故源项数据 number source

for k in range(1,ns+1):
    dose1=xr.open_dataset(fnames[k-1])
    dose2=dose1[dose_name].values.transpose(0,2,1)*scale_factor   #将维度转为time,x,y
    dose3=np.mean(dose2,axis=0)

'''
画图部分
'''
print('开始绘制图像')
s=time.time()

cmap = plt.cm.jet
cmap2 = truncate_colormap(cmap, 0.4, 1, 20)


img = plt.imread(dir_tif)

plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
plt.rcParams["axes.unicode_minus"]=False #该语句解决图像中的“-”负号的乱码问题

fig = plt.figure(figsize=(7,7),dpi=96)  #白色画布
ax1 = fig.add_axes([0.09, 0.09, 0.85, 0.85])
ax1.imshow(img, extent=[info[1,0], info[1,1], info[1,0], info[1,1]])

ax1.set_xticks([])     #关闭坐标轴
ax1.set_yticks([])

titlename=['RC'+ '%02d'%i for i in range(1,ns+1)]

for k in range(0,ns):

    ax2 = fig.add_axes(ax1.get_position().bounds)
    ax2.set_facecolor('none')


    ax2.set_xlim(info[1,0],info[1,1])
    ax2.set_ylim(info[1,0],info[1,1])

    ax2.set_xticks(np.linspace(info[1,0],info[1,1],7))
    ax2.set_yticks(np.linspace(info[1,0],info[1,1],7))


    ax2.set_xlabel('X / km',fontproperties='Times New Roman',fontsize=15)
    ax2.set_ylabel('Y / km',fontproperties='Times New Roman',fontsize=15)

    h2=ax2.contourf(xx,yy,np.log10(dose3),cmap=cmap2,alpha=0.5)

    plt.title(titlename[k]+'释放平均剂量场')
    plt.savefig(os.path.join(dir_out,titlename[k]+'释放平均剂量场'+'.png'),dpi=200)

    ax2.remove()

print('打印图像用时:%5.1f'% (time.time()-s))




