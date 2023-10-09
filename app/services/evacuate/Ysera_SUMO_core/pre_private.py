import os
import xml.etree.ElementTree as ET
import glob
import logging
import itertools
from evacuate.src.utils import input_args
from evacuate.src.utils import standardization_xml
from evacuate.src.pre_vehicle import get_vehicle_speed
from evacuate.src.pre_vehicle import init_vehicle_cfg
from evacuate.src.utils import get_similar_type_count
import evacuate.src.evacuate_distribution as evacuate_distribution

_author_ = 'Nan Jia'
_email_ = 'KoiGoko@outlook.com'

# 非公共车辆模拟环境预处理模块

# 配置日志记录器
logging.basicConfig(filename='../sumo.log', level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')

evacuate = {}
vehicle = {}
cfg_path = ''


# 配置初始化
def init_private_cfg(_cfg_path):
    _evacuate = input_args(_cfg_path, 'evacuate')
    _vehicle = input_args(_cfg_path, 'vehicle')
    global cfg_path
    cfg_path = _cfg_path
    evacuate.update(_evacuate)
    vehicle.update(_vehicle)


def distribute_cars():
    # 车辆分配表
    dist_cars = evacuate['vehicle_number']

    return dist_cars


# 计算车辆类型，车辆类型会用到我的sumo的形成文件的命名
def cal_private_trips_type():
    vehicles = []
    for k, v in evacuate['vehicle_number'].items():
        vehicles.append(list(v.keys()))
    # 取并集
    merges = list(itertools.chain.from_iterable(vehicles))
    vehicle_name = list(set(merges))
    return vehicle_name


# 初始化trips.xml文件
def init_trips(_xml_path, _vehicle_names):
    # 模拟场景名称
    simulator_name = evacuate['simulator']['name']

    # 清除已经存在的trips文件
    files = glob.glob(os.path.join(_xml_path, f'osm.{simulator_name}.*.trips.xml'))
    if not files:
        print('新的非公共车辆行程文件初始化')
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

    # 配置初始化
    init_vehicle_cfg(cfg_path)
    speeds = get_vehicle_speed()

    try:
        for vehicle_name in _vehicle_names:
            tree = ET.ElementTree(root)
            # 创建 vType 元素
            vtype = ET.SubElement(root, "vType")
            vtype.set("id", vehicle_name)
            vtype.set("vClass", vehicle_name)
            # 设置车辆速度
            vtype.set('maxSpeed', str(speeds[vehicle_name]))

            filename = f"osm.{simulator_name}.{vehicle_name}.trips.xml"

            tree.write(os.path.join(_xml_path, filename), encoding="utf-8", xml_declaration=True)
            root.remove(vtype)
    except Exception as e:
        logging.error("行程文件生成异常：{}".format(e))


# trip的模板
def trips_template(pattern):
    trip_template = {}
    # 根据边生成路线
    if pattern == 'lane':
        trip_template = {
            "id": "",
            "type": "",
            "depart": "",
            "departLane": "best",
            "from": "",
            "to": "",
        }

    return trip_template


# 计算非公共车辆行程
def generate_private_routes():
    # 路线信息
    _route_infos = []

    # 撤离分配
    evacuate_points = evacuate['evacuates']
    settle_points = evacuate['settlements']
    routes = evacuate['routes']

    for k, v in routes.items():
        route_info = {k: settle_points[v], 'priority': evacuate['evacuation_order'][k]}

        _route_infos.append(route_info)

    # 根据 priority 进行排序
    _route_infos = sorted(_route_infos, key=lambda x: x['priority'])

    return _route_infos


# 装配每一辆车的行程
def generate_private_trips(vehicle_type, vehicle_info, routes):
    trips_array = []
    print(vehicle_info)
    evacuates = evacuate['evacuates']
    distribution = evacuate['evacuate_distribution']

    template = trips_template('lane')
    template['type'] = vehicle_type

    depart = 0

    type_count = get_similar_type_count(cfg_path, vehicle_type)

    uniforms = evacuate_distribution.uniform_distribution(type_count)
    evacuation_order = evacuate['evacuation_order']
    evacuation_delay = evacuate['evacuation_delay']

    for k, v in vehicle_info.items():
        print(k, v)

        start = evacuates[k]
        for route in routes:
            if k in route.keys():
                to = route.get(k)
                priority = route.get('priority')
                break

        index = 0
        for i in range(v):
            trip = template.copy()
            trip['id'] = f"{k}_{vehicle_type}_{index}"
            index += 1
            # xml格式只接受字符串
            trip['depart'] = str(uniforms[depart] + (evacuation_order[k] * evacuation_delay))
            depart += 1
            priority = round(priority, 2)

            depart = round(depart, 2)
            trip['from'] = start
            trip['to'] = to

            trips_array.append(trip)
    return trips_array


# 装配trips文件
def generate_trips(paths):
    files = glob.glob(os.path.join(paths, 'osm.*.*.trips.xml'))

    routes = generate_private_routes()
    vehicle_number = distribute_cars()
    stop_template = {"edge": "", "parking": "true", "duration": "0"}

    try:
        for file in files:
            tree = ET.parse(file)
            root = tree.getroot()
            vehicle_type = root.find('vType').get('id')

            vehicle_info = {}
            for k, v in vehicle_number.items():
                number = v.get(vehicle_type)
                if number is None:
                    continue
                vehicle_info[k] = number
            trips_array = generate_private_trips(vehicle_type, vehicle_info, routes)

            element_trip = 'trip'
            # 对每一个element进行操作
            for element in trips_array:
                stop_template['edge'] = element['to']
                trip_point = ET.SubElement(root, element_trip, attrib=element)
                ET.SubElement(trip_point, "stop", attrib=stop_template)

            # 标准化xml
            pretty_xml_str = standardization_xml(root)

            # 写入文件
            with open(file, "w", encoding="utf-8") as f:
                f.write(pretty_xml_str)

    except Exception as e:
        logging.error("行程文件写入错误：{}".format(e))


def private_run(_cfg_path, _xml_path):
    init_private_cfg(_cfg_path)

    # 获取私家车车辆类型
    private_types = cal_private_trips_type()

    # 初始化私家车行程文件
    init_trips(_xml_path, private_types)

    # 生成私家车行程文件
    generate_trips(_xml_path)


if __name__ == '__main__':
    print('非公共车辆模拟环境预处理模块')
