from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.services.nuclear.models.nuclear_stations_instance import nuclear_stations_Base


class NuclearStation(nuclear_stations_Base):
    __tablename__ = "nuclear_stations"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String)
    nuclear_stations_name = Column(String)
    reactor_type = Column(String)
    status = Column(String)
    location = Column(String)
    reference_unit_power = Column(Integer)
    total_generating_capacity = Column(Integer)
    initial_grid_connection_time = Column(String)
    longitude = Column(Float)
    latitude = Column(Float)
    elevation = Column(Float)
