from fastapi import Depends, HTTPException, FastAPI
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

config = Config(".env")

# Mock database for users and their roles
fake_users_db = {
    "user1": {"username": "user1", "password": "password1", "role": "admin"},
    "user2": {"username": "user2", "password": "password2", "role": "user"},
}

# OAuth configuration
oauth = OAuth()
oauth.register(
    name='example',
    client_id=config('OAUTH_CLIENT_ID'),
    client_secret=config('OAUTH_CLIENT_SECRET'),
    authorize_url='https://example.com/oauth/authorize',
    fetch_token_url='https://example.com/oauth/token',
)

# OAuth2PasswordBearer for handling token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# AuthManager class to handle authentication and authorization
class AuthManager:
    def __init__(self):
        pass

    def get_current_user(self, token: str = Depends(oauth2_scheme)):
        user = fake_users_db.get(token)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user

    def is_super_admin(self, current_user: dict = Depends(get_current_user)):
        return current_user.get("role") == "admin"


# FastAPI app
app = FastAPI()

# Create an instance of AuthManager
auth_manager = AuthManager()


# Route that requires super admin privileges
@app.get("/admin")
async def admin_route(current_user: dict = Depends(auth_manager.is_super_admin)):
    return {"message": "Welcome, super admin!"}


# Route for regular users
@app.get("/users/me")
async def read_current_user(current_user: dict = Depends(auth_manager.get_current_user)):
    return {"username": current_user["username"], "role": current_user["role"]}


# Login route
@app.post("/token")
async def login_for_access_token(username: str, password: str):
    user = fake_users_db.get(username)
    if user is None or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": username, "token_type": "bearer"}
