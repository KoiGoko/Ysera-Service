from typing import List, Optional
from app.nuclear.nuclear import Nuclear


class NuclearRepository:
    def get_user(self, user_id: int) -> Optional[Nuclear]:
        # Database retrieval logic specific to user data
        pass

    def create_user(self, user: Nuclear) -> Nuclear:
        # Database insertion logic for user data
        pass

    def get_users(self) -> List[Nuclear]:
        # Database retrieval logic for multiple users
        pass
