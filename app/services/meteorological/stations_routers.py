from fastapi import Depends, FastAPI
from fastapi import APIRouter
from sqlalchemy.orm import Session
import services.stations_service as stations_service
from models.stations_model import getMeteorologicalStationsSession

router = APIRouter()


def get_db():
    db = getMeteorologicalStationsSession()
    try:
        yield db
    finally:
        db.close()


@router.get("/me_stations_info")
def read_all_stations(db: Session = Depends(get_db)):
    stations = stations_service.get_station_info(db)
    return stations


@router.get("/me_stations_with_distance")
def read_all_stations(db: Session = Depends(get_db)):
    stations = stations_service.get_station_info(db)
    return stations


@router.get("/me_stations_with_nearest")
def read_all_stations(db: Session = Depends(get_db)):
    stations = stations_service.get_station_info(db)
    return stations


app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
