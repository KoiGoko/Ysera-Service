from sqlalchemy.orm import Session
import geojson
from app.services.nuclear.models.nu_stations_model import NuclearStation
from app.services.nuclear.models.nu_stations_instance import get_nu_stations_session


def get_nu_stations(db: Session):
    res_stations = db.query(NuclearStation).all()

    features = []
    column_names = NuclearStation.__table__.columns.keys()
    for res_station in res_stations:
        properties = {}
        for column_name in column_names:
            properties[column_name] = getattr(res_station, column_name)

        feature = geojson.Feature(
            geometry=geojson.Point((res_station.longitude, res_station.latitude)),
            properties=properties
        )
        features.append(feature)
    nu_stations_collection = geojson.FeatureCollection(features)
    return nu_stations_collection
