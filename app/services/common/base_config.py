import os

import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


class BaseConfig:
    def __init__(self, database_url):
        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()

    def get_base(self):
        return self.Base

    def get_session(self):
        return self.SessionLocal()

    def get_engine(self):
        return self.engine


def get_data_url(base_name):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    data_url = os.path.join(curr_dir, "data_url.yaml")
    with open(data_url, 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    return data[base_name]


if __name__ == '__main__':
    get_data_url("meteorological_stations")
    Config = BaseConfig(get_data_url("meteorological_stations"))
    print('hello')
