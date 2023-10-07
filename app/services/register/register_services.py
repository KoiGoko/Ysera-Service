from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 用于存储用户注册信息的虚拟数据库
fake_db = {}


# Pydantic模型用于验证注册请求的数据
class UserRegistration(BaseModel):
    username: str
    email: str
    password: str


# 注册路由，接受用户注册信息
@app.post("/register")
async def register_user(user: UserRegistration):
    # 检查用户名是否已经存在
    if user.username in fake_db:
        raise HTTPException(status_code=400, detail="Username already registered")

    # 在实际应用中，你可能还会检查邮箱是否已经被注册，密码的强度等

    # 将用户信息存储到虚拟数据库
    fake_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "password": user.password  # 在实际应用中，应该使用密码哈希而不是明文存储
    }

    return {"message": "User registered successfully"}


if __name__ == "__main__":
    import uvicorn

    # 启动FastAPI应用
    uvicorn.run(app, host="127.0.0.1", port=8000)
