from evacuate.src.utils import input_args

__author__ = 'Nan Jia'
__email__ = 'KoiGoko@outlook.com'

# 车辆情况预处理模块

# 设置vehicle.yaml文件的路径
cfg_path = ''


def init_vehicle_cfg(_cfg_path):
    global cfg_path
    cfg_path = _cfg_path


def get_vehicle_speed():
    # 读取已经自定义好的车辆速度
    vehicle_speed = input_args(cfg_path, 'vehicle')['vehicle_speed']
    return vehicle_speed


def get_vehicle_length():
    # 读取已经定义好的车辆长度,车辆长度将会是计算道路拥堵的重要参数
    vehicle_length = input_args(cfg_path, 'vehicle')['vehicle_length']
    return vehicle_length


def get_vehicle_capacity():
    # 读取已经定义好的车辆载客量
    vehicle_capacity = input_args(cfg_path, 'vehicle')['vehicle_capacity']
    return vehicle_capacity


def get_vehicle_type():
    vehicle_type = input_args(cfg_path, 'vehicle')['vehicle_type']
    return vehicle_type


if __name__ == '__main__':
    print('车辆情况预处理模块')
