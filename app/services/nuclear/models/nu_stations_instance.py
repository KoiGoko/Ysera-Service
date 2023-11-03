from app.services.common.base_config import BaseConfig, get_data_url

Config = BaseConfig(get_data_url("nuclear_stations"))
nuclear_stations_Base = Config.get_base()


def getNuclearStationsBase():
    return Config.get_base()


def getNuclearStationsSession():
    return Config.get_session()


def getNuclearStationsEngine():
    return Config.get_engine()
