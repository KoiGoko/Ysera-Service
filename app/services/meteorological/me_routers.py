import uvicorn
from fastapi import APIRouter, FastAPI

from app.services.meteorological.services.me_service import get_me_stations
from app.cors.handle_cors import handle_cors

router = APIRouter(
    prefix="/me",
    tags=["meStations"],
    responses={404: {"description": "Not found"}},
)


@router.get("/stations", tags=["meStations"])
async def read_all_stations():
    stations = get_me_stations()
    return stations


if __name__ == '__main__':
    app = FastAPI()
    app.include_router(router)
    handle_cors(app, origins=["http://localhost", "http://localhost:8003"])
    uvicorn.run(app, port=8003)
