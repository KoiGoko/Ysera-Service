from sqlalchemy.orm import Session
import geojson
from ..model.stations_model import Stations
from app.services.utils.query_results_to_json import query_results_to_json


def get_station_info(db: Session):
    res = db.query(Stations).all()

    # 将结果列表转换为 JSON 字符串
    json_data = query_results_to_json(res)

    features = []
    for item in json_data:
        properties = {}  # 创建一个空字典用于存储属性键值对
        for key, value in item.items():
            properties[key] = value  # 将数据中的键值对添加到属性字典中

        # 创建一个 GeoJSON 特征
        feature = geojson.Feature(
            geometry=geojson.Point((item["longitude"], item["latitude"])),
            properties=properties  # 使用动态属性字典
        )
        features.append(feature)

    # 创建一个 GeoJSON 特征集合
    feature_collection = geojson.FeatureCollection(features)

    return feature_collection

def getStationsWithDistance() {
    return axios.get('/api/stations/distance')
}

def getStation
