import matplotlib.pyplot as plt
import netCDF4
import numpy as np
import time
from PIL import Image

dose_nc = netCDF4.Dataset('dose02.nc')

lon = dose_nc.variables['lon'][:]
lat = dose_nc.variables['lat'][:]
dose_inhaled = dose_nc.variables['air'][:]
# dose_eff = dose_nc.variables['dose_eff'][:]
# dose_th = dose_nc.variables['dose_th'][:]

dose_eff_min = np.min(dose_inhaled)
dose_eff_max = np.max(dose_inhaled)

norm_dose_eff = (dose_inhaled - dose_eff_min) / (dose_eff_max - dose_eff_min)

lon_mesh, lat_mesh = np.meshgrid(lon, lat)

# 编码到图像0-255区间
gray_img = (norm_dose_eff * 255).astype(np.uint8)
time1 = time.time()


for i in range(0, 53):
    gray_img1 = gray_img[i, :, :]
    im = Image.fromarray(gray_img1, mode='L')
    im.save('dose01_' + str(i) + '.png')
# for i in range(0, 24):
#     gray_img1 = gray_img[i, :, :]
#     plt.imsave('dose01_' + str(i) + '.png', gray_img1, cmap='gray')
time2 = time.time()


with Image.open('output_multi_frame.tif', 'w') as multi_frame_tiff:
    for gray_img in gray_images:
        # 将 NumPy 数组转换为 Pillow 图像对象
        image = Image.fromarray(gray_img, mode='L')
        # 将图像添加到多帧 TIFF 文件中
        multi_frame_tiff.save(image)

print(time2 - time1)



# gray_img1 = gray_img[5, :, :]
#
# plt.imshow(gray_img1, cmap='gray')
# plt.colorbar()
# # plt.show()
# plt.savefig('dose01.png')
print(dose_nc)
