from pydantic import BaseModel


class WeatherStation(BaseModel):
    id: str
    province: str
    station_id: str
    station_name: str
    station_type: str
    latitude: float
    longitude: float
    # 观测场拔海高度
    observed_sea_level_height: float
    # 气压传感器拔海高度
    barometric_sensor_altitude_meters: float
    # 气象站备注
    station_note: str
