import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import xml.etree.ElementTree as ET
import os
import numpy as np
import glob

__author__ = 'Nan Jia'
__email__ = 'KoiGoko@outlook.com'

from evacuate.src.utils import input_args


# 结果分析模块


def read_stop_xml(xml_path):
    context = ET.iterparse(xml_path)
    datas = {}
    i = 0
    for event, elem in context:
        if elem.tag == 'stopinfo' and event == 'end':
            stop = {'id': elem.get('id'),
                    'type': elem.get('type'),
                    'started': elem.get('started'),
                    'stop_lane': elem.get('lane'),
                    'ended': elem.get('ended')}

            i += 1
            datas[i] = stop
            elem.clear()
    datas = pd.DataFrame.from_dict(datas, orient='index')
    datas['started'] = datas['started'].astype(float)
    datas['ended'] = datas['ended'].astype(float)
    datas['stop_lane'] = datas['stop_lane'].str[:-2]
    datas = datas.sort_values(by=['started'])

    datas = datas.groupby('stop_lane').agg({'id': list, 'type': list, 'started': list, 'ended': list})
    return datas


def process_stop_to_xlsx(stop_data, cfg_path, output_file):
    vehicle = input_args(cfg_path, 'vehicle')
    evacuate = input_args(cfg_path, 'evacuate')
    population = evacuate['default_population']
    # 安置点
    settlements = evacuate['settlements']
    # 撤离点
    evacuates = evacuate['evacuates']
    reverse_settlements = {value: key for key, value in settlements.items()}
    reverse_evacuates = {value: key for key, value in evacuates.items()}
    vehicle_capacity = vehicle['vehicle_capacity']

    stop_infos = {}
    for pd_ele in stop_data.iterrows():

        lane = pd_ele[0]
        settle_name = ''
        if lane in reverse_settlements.keys():
            settle_name = reverse_settlements[lane]
        elif lane in reverse_evacuates.keys():
            settle_name = reverse_evacuates[lane]
        vehicles = []
        for i in pd_ele[1]['id']:
            if len(i.split('_')) >= 4:
                vehicles.append(i.split('_')[0] + '_' + '_'.join(i.split('_')[3:]))
                continue
            vehicles.append(i.split('_')[0])

        types = pd_ele[1]['type']
        starts = []
        s = 0
        for i in types:
            value = vehicle_capacity.get(i)
            if 'public' in i:
                t = i.split('_')[1]
                value = vehicle_capacity.get(t)
            s += value
            starts.append(s)

        start_times = pd_ele[1]['started']
        end_times = pd_ele[1]['ended']

        stop_infos[settle_name] = {'vehicles': vehicles,
                                   'types': types,
                                   'starts': starts,
                                   'start_times': start_times,
                                   'end_times': end_times}
    if os.path.exists(output_file):
        os.remove(output_file)
    with pd.ExcelWriter(output_file) as writer:
        for i in stop_infos:
            print(i)
            pd_ele = pd.DataFrame.from_dict(stop_infos[i], orient='index')
            pd_ele.to_excel(writer, sheet_name=i)
    print('输出stop处理结果结束')


def process_xlsx(stop_xlsx_file, cfg_path, output_file):
    evacuate = input_args(cfg_path, 'evacuate')
    evacuates = evacuate['evacuates']
    vehicle = input_args(cfg_path, 'vehicle')['vehicle_capacity']

    stop_xlsx = pd.ExcelFile(stop_xlsx_file)

    col_name = stop_xlsx.parse(sheet_name=0, index_col=0).index.tolist()

    stop_veh_infos = {}

    for sheet_name in stop_xlsx.sheet_names:

        if sheet_name in evacuates.keys():
            continue

        stop_value = stop_xlsx.parse(sheet_name, index_col=0)

        for col in stop_value.columns:
            veh = stop_value[col].iloc[0]
            towns = str.split(veh, '_')

            if len(towns) >= 2:
                town_name = '_'.join(towns[1:])

            if len(towns) == 1:
                town_name = towns[0]

            ele = stop_value[col].values.reshape(-1, 1)
            if '_'.join(ele[1]).split('_')[0] == 'public':
                veh_name = '_'.join(ele[1]).split('_')[1]
                ele[2] = vehicle.get(veh_name)
            else:
                veh_name = '_'.join(ele[1]).split('_')[0]
                ele[2] = vehicle.get(veh_name)

            if town_name in stop_veh_infos.keys():
                pre_values = stop_veh_infos[town_name]
                curr_values = np.hstack((pre_values, ele))
                sort_indices = np.argsort(curr_values[3, :])
                sorted_curr = curr_values[:, sort_indices]
                stop_veh_infos[town_name] = sorted_curr
            else:
                stop_veh_infos[town_name] = ele

    with pd.ExcelWriter(output_file) as writer:
        for town_name, value in stop_veh_infos.items():
            ele = pd.DataFrame(value, index=col_name)
            sum_values = ele.loc['starts'].cumsum()
            ele.loc['sum'] = sum_values
            ele.to_excel(writer, sheet_name=town_name)

    print('输出stop处理结果结束')


def modify_last_sum(evacuate_path, cfg_path):
    evacuate_datas = pd.read_excel(evacuate_path, sheet_name=None, index_col=0)
    evacuate = input_args(cfg_path, 'evacuate')
    default_population = evacuate['default_population']

    if os.path.exists(evacuate_path):
        os.remove(evacuate_path)

    with pd.ExcelWriter(evacuate_path) as writer:
        for name, value in evacuate_datas.items():
            sums_row = value.loc['sum']
            if default_population[name] != sums_row.iloc[-1]:
                sums_row.iloc[-1] = default_population[name]

            value.to_excel(writer, sheet_name=name)


if __name__ == '__main__':

    paths = glob.glob(r'F:\厂址应急道路专题数据\*')

    for path in paths:
        result_path = path
        output_file = os.path.join(result_path, 'settlement.xlsx')
        evacuate_file = os.path.join(result_path, 'evacuate.xlsx')

        stops = read_stop_xml(os.path.join(result_path, 'stop.xml'))

        process_stop_to_xlsx(stops, result_path, output_file)
        process_xlsx(output_file, result_path, evacuate_file)
        modify_last_sum(evacuate_file, result_path)
