# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 20:58:12 2022

@author: xinjian
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

xline=np.load('xline.npy')
yline=np.load('yline.npy')
data=np.load('data.npy').astype('int')
nt=np.shape(data)[0]
ns=np.shape(data)[2]



# 统计每个事故序列对应剂量的CCDF
dx=xline[1]-xline[0]


xy=np.zeros_like(data)

for i in range(np.shape(data)[2]):
    xy[:,0,i]=xline[data[:,0,i]]
    xy[:,1,i]=xline[data[:,1,i]]
    
# 将xy转换为距离
dis=np.sqrt(xy[:,0,:]**2+xy[:,1,:]**2)+dx/2*np.random.rand(nt,1)

dis1=np.sort(dis,axis=0)
# dis1=dis1[::-1,:]
# 排序得到自然分布频率
fre=np.linspace(nt,1,nt)/(nt+1)

colors=['k','grey','r','coral','orange','blue','olive','y','pink',
        'greenyellow','darkgreen','lime','cyan']
fig=plt.figure(figsize=(5,4), dpi=300)
ax1 = fig.add_axes([0.15, 0.15, 0.75, 0.75])

# index=[round(nt*0.05),round(nt*0.5),round(nt*0.95),]
for i in range(ns):
    ax1.plot(dis1[:,i],fre,color=colors[i])
# ax1.fill_between(xp,yp[:,0],yp[:,2],facecolor='bisque',alpha=0.7)
# ax1.legend(['95%','50%','5%'],fontsize=7)
ax1.set_xlabel('Distance(km)')
ax1.set_ylabel('probability')
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlim(0.2,45)

# ax1.set_xticks([1,3,10,30])
ax1.grid('True',which='both',linewidth=0.4,alpha=0.5)
# ax1.set_title('dose vs distance')
plt.savefig('dose_fre.png',dpi=300)
plt.close(fig)




#####################################################
'''
考虑所有事故的发生频率，得到超过剂量阈值的绝对频率
直接对距离进行统计即可
'''
fres=np.array([2.22E-07,2.57E-09,7.15E-09,4.13E-09,1.92E-09,5.81E-10,
              6.29E-13,1.36E-11,3.28E-10,5.23E-09,9.61E-09])

xs=np.linspace(0.1, np.max(xline)*1.5,200)  # 定义统计的距离

ff=np.zeros([len(xs),ns])
    


for j in range(ns):
    disj=dis1[:,j]
    for i in range(len(xs)):
        ff[i,j]=len(disj[disj>=xs[i]])/nt


for j in range(ns):
    ff[:,j]*=fres[j]
    
fsum=np.sum(ff,axis=1)    

fig=plt.figure(figsize=(5,4), dpi=300)
ax1 = fig.add_axes([0.15, 0.15, 0.75, 0.75])

# index=[round(nt*0.05),round(nt*0.5),round(nt*0.95),]
for i in range(ns):
    ax1.plot(xs,ff[:,i],linewidth=0.5)
    
ax1.plot(xs,fsum,color='deepskyblue',linewidth=2)
# ax1.fill_between(xp,yp[:,0],yp[:,2],facecolor='bisque',alpha=0.7)
# ax1.legend(['95%','50%','5%'],fontsize=7)
ax1.set_xlabel('Distance(km)')
ax1.set_ylabel('probability')
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlim(0.5,45)
ax1.set_ylim(1e-13,2e-7)

# ax1.set_xticks([1,3,10,30])
ax1.grid('True',which='both',linewidth=0.4,alpha=0.5)
# ax1.set_title('dose vs distance')
plt.savefig('dose_fre_sum.png',dpi=300)
plt.close(fig)





