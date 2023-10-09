from sqlalchemy.orm import Session
import geojson
from app.services.meteorological.models.stations_model import Station
from app.services.utils.query_results_to_json import query_results_to_json
from geopy.distance import geodesic


def get_station_info(db: Session):
    res = db.query(Station).all()

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


def getStationsWithDistance(db_session: Session, lon, lat, distance):
    distance_expr = geodesic(
        [Station.latitude, Station.longitude], [lon, lat]).kilometers

    nearest_station = (
        db_session.query(Station)
        .order_by(distance_expr)
        .filter(distance_expr <= distance)
        .first()
    )
    return nearest_station


def getStationsWithNearest(db_session: Session, lon, lat, distance):
    distance_expr = geodesic(
        [Station.latitude, Station.longitude], [lon, lat]).kilometers

    nearest_station = (
        db_session.query(Station)
        .order_by(distance_expr)
        .filter(distance_expr <= distance)
        .first()
    )
    return nearest_station
