import geojson
from sqlalchemy.orm import Session
from fastapi import Depends

from app.services.meteorological.models.me_stations_model import MeteorologicalStation
from app.services.utils.res_to_json import res_to_json
from app.services.meteorological.models.me_data_base import get_me_session


def get_me_stations():
    db = get_me_session()
    res = db.query(MeteorologicalStation).all()

    # json_data = res_to_json(res)

    # features = []
    # for item in json_data:
    #     properties = {}  # 创建一个空字典用于存储属性键值对
    #     for key, value in item.items():
    #         properties[key] = value  # 将数据中的键值对添加到属性字典中
    #
    #     feature = geojson.Feature(
    #         geometry=geojson.Point((item["longitude"], item["latitude"])),
    #         properties=properties  # 使用动态属性字典
    #     )
    #     features.append(feature)
    # feature_collection = geojson.FeatureCollection(features)

    return res
