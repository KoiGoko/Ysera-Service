import glob
import os
import xml.etree.ElementTree as ET

__author__ = 'Nan Jia'
__email__ = 'KoiGoko@outlook.com'


def init_sumocfg(_xml_path):
    trips = glob.glob(os.path.join(_xml_path, 'osm.*.trips.xml'))

    trip_name = [path.split('\\')[-1] for path in trips]

    trip_name = ', '.join(trip_name)

    sumo_cfg = _xml_path

    sumo_cfg = os.path.join(sumo_cfg, 'osm.sumocfg')

    tree = ET.parse(sumo_cfg)

    root = tree.getroot()

    route_files_element = root.find('./input/route-files')

    route_files_element.attrib.pop('value')

    # Set the new value
    route_files_element.set('value', trip_name)

    # Save the changes to the XML file
    tree.write(sumo_cfg)


if __name__ == '__main__':
    # init_sumocfg(r'D:\Ysera\Ysera-Core\evacuate\xiapu\xiapu')
    print('sumocfg文件初始化模块')
