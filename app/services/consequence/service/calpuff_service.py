from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List

app = FastAPI()

# 模拟数据存储
data_store = {}


class Item(BaseModel):
    name: str


# 服务类，包含增删改查逻辑
class CRUDService:
    def create_item(self, item_id: int, item: str):
        data_store[item_id] = item
        return {"item_id": item_id, "item": item}

    def read_item(self, item_id: int):
        if item_id not in data_store:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"item_id": item_id, "item": data_store[item_id]}

    def update_item(self, item_id: int, updated_item: str):
        if item_id not in data_store:
            raise HTTPException(status_code=404, detail="Item not found")
        data_store[item_id] = updated_item
        return {"item_id": item_id, "updated_item": updated_item}

    def delete_item(self, item_id: int):
        if item_id not in data_store:
            raise HTTPException(status_code=404, detail="Item not found")
        deleted_item = data_store.pop(item_id)
        return {"item_id": item_id, "deleted_item": deleted_item}


# 实例化服务类
crud_service = CRUDService()


# 控制器，依赖于服务类
class ItemController:
    def __init__(self, crud_service: CRUDService = Depends()):
        self.crud_service = crud_service

    def create_item(self, item_id: int, item: Item):
        return self.crud_service.create_item(item_id, item.name)

    def read_item(self, item_id: int):
        return self.crud_service.read_item(item_id)

    def update_item(self, item_id: int, updated_item: Item):
        return self.crud_service.update_item(item_id, updated_item.name)

    def delete_item(self, item_id: int):
        return self.crud_service.delete_item(item_id)


# 实例化控制器类
item_controller = ItemController()


# 增
@app.post("/items/{item_id}", response_model=dict)
async def create_item(item_id: int, item: Item):
    return item_controller.create_item(item_id, item)


# 查
@app.get("/items/{item_id}", response_model=dict)
async def read_item(item_id: int):
    return item_controller.read_item(item_id)


# 改
@app.put("/items/{item_id}", response_model=dict)
async def update_item(item_id: int, updated_item: Item):
    return item_controller.update_item(item_id, updated_item)


# 删
@app.delete("/items/{item_id}", response_model=dict)
async def delete_item(item_id: int):
    return item_controller.delete_item(item_id)
