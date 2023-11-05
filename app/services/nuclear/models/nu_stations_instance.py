from app.services.common.base_config import BaseConfig, get_data_url

config = BaseConfig(get_data_url("nuclear_stations"))
nu_stations_base = config.get_base()


def get_nu_stations_base():
    return config.get_base()


def get_nu_stations_session():
    return config.get_session()


def get_nu_stations_engine():
    return config.get_engine()
