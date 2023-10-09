import glob
import itertools
import logging
import os
import xml.etree.ElementTree as ET

from evacuate.src.pre_private import input_args
from evacuate.src.pre_vehicle import get_vehicle_speed
from evacuate.src.utils import standardization_xml
from evacuate.src.dynamic_public import dynamic_public

__author__ = 'Nan Jia'
__email__ = 'KoiGoko@outlook.com'

# 公共车辆分配

# 配置日志记录器
logging.basicConfig(filename='core.log', level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')

evacuate = {}
pb_info = {}
cfg_path = ''


# 配置初始化
def init_public_cfg(_cfg_path):
    _evacuate = input_args(_cfg_path, 'evacuate')
    global cfg_path
    cfg_path = _cfg_path
    evacuate.update(_evacuate)


# 初次调度分配
def init_public_routes(pattern):
    # 信息保存
    _pb_info = {'public_position': evacuate['public_position']}

    # 自定义调度
    if pattern == 'custom':
        _pb_info['public_routes'] = evacuate['public_routes']

    pb_info.update(_pb_info)


# 计算公共车辆类型
def cal_public_type(pattern):
    vehicles = []
    if pattern == 'custom':
        for k, v in evacuate['public_routes'].items():
            for k1, v1 in v.items():
                vehicles.append(list(v1.keys()))

    # 取并集
    merges = list(itertools.chain.from_iterable(vehicles))
    return list(set(merges))


# 初始化初次分配的公共车辆的行程文件
def init_public_xml(public_trips_path, public_type):
    # 模拟场景名称
    simulator_name = evacuate['simulator']['name']

    files = glob.glob(os.path.join(public_trips_path, f'osm.{simulator_name}.public.*.trips.xml'))
    if not files:
        print('新的公共车辆行程文件初始化')
    else:
        for file in files:
            if os.path.exists(file):
                os.remove(file)
                print('remove file: {}'.format(file))
    # 创建根元素 routes
    root = ET.Element("routes")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:noNamespaceSchemaLocation", "http://sumo.dlr.de/xsd/routes_file.xsd")

    # 获取自定义的车辆速度
    speeds = get_vehicle_speed()

    try:
        for vehicle_name in public_type:
            tree = ET.ElementTree(root)
            # 创建 vType 元素
            vtype = ET.SubElement(root, "vType")
            vtype.set("id", 'public_' + vehicle_name)
            vtype.set("vClass", vehicle_name)
            # 设置车辆速度
            vtype.set('maxSpeed', str(speeds[vehicle_name]))

            filename = f"osm.{simulator_name}.public.{vehicle_name}.trips.xml"

            tree.write(os.path.join(public_trips_path, filename), encoding="utf-8", xml_declaration=True)
            root.remove(vtype)
    except Exception as e:
        logging.error("行程文件生成异常：{}".format(e))


# 公共车辆模板
def public_trips_template():
    trip_template = {
        "id": "",
        "type": "{}",
        "depart": "",
        "departLane": "best",
        "from": "",
        "to": "",
    }
    return trip_template


# 初始化公共车辆的trips
def init_public_trips(v_type, number, route, depart):
    trip_template = public_trips_template()
    trip_array = []
    start = ''
    end = ''
    for k, v in route.items():
        start = k
        end = v

    for i in range(number):
        trip = trip_template.copy()
        trip['id'] = k + '_' + v_type + '_' + str(i)
        trip['type'] = 'public_' + v_type
        # 设置公共车辆的出发分布
        trip['depart'] = str(depart)

        trip['from'] = evacuate['public_position'][start]

        arrival_name = evacuate['arrival_position'][start]
        trip['to'] = evacuate['settlements'][arrival_name]
        depart += 1
        trip_array.append(trip)

    return trip_array, end, depart


# 生成行程文件
def generate_public_trips(paths):
    files = glob.glob(os.path.join(paths, 'osm.*.public.*.trips.xml'))
    routes = []
    route_info = pb_info['public_routes']
    for k, v in route_info.items():
        for k1, v1 in v.items():
            route = {'route': {k: k1},
                     'vehicle': v1}
            routes.append(route)

    stop_template = {"edge": "", "parking": "true", "duration": "0"}
    start = 20
    for file in files:
        tree = ET.parse(file)
        root = tree.getroot()
        vehicle_type = root.find('vType').get('vClass')

        # 获取分配策略
        tags_dy = dynamic_public(cfg_path)

        for route in routes:

            for k, v in route['vehicle'].items():
                if vehicle_type == k:
                    route1 = route['route']
                    trips_array, end, depart = init_public_trips(vehicle_type, v, route1, start)
                    start = depart

                    element_trip = 'trip'

                    # 对每一个element进行操作
                    for j, element in enumerate(trips_array):
                        stop_template = stop_template.copy()
                        stop_template['edge'] = evacuate['evacuates'][end]

                        element['id'] = element['id'] + '_' + end

                        trip_point = ET.SubElement(root, element_trip, attrib=element)

                        no_flag = True

                        if end in tags_dy.keys():
                            for pa, va in tags_dy[end].items():

                                if pa == 'all' and va == 0:
                                    no_flag = False

                                if pa == 'all':
                                    for i in range(va - 1):
                                        ET.SubElement(trip_point, "stop", attrib=stop_template.copy())

                                        stop_template1 = stop_template.copy()

                                        # 需要到达的终点
                                        stop_template1['edge'] = element['to']
                                        ET.SubElement(trip_point, "stop", attrib=stop_template1)

                                if pa == k + '_all':
                                    while (va - 1) > 0 and k == pa.split('_')[0]:

                                        ET.SubElement(trip_point, "stop", attrib=stop_template.copy())

                                        stop_template1 = stop_template.copy()

                                        # 需要到达的终点
                                        stop_template1['edge'] = element['to']
                                        ET.SubElement(trip_point, "stop", attrib=stop_template1)
                                        va -= 1

                                if pa == k:
                                    if j < va and k == pa:
                                        ET.SubElement(trip_point, "stop", attrib=stop_template.copy())

                                        stop_template1 = stop_template.copy()

                                        # 需要到达的终点
                                        stop_template1['edge'] = element['to']
                                        ET.SubElement(trip_point, "stop", attrib=stop_template1)

                        # 需要到达的撤离点
                        if no_flag:
                            ET.SubElement(trip_point, "stop", attrib=stop_template.copy())

                            stop_template1 = stop_template.copy()

                            # 需要到达的终点
                            stop_template1['edge'] = element['to']
                            ET.SubElement(trip_point, "stop", attrib=stop_template1)
                            no_flag = True

                    # 标准化xml
                    pretty_xml_str = standardization_xml(root)

                    # 写入文件
                    with open(file, "w", encoding="utf-8") as f:
                        f.write(pretty_xml_str)


def public_run(_cfg_path, _xml_path):
    # 配置初始化
    init_public_cfg(_cfg_path)

    # 初始化公共车辆调度
    init_public_routes('custom')

    # 计算公共车辆类型
    public_types = cal_public_type('custom')

    # 初始化公共车辆行程文件
    init_public_xml(_xml_path, public_types)

    # 生成公共车辆行程文件
    generate_public_trips(_xml_path)


if __name__ == '__main__':
    print('公共车辆调度模块')
