from fastapi import Depends, FastAPI
from fastapi import APIRouter
from sqlalchemy.orm import Session
import app.services.meteorological.services.meteorological_stations_service as meteorological_stations_service
from app.cors.handle_cors import handle_cors
from app.services.meteorological.models.meteorological_stations_instance import getMeteorologicalStationsSession

meteorological_router = APIRouter()
app = FastAPI()


def get_db():
    db = getMeteorologicalStationsSession()
    try:
        yield db
    finally:
        db.close()


@app.get("/me_stations_info", tags=["meteorological"])
async def read_all_stations(db: Session = Depends(get_db)):
    stations = meteorological_stations_service.get_meteorological_stations_info(db)
    return stations

# @meteorological_router.get("/me_stations_with_distance")
# def read_all_stations(db: Session = Depends(get_db)):
#     stations = stations_service.get_meteorological_station_info(db)
#     return stations
#
#
# @meteorological_router.get("/me_stations_with_nearest")
# def read_all_stations(db: Session = Depends(get_db)):
#     stations = stations_service.get_meteorological_station_info(db)
#     return stations
handle_cors(app, origins=["http://localhost", "http://localhost:8001"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8001)


