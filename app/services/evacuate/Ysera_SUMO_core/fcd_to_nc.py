import xml.etree.ElementTree as ET
import asyncio
import re
import numpy as np
from evacuate.src.utils import input_args
import os
import netCDF4 as nc

__author__ = 'Nan Jia'
__email__ = 'KoiGoko@outlook.com'


def process_xml(xml_string, last_position):
    xml_string = remove_comments(xml_string)
    if last_position == 0:
        line_to_remove = '<?xml version="1.0" encoding="UTF-8"?>'
        xml_string = xml_string.replace(line_to_remove, '')
    xml_string = f"<root>{xml_string}</root>"
    context = ET.fromstring(xml_string)

    res_data = []
    base = 0
    for timestep in context.findall('timestep'):
        datas = None
        print(timestep.get('time'))
        vehicle_ele = timestep.findall('vehicle')
        if len(vehicle_ele) > 0:

            if len(vehicle_ele) > base:
                base = len(vehicle_ele)
            for vehicle in vehicle_ele:
                data = np.array([vehicle.get('id'), vehicle.get('x'), vehicle.get('y'), vehicle.get('type'),
                                 vehicle.get('speed'), vehicle.get('pos'), vehicle.get('lane')], dtype=str).reshape(1,
                                                                                                                    7)

                datas = np.vstack((datas, data)) if datas is not None else data

            res_data.append(datas)
            continue
        res_data.append(None)

    return res_data, base


def generate_initArray(file_path):
    evacuate = input_args(file_path, 'evacuate')

    private_veh = evacuate['vehicle_number']
    public_veh = evacuate['public_routes']

    veh = []
    for k, v in private_veh.items():
        for k1, v1 in v.items():
            for i in range(v1):
                veh.append(k + '_' + k1 + '_' + str(i))

    for k, v in public_veh.items():
        for k1, v1 in v.items():
            for k2, v2 in v1.items():
                for i in range(v2):
                    veh.append(k + '_' + k2 + '_' + str(i) + '_' + k1)

    veh = np.array(veh).reshape(len(veh), 1)
    veh = np.sort(veh, axis=0)
    veh = np.pad(veh, ((0, 0), (0, 6)), 'constant')

    return veh


def remove_comments(xml_string):
    pattern = r"<!--.*?-->"
    return re.sub(pattern, '', xml_string, flags=re.DOTALL)


def find_last_timestep(xml_string):
    last_timestep_index = xml_string.rfind("</timestep>")
    return last_timestep_index


async def read_data(file_path, cfg_path):
    last_position = 0
    incomplete_xml = ""
    end = False
    read_count = 4096 * 200
    veh = generate_initArray(cfg_path)
    with open(file_path, 'r') as f:
        while not end:
            f.seek(last_position)
            data = incomplete_xml + f.read(read_count)

            if data.rfind("</timestep>") == -1:
                await asyncio.sleep(0.0001)
                read_count += 4096 * 200
                continue

            if last_position == 0:
                line_to_remove = '<fcd-export xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/fcd_file.xsd">'
                data = data.replace(line_to_remove, '')

            if data.rfind("</fcd-export>") != -1:
                data = data.replace("</fcd-export>", '')
                end = True

            process_data = data[:find_last_timestep(data) + len("</timestep>") + 1]

            pro_data, base = process_xml(process_data, last_position)

            res_array = None

            for pro_ele in pro_data:
                veh1 = np.copy(veh)
                if pro_ele is not None:
                    matching_indices = np.where(np.isin(veh[:, 0], pro_ele[:, 0]))[0]
                    veh1[matching_indices, 1:] = pro_ele[:, 1:]

                res_array = np.dstack((res_array, veh1)) if res_array is not None else veh1[:, :, np.newaxis]

            nc_path = 'res_xr.nc'

            if os.path.exists(nc_path):
                res_xr = nc.Dataset(nc_path, 'a')
                length = res_xr.dimensions['timestep'].size
                print('nc长度 ', length)
                res_xr.variables['data'][:, :, length:length + res_array.shape[2]] = res_array
            else:
                res_xr = nc.Dataset(nc_path, 'w')
                res_xr.createDimension('timestep', None)
                res_xr.createDimension('value', 7)
                res_xr.createDimension('vehicle', res_array.shape[0])

                # 请注意，这里的数据类型是'S40'，可以根据自己的数据类型的长度修改这里的值
                # S40指的是最长可以表示40个字符的字符串
                res_xr.createVariable('timestep', 'S40', ('timestep',))
                res_xr.createVariable('value', 'S40', ('value',))
                res_xr.createVariable('vehicle', 'S40', ('vehicle',))

                array_xr = res_xr.createVariable('data', 'S40', ('vehicle', 'value', 'timestep'))

                array_xr[:] = res_array

            incomplete_xml = data[find_last_timestep(data) + len("</timestep>"):]

            last_position = f.tell()  # 记录当前文件指针位置
            read_count = 4096 * 10


async def main():
    # fcd路径
    xml_file = r'F:\厂址应急道路专题数据\10km工作日晴昼\fcd.xml'
    # 配置文件路径
    cfg_path = r'F:\厂址应急道路专题数据\10km工作日晴昼'
    await read_data(xml_file, cfg_path)

    # res_file = nc.Dataset(r'D:\Ysera\Ysera-Core\evacuate\src\res\5km晴昼.nc', 'r')
    # print('nc长度', res_file.dimensions['timestep'].size)
    # res_file.close()


if __name__ == "__main__":
    if os.path.exists('res_xr.nc'):
        os.remove('res_xr.nc')
        print('remove previous res_xr.nc')
    asyncio.run(main())
