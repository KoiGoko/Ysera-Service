from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# 模拟数据存储
gfs_data = {}


class File(BaseModel):
    content: str


# GFS服务类，包含增删改查逻辑
class GFS:
    def create_file(self, file_id: str, file: File):
        gfs_data[file_id] = file.content
        return {"file_id": file_id, "content": file.content}

    def read_file(self, file_id: str):
        if file_id not in gfs_data:
            raise HTTPException(status_code=404, detail="File not found")
        return {"file_id": file_id, "content": gfs_data[file_id]}

    def update_file(self, file_id: str, updated_file: File):
        if file_id not in gfs_data:
            raise HTTPException(status_code=404, detail="File not found")
        gfs_data[file_id] = updated_file.content
        return {"file_id": file_id, "updated_content": updated_file.content}

    def delete_file(self, file_id: str):
        if file_id not in gfs_data:
            raise HTTPException(status_code=404, detail="File not found")
        deleted_content = gfs_data.pop(file_id)
        return {"file_id": file_id, "deleted_content": deleted_content}


# 实例化GFS服务类
gfs_service = GFS()


# GFS控制器，依赖于GFS服务类
class GFSController:
    def __init__(self, gfs_service: GFS = Depends()):
        self.gfs_service = gfs_service

    def create_file(self, file_id: str, file: File):
        return self.gfs_service.create_file(file_id, file)

    def read_file(self, file_id: str):
        return self.gfs_service.read_file(file_id)

    def update_file(self, file_id: str, updated_file: File):
        return self.gfs_service.update_file(file_id, updated_file)

    def delete_file(self, file_id: str):
        return self.gfs_service.delete_file(file_id)


# 实例化GFS控制器类
gfs_controller = GFSController()


# 增
@app.post("/files/{file_id}", response_model=dict)
async def create_file(file_id: str, file: File):
    return gfs_controller.create_file(file_id, file)


# 查
@app.get("/files/{file_id}", response_model=dict)
async def read_file(file_id: str):
    return gfs_controller.read_file(file_id)


# 改
@app.put("/files/{file_id}", response_model=dict)
async def update_file(file_id: str, updated_file: File):
    return gfs_controller.update_file(file_id, updated_file)


# 删
@app.delete("/files/{file_id}", response_model=dict)
async def delete_file(file_id: str):
    return gfs_controller.delete_file(file_id)
