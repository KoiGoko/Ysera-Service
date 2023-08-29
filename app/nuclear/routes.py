from typing import List
from fastapi import APIRouter, Depends
from app.models.user import User
from app.modules.user.services.user_service import UserService

router = APIRouter()


@router.get("/users/", response_model=List[User])
async def get_users(user_service: UserService = Depends()):
    return user_service.get_users()


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, user_service: UserService = Depends()):
    return user_service.get_user(user_id)


@router.post("/users/", response_model=User)
async def create_user(user: User, user_service: UserService = Depends()):
    return user_service.create_user(user)
