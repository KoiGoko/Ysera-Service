from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi_admin.factory import app as admin_app
from fastapi_admin.depends import get_admin

app = FastAPI()

# 定义 OAuth2 密码模型
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 虚拟数据库，用于存储用户信息
fake_users_db = {
    "admin": {
        "username": "admin",
        "password": "adminpass",
        "email": "admin@example.com",
        "is_active": True,
        "is_superuser": True,
    },
}


# 获取当前用户的依赖项
def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_users_db.get(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


# 用户认证
def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if user and user["password"] == password:
        return user


# FastAPI 后台管理配置
admin_app.config.authenticate = authenticate_user
admin_app.config.current_user = get_current_user


# 定义 FastAPI 路由
@app.get("/")
def read_root(current_user: dict = Depends(get_current_user)):
    return {"message": "Hello, admin!", "current_user": current_user}


# 启动 FastAPI 和 FastAPI Admin
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
