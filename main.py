from fastapi import FastAPI
from typing import Union
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
import uvicorn

app = FastAPI()


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

if __name__ == '__main__':
    uvicorn.run(app)

