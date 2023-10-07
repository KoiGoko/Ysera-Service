from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

config = Config(".env")  # 使用配置文件存储敏感信息

oauth = OAuth()

# 配置 OAuth2 客户端信息
oauth.register(
    name='example',
    client_id=config('OAUTH_CLIENT_ID'),
    client_secret=config('OAUTH_CLIENT_SECRET'),
    authorize_url='https://example.com/oauth/authorize',
    authorize_params=None,
    authorize_params_defaults=None,
    authorize_params_required=None,
    authorize_extra_params=None,
    authorize_response=None,
    authorize_redirect=None,
    authorize_scopes=None,
    client_kwargs=None,
    fetch_token_url='https://example.com/oauth/token',
    fetch_token_params=None,
    fetch_token_params_defaults=None,
    fetch_token_params_required=None,
    fetch_token_extra_params=None,
    fetch_token_headers=None,
    fetch_token_response=None,
    fetch_token_scope=None,
)


async def fetch_user(token):
    # 使用 OAuth2 令牌获取用户信息的逻辑
    # 请根据您的 OAuth2 服务提供商的要求实现此逻辑
    pass


# 用于获取 OAuth2 用户信息的路由
async def get_user_info(request):
    token = await oauth.example.authorize_access_token(request)
    user_info = await fetch_user(token)
    return user_info


from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

# 用于验证用户名和密码的虚拟数据库
fake_users_db = {
    "user1": {
        "username": "user1",
        "password": "password1"
    },
    "user2": {
        "username": "user2",
        "password": "password2"
    }
}

# OAuth2PasswordBearer 类用于处理身份验证令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 获取当前用户的依赖项
def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_users_db.get(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


# 路由，要求登录后才能访问
@app.get("/users/me")
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"]}


# 登录路由，接受用户名和密码并返回令牌
@app.post("/token")
async def login_for_access_token(username: str, password: str):
    user = fake_users_db.get(username)
    if user is None or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": username, "token_type": "bearer"}
