# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 16:46:32 2022

@author: 86139

"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import yaml,os,glob,time
from functools import partial

def findxy(dose_arr,dose_limit=0.05):
    '''
    寻找一个剂量场中剂量超过特定阈值的最远位置
    输入：dose_arr二维数组或者三维数组，要求时间为第一个维度
          dose_limit，统计的剂量值
    输出：对应的xy坐标
    '''
    import numpy as np
    
    if dose_arr.ndim==2:  # 如果数组为二维，直接加上时间维
        dose_arr=np.expand_dims(dose_arr,axis=0)
        
    t,m,n=np.shape(dose_arr)
    
    xyindex=np.zeros([t,2],'int32')
    # 构造距离函数
    xx,yy=np.meshgrid(np.linspace(-n,n,n),np.linspace(-m,m,m))

    dis=np.sqrt(xx**2+yy**2)
    
    for k in range(t):
        dose_arr1=dose_arr[k,:,:]
        dis1=dis.copy()
        if dose_arr1.min()>dose_limit:  # 最小值仍大于限值，取最远点即可
            xyindex[k,:]=[m,n]
            
        elif dose_arr1.max()<dose_limit:   # 最大值小于限值，取最中心点
            xyindex[k,:]=[round(m/2),round(n/2)]
    
        else:
            index=dose_arr1<dose_limit
            dis1[index]=np.nan
            i,j = np.where(dis1 == np.nanmax(dis1))
            xyindex[k,:]=[i[0],j[0]]
            
    return xyindex
    
    

if __name__ == '__main__':
     
    s=time.time()
    with  open('绘图配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)
        dir_in=dir_sys['dir_in']
        dir_out=dir_sys['dir_out']
        
        #%%read nc
    fnames=glob.glob(os.path.join(dir_in, '*.nc'))
    
    f1=xr.open_dataset(fnames[0])
    print(f1)
    
    # 获取基本的网格信息
    nx,ny,nt=f1.dims['x'],f1.dims['y'],f1.dims['time']
    
    x,y=f1['lon'].values,f1['lat'].values
    
    xx,yy=np.meshgrid(x,y)
    dis=np.sqrt(xx**2+yy**2)
    
    dose_eff=f1.dose_eff.values*1.0e-6     #  dose_eff  (time, y, x) float32
    f1.close()
    
    data=findxy(dose_eff,0.01)
    
    # pool = pathos.multiprocessing.Pool(8)
    # data = pool.map(partial(findxy, dose_limit=0.05), dose_eff)
    
    print(time.time()-s)
    








