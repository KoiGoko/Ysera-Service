from typing import List, Optional
from app.nuclear.nuclear import Nuclear
from app.nuclear.repositories.nuclear_repository import NuclearRepository


class UserService:
    def __init__(self, user_repository: NuclearRepository):
        self.user_repository = user_repository

    def get_user(self, user_id: int) -> Optional[Nuclear]:
        return self.user_repository.get_user(user_id)

    def create_user(self, user: Nuclear) -> Nuclear:
        return self.user_repository.create_user(user)

    def get_users(self) -> List[Nuclear]:
        return self.user_repository.get_users()
