# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 16:46:32 2022

@author: 86139

"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import yaml, os, glob

with  open('绘图配置.YAML', 'r', encoding='utf-8') as f:
    dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)
    dir_in = dir_sys['dir_in']
    dir_out = dir_sys['dir_out']

# %%read nc
fnames = glob.glob(os.path.join(dir_in, '*.nc'))

vinfo = xr.open_dataset(fnames[0])
num_hour = len(vinfo.time)
# 从nc中读取经纬度信息
info = np.matrix([[len(vinfo.lon), len(vinfo.lat)], [min(vinfo.lon).values, max(vinfo.lon).values],
                  [min(vinfo.lat).values, max(vinfo.lat).values]])
# 确定网格信息
xline = np.linspace(info[1, 0], info[1, 1], int(info[0, 0]))
yline = np.linspace(info[2, 0], info[2, 1], int(info[0, 1]))

np.save('xline.npy', xline)
np.save('yline.npy', yline)

xx, yy = np.meshgrid(xline, yline)
dx = xline[1] - xline[0]
source1x = 0
source1y = 0
xydis = np.sqrt((xx - source1x) ** 2 + (yy - source1y) ** 2)

ns = len(fnames)  # 对应事故源项数据 number source

dose_limit = np.ones([ns, 1]) * 0.05  # 设定剂量限值;
xyindex = np.zeros([num_hour, 2])

data = np.zeros([num_hour, 2, ns])
out = []
for k in range(1, ns + 1):
    dose1 = xr.open_dataset(fnames[k - 1])
    dose2 = dose1.dose_eff.values.transpose(0, 2, 1)  # 将维度转为与matlab相同
    for i in range(num_hour):
        temp = dose2[i, :, :] * 1e-06
        if temp.min() > dose_limit[0]:
            xyindex[i, :] = 1
        elif temp.max() < dose_limit[0]:
            m, n = np.where(xydis == xydis.min())
            xyindex[i, 0] = m[0]
            xyindex[i, 1] = n[0]
        else:
            indexbool = [temp >= dose_limit[0][0]][0]
            index = np.zeros((indexbool.shape[0], indexbool.shape[1]))
            index[np.where(indexbool == True)] = 1
            xydis1 = xydis.copy()
            xydis1[np.where(index == 0)] = np.nan
            m, n = np.where(xydis1 == np.nanmax(xydis1))
            xyindex[i, 0] = m[0]
            xyindex[i, 1] = n[0]
    # 剔除有nan的行
    xyindex2 = xyindex.copy()
    mask = np.any(np.isnan(xyindex2), axis=1)
    mask = np.isnan(xyindex2[:, 0])
    xyindex2 = xyindex2[~mask]
    out.append(xyindex2)

    for i in range(11):
        data[:, :, i] = out[i]
    np.save('data.npy', data)

# img = plt.imread(os.path.join(dir_out,'xizoushan30.tif'))
# colors=['blue','brown','red','lightsalmon','orange','gold',
#         'yellow','yellowgreen','turquoise','deepskyblue','hotpink']


# fig = plt.figure(figsize=(9,9),dpi=200)  #白色画布
# ax1 = fig.add_axes([0.09, 0.09, 0.85, 0.85])
# ax1.imshow(img, extent=[info[1,0], info[1,1], info[1,0], info[1,1]]) 

# ax1.set_xticks([])     #关闭坐标轴
# ax1.set_yticks([])

# for k in range(0,ns):    
#     ax2 = fig.add_axes(ax1.get_position().bounds)
#     ax2.set_facecolor('none')

#     #添加同心圆

#     distance = np.linspace(0,info[1,1],5)    

#     for idis in range(len(distance)):
#         circle = Circle((0, 0), radius=distance[idis], facecolor="None", edgecolor="white",label='a circle',linestyle='-',linewidth=1.5)
#         ax2.add_patch(circle) 

#     ax2.set_xlim(info[1,0],info[1,1])
#     ax2.set_ylim(info[1,0],info[1,1])

#     ax2.set_xticks(np.linspace(info[1,0],info[1,1],7))
#     ax2.set_yticks(np.linspace(info[1,0],info[1,1],7))


#     ax2.set_xlabel('Distance / km',fontproperties='Times New Roman',fontsize=15)
#     ax2.set_ylabel('Distance / km',fontproperties='Times New Roman',fontsize=15)

#     #画散点
#     scdatax1 = out[k][:,1]
#     for i in range(len(scdatax1)):
#         scdatax1[i]=xline[int(out[k][i,1])]
#     scdatax = scdatax1-dx/2+dx*np.random.rand(len(out[k][:,1]))
#     scdatay1 = out[k][:,0]
#     for i in range(len(scdatay1)):
#         scdatay1[i]=yline[int(out[k][i,0])]

#     scdatay = scdatay1-dx/2+dx*np.random.rand(len(out[k][:,0]))
#     ax2.scatter(scdatax,scdatay,s=8,color=colors[k])
#     plt.title('RC'+'%02i'%int(k+1)+' dose-location')
#     plt.savefig(os.path.join(dir_out,'RC'+'%02i'%int(k+1)+'.png'),dpi=200)
#     ax2.remove()
