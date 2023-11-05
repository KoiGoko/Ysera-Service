from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.services.meteorological.services.me_service import get_me_stations
from app.services.meteorological.models.me_data_base import get_me_session

router = APIRouter(
    prefix="/me",
    tags=["meStations"],
    responses={404: {"description": "Not found"}},
)


def get_db():
    db = get_me_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/stations", tags=["meStations"])
async def read_all_stations(db: Session = Depends(get_db)):
    stations = get_me_stations(db)
    return stations
