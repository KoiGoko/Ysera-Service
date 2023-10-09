import yaml
import os
import logging
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

_author_ = 'Nan Jia'
_email_ = 'KoiGoko@outlook.com'

# 配置日志记录器
logging.basicConfig(filename='../sumo.log', level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')


# 读取参数
def input_args(_cfg_path, select):
    # 参数文件
    _cfg_yaml = ['evacuate.yaml', 'vehicle.yaml', 'environment.yaml', 'result.yaml', 'person.yaml']
    with open(os.path.join(_cfg_path, _cfg_yaml[0]), encoding='utf-8') as f:
        _evacuate = yaml.load(f, Loader=yaml.FullLoader)
        if select == 'evacuate':
            return _evacuate

    with open(os.path.join(_cfg_path, _cfg_yaml[1]), encoding='utf-8') as f:
        _vehicle = yaml.load(f, Loader=yaml.FullLoader)
        if select == 'vehicle':
            return _vehicle

    with open(os.path.join(_cfg_path, _cfg_yaml[2]), encoding='utf-8') as f:
        _environment = yaml.load(f, Loader=yaml.FullLoader)
        if select == 'environment':
            return _environment

    with open(os.path.join(_cfg_path, _cfg_yaml[3]), encoding='utf-8') as f:
        _result = yaml.load(f, Loader=yaml.FullLoader)
        if select == 'result':
            return _result

    with open(os.path.join(_cfg_path, _cfg_yaml[4]), encoding='utf-8') as f:
        _person = yaml.load(f, Loader=yaml.FullLoader)
        if select == 'person':
            return _person

    if select == 'all':
        return _evacuate, _vehicle, _environment, _result, _person
    else:
        raise ValueError('select must be in evacuate, capacity, environment, result ro all')


# 字符串标准化
def standardization_xml(root):
    # 创建字符串
    xml_str = ET.tostring(root, encoding="utf-8")
    # 创建minidom解析器
    dom = minidom.parseString(xml_str)
    # 格式化XML
    pretty_xml_str = dom.toprettyxml(indent="  ")
    return pretty_xml_str


def get_similar_type_count(xml_path, type_name):
    evacuate = input_args(xml_path, 'evacuate')
    vehicle_data = evacuate['vehicle_number']

    vehicle_counts = {}

    for region in vehicle_data:
        for vehicle_type, count in vehicle_data[region].items():
            if vehicle_type in vehicle_counts:
                vehicle_counts[vehicle_type] += count
            else:
                vehicle_counts[vehicle_type] = count

    return vehicle_counts[type_name]


def get_distribute(count, distribute_type):
    pass


if __name__ == '__main__':
    input_args(r'D:\Ysera\Ysera-Core\evacuate\cfg', 'all')
    # get_similar_type_count(r'E:\Ysera-Core\evacuate\cfg', 'bus')
    print('工具函数模块')
