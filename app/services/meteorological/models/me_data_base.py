from app.services.common.base_config import BaseConfig, get_data_url

config = BaseConfig(get_data_url("meteorological_stations"))
me_base = config.get_base()


def get_me_base():
    return config.get_base()


def get_me_session():
    return config.get_session()


def get_me_engine():
    return config.get_engine()
