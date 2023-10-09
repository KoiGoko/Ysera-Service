from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# 模拟数据存储
sources_data = {}


class NuclideSource(BaseModel):
    nuclide: str
    activity: float
    location: str


# 核素源项服务类，包含增删改查逻辑
class NuclideSourceService:
    def create_source(self, source_id: str, source: NuclideSource):
        sources_data[source_id] = source
        return {"source_id": source_id, "source": source.dict()}

    def read_source(self, source_id: str):
        if source_id not in sources_data:
            raise HTTPException(status_code=404, detail="Source not found")
        return {"source_id": source_id, "source": sources_data[source_id].dict()}

    def update_source(self, source_id: str, updated_source: NuclideSource):
        if source_id not in sources_data:
            raise HTTPException(status_code=404, detail="Source not found")
        sources_data[source_id] = updated_source
        return {"source_id": source_id, "updated_source": updated_source.dict()}

    def delete_source(self, source_id: str):
        if source_id not in sources_data:
            raise HTTPException(status_code=404, detail="Source not found")
        deleted_source = sources_data.pop(source_id)
        return {"source_id": source_id, "deleted_source": deleted_source.dict()}


# 实例化核素源项服务类
source_service = NuclideSourceService()


# 核素源项控制器，依赖于核素源项服务类
class NuclideSourceController:
    def __init__(self, source_service: NuclideSourceService = Depends()):
        self.source_service = source_service

    def create_source(self, source_id: str, source: NuclideSource):
        return self.source_service.create_source(source_id, source)

    def read_source(self, source_id: str):
        return self.source_service.read_source(source_id)

    def update_source(self, source_id: str, updated_source: NuclideSource):
        return self.source_service.update_source(source_id, updated_source)

    def delete_source(self, source_id: str):
        return self.source_service.delete_source(source_id)


# 实例化核素源项控制器类
source_controller = NuclideSourceController()


# 增
@app.post("/sources/{source_id}", response_model=dict)
async def create_source(source_id: str, source: NuclideSource):
    return source_controller.create_source(source_id, source)


# 查
@app.get("/sources/{source_id}", response_model=dict)
async def read_source(source_id: str):
    return source_controller.read_source(source_id)


# 改
@app.put("/sources/{source_id}", response_model=dict)
async def update_source(source_id: str, updated_source: NuclideSource):
    return source_controller.update_source(source_id, updated_source)


# 删
@app.delete("/sources/{source_id}", response_model=dict)
async def delete_source(source_id: str):
    return source_controller.delete_source(source_id)
