from sqlalchemy import Column, Integer, String, Float
from app.services.common.base_config import BaseConfig, getDataUrl

Config = BaseConfig(getDataUrl("meteorological_stations"))
Base = Config.getBase()


def getMeteorologicalStationsBase():
    return Config.getBase()


def getMeteorologicalStationsSession():
    return Config.getSession()


def getMeteorologicalStationsEngine():
    return Config.getEngine()


class Stations(Base):
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

    def __str__(self):
        return f"Stations(id={self.id}, station_name='{self.station_name}')"
