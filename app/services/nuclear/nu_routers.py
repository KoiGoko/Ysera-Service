from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

import app.services.nuclear.services.nu_stations_service as nuclear_stations_service
from app.services.nuclear.models.nu_stations_instance import getNuclearStationsSession

router = APIRouter(
    prefix="/nu",
    tags=["nuStations"],
    responses={404: {"description": "Not found"}},
)


def get_db():
    db = getNuclearStationsSession()
    try:
        yield db
    finally:
        db.close()


@router.get("/stations", tags=["nuStations"])
async def read_all_stations(db: Session = Depends(get_db)):
    stations = nuclear_stations_service.get_nuclear_stations_info(db)
    return stations

if __name__ == '__main__':
    import uvicorn
    from fastapi import FastAPI
    from app.cors.handle_cors import handle_cors

    app = FastAPI()
    app.include_router(router)
    handle_cors(app, origins=["http://localhost", "http://localhost:8005"])
    uvicorn.run(app, port=8005)
