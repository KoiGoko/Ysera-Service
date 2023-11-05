from sqlalchemy import Column, Integer, String, Float
from app.services.meteorological.models.me_data_base import me_base


class MeteorologicalStation(me_base):
    __tablename__ = "meteorological_stations"

    id = Column(Integer, primary_key=True, index=True)
    province = Column(String)
    station_id = Column(String)
    station_name = Column(String)
    station_type = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    observed_sea_level_height = Column(Float)
    barometric_sensor_altitude_meters = Column(Float)
    station_note = Column(String)


