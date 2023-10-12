from sqlalchemy.orm import Session
import geojson
from app.services.nuclear.models.nuclear_stations_model import NuclearStation
from app.services.utils.query_results_to_json import query_results_to_json


def get_nuclear_stations_info(db: Session):
    res = db.query(NuclearStation).all()

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


#
# # 添加核电厂信息
# def add_nuclear_station(db: Session, name: str, latitude: float, longitude: float):
#     new_station = Stations(name=name, latitude=latitude, longitude=longitude)
#     db.add(new_station)
#     db.commit()
#     db.refresh(new_station)
#     return new_station
#
#
# # 更新核电厂信息
# def update_nuclear_station(db: Session, station_id: int, name: str, latitude: float, longitude: float):
#     station = db.query(Stations).filter(Stations.id == station_id).first()
#
#     if station:
#         station.name = name
#         station.latitude = latitude
#         station.longitude = longitude
#         db.commit()
#         db.refresh(station)
#         return station
#     else:
#         return None
#
#
# 删除核电厂信息
def delete_nuclear_station(db: Session, station_id: int):
    station = db.query(NuclearStation).filter(NuclearStation.id == station_id).first()

    if station:
        db.delete(station)
        db.commit()
        return True
    else:
        return False
