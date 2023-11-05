from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.services.nuclear.services.nu_stations_service import get_nu_stations
from app.services.nuclear.models.nu_stations_instance import get_nu_stations_session

router = APIRouter(
    prefix="/nu",
    tags=["nuStations"],
    responses={404: {"description": "Not found"}},
)


def get_db():
    db = get_nu_stations_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/stations", tags=["nuStations"])
async def read_all_stations(db: Session = Depends(get_db)):
    stations = get_nu_stations(db)

    return stations
