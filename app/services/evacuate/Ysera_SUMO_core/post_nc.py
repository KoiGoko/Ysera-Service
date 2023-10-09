import netCDF4 as nc

__author__ = 'Nan Jia'
__email__ = 'KoiGoko@outlook.com'


def read_nc_file(filename):
    # 打开 NetCDF 文件
    dataset = nc.Dataset(filename, 'r')
    return dataset


if __name__ == "__main__":
    filename = 'res_xr_5km.nc'  # 文件路径
    dataset = read_nc_file(filename)

    # 获取数据变量 'data'
    data_var = dataset.variables['data']

    # 关闭数据集
    dataset.close()
