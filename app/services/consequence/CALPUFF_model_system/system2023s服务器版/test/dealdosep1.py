# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 16:46:32 2022

@author: 86139

"""

from functools import partial

# import matplotlib.pyplot as plt
# from matplotlib.patches import Circle
import glob
import numpy as np
import os
import pathos
import time
import xarray as xr
import yaml


def findxy(dose_arr, dose_limit):
    """
    寻找一个剂量场中剂量超过特定阈值的最远位置
    输入：dose_arr二维的数组
          dose_limit，统计的剂量值
    输出：对应的xy坐标
    """
    import numpy as np
    m, n = np.shape(dose_arr)

    # 构造距离函数
    xx, yy = np.meshgrid(np.linspace(-n, n, n), np.linspace(-m, m, m))

    dis = np.sqrt(xx ** 2 + yy ** 2)

    if dose_arr.min() > dose_limit:  # 最小值仍大于限值，取最远点即可
        xyindex = [m, n]

    elif dose_arr.max() < dose_limit:  # 最大值小于限值，取最中心点
        xyindex = [round(m / 2), round(n / 2)]

    else:
        index = dose_arr < dose_limit
        dis[index] = np.nan
        i, j = np.where(dis == np.nanmax(dis))
        xyindex = [i[0], j[0]]

    return xyindex


if __name__ == '__main__':
    s = time.time()
    with  open('绘图配置.YAML', 'r', encoding='utf-8') as f:
        dir_sys = yaml.load(f.read(), Loader=yaml.FullLoader)
        dir_in = dir_sys['dir_in']
        dir_out = dir_sys['dir_out']

    # %%read nc
    fnames = glob.glob(os.path.join(dir_in, '*.nc'))

    f1 = xr.open_dataset(fnames[0])
    print(f1)

    # 获取基本的网格信息
    nx, ny, nt = f1.dims['x'], f1.dims['y'], f1.dims['time']

    x, y = f1['lon'].values, f1['lat'].values

    xx, yy = np.meshgrid(x, y)
    dis = np.sqrt(xx ** 2 + yy ** 2)

    dose_eff = f1.dose_eff.values * 1.0e-6  # dose_eff  (time, y, x) float32
    f1.close()
    pool = pathos.multiprocessing.Pool(2)

    data = pool.map(partial(findxy, dose_limit=0.05), dose_eff)

    print(time.time() - s)

    pool.close()
    pool.join()
