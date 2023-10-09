from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml
import os


class BaseConfig:
    def __init__(self, database_url):
        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()

    def getBase(self):
        return self.Base

    def getSession(self):
        return self.SessionLocal()

    def getEngine(self):
        return self.engine

    def test_connection(self):
        with self.SessionLocal() as session:
            session.execute("SELECT 1")

    def __str__(self):
        return f"BaseConfig(engine={self.engine}, SessionLocal='{self.SessionLocal}', Base='{self.Base}')"


def getDataUrl(base_name):
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    data_url = os.path.join(curr_dir, "data_url.yaml")
    with open(data_url, 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    return data[base_name]


if __name__ == '__main__':
    getDataUrl("meteorological_stations")
    Config = BaseConfig(getDataUrl("meteorological_stations"))
    Config.test_connection()
    print(Config)
