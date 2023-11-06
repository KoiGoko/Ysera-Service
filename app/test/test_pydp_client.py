import time

import netCDF4
import numpy as np
from PIL import Image

dose_nc = netCDF4.Dataset('dose01.nc')

lon = dose_nc.variables['lon'][:]
lat = dose_nc.variables['lat'][:]
dose_inhaled = dose_nc.variables['air'][:]

dose_eff_min = np.min(dose_inhaled)
dose_eff_max = np.max(dose_inhaled)

norm_dose_eff = (dose_inhaled - dose_eff_min) / (dose_eff_max - dose_eff_min)

lon_mesh, lat_mesh = np.meshgrid(lon, lat)

# 编码到图像0-255区间
gray_img = (norm_dose_eff * 255).astype(np.uint8)
time1 = time.time()

# Assuming 'dose01_0.png' to 'dose01_52.png' exist in your directory
for i in range(36):
    gray_img1 = (norm_dose_eff[i, :, :] * 65535).astype(np.uint16)  # Scale to 16-bit range
    im = Image.fromarray(gray_img1, mode='I;16')  # Use 'I;16' mode for 16-bit grayscale
    im.save(f'dose01_{i}_int16.png')

image_list = []

for i in range(36):
    image_path = f'dose01_{i}_int16.png'
    img = Image.open(image_path)
    image_list.append(img)

# Save as a single TIFF file with int16 precision
image_list[0].save('stacked_dose01_int16.tif', save_all=True, append_images=image_list[1:], compression='tiff_deflate')

time2 = time.time()
print(time2 - time1)
print('done')
