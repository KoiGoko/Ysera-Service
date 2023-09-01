from fastapi import FastAPI
from typing import Union
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
import uvicorn
from fastapi_admin.app import app as admin_app
from fastapi import FastAPI

app = FastAPI()
app.mount("/admin", admin_app)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

# # 创建AdminSite实例
# site = AdminSite(settings=Settings(database_url_async='sqlite+aiosqlite:///amisadmin.db'))
#
# # 挂载后台管理系统
# site.mount_app(app)


