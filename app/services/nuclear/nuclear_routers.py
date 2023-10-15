from fastapi import Depends, FastAPI
from fastapi import APIRouter
from sqlalchemy.orm import Session

import app.services.nuclear.services.nuclear_stations_service as nuclear_stations_service
from app.cors.handle_cors import handle_cors
from app.services.nuclear.models.nuclear_stations_instance import getNuclearStationsSession

nuclear_router = APIRouter()
app = FastAPI()


def get_db():
    db = getNuclearStationsSession()
    try:
        yield db
    finally:
        db.close()


@app.get("/nu_stations_info", tags=["nuclear"])
async def read_all_stations(db: Session = Depends(get_db)):
    stations = nuclear_stations_service.get_nuclear_stations_info(db)
    return stations

if __name__ == "__main__":
    import uvicorn
    handle_cors(app, origins=["http://localhost", "http://localhost:8000"])
    uvicorn.run(app, port=8002)
