# auth.py - 模块化的身份验证逻辑

from fastapi_auth.auth_app import Auth
from fastapi_auth.auth_settings import AuthSettings
from fastapi_auth.manager import UserDatabaseManager

auth_settings = AuthSettings(secret="mysecret", access_lifetime=3600, refresh_lifetime=3600)
auth = Auth(auth_settings)

users_db = UserDB()  # 实际项目中，应使用真实的数据库


# 用户认证逻辑
def authenticate_user(username, password):
    user = users_db.authenticate_user(username=username, password=password)
    return user


# 创建访问令牌逻辑
def create_access_token(data):
    return auth.create_access_token(data=data)


# 用户管理逻辑
def get_user_by_username(username):
    return users_db.get_user_by_username(username)
