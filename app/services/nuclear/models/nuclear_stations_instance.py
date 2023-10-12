from app.services.common.base_config import BaseConfig, getDataUrl

Config = BaseConfig(getDataUrl("nuclear_stations"))
nuclear_stations_Base = Config.getBase()


def getNuclearStationsBase():
    return Config.getBase()


def getNuclearStationsSession():
    return Config.getSession()


def getNuclearStationsEngine():
    return Config.getEngine()
