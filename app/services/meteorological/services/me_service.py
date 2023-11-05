import geojson
from sqlalchemy.orm import Session
from app.services.meteorological.models.me_stations_model import MeteorologicalStation


def get_me_stations(db: Session):
    me_stations = db.query(MeteorologicalStation).all()

    features = []
    column_names = MeteorologicalStation.__table__.columns.keys()
    for me_station in me_stations:
        properties = {}
        for column_name in column_names:
            properties[column_name] = getattr(me_station, column_name)

        feature = geojson.Feature(
            geometry=geojson.Point((me_station.longitude, me_station.latitude)),
            properties=properties
        )
        features.append(feature)
    me_stations_collection = geojson.FeatureCollection(features)
    return me_stations_collection
