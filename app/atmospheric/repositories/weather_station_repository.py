from typing import List, Optional
from app.atmospheric.weather_station import WeatherStation


class NuclearRepository:
    def get_user(self, user_id: int) -> Optional[WeatherStation]:
        # Database retrieval logic specific to user data
        pass

    def create_user(self, user: WeatherStation) -> WeatherStation:
        # Database insertion logic for user data
        pass

    def get_users(self) -> List[WeatherStation]:
        # Database retrieval logic for multiple users
        pass
