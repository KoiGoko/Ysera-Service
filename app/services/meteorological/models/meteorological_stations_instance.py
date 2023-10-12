from app.services.common.base_config import BaseConfig, getDataUrl

Config = BaseConfig(getDataUrl("meteorological_stations"))
meteorological_stations_Base = Config.getBase()


def getMeteorologicalStationsBase():
    return Config.getBase()


def getMeteorologicalStationsSession():
    return Config.getSession()


def getMeteorologicalStationsEngine():
    return Config.getEngine()
