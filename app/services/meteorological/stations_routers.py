from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
import model.stations_model as models
import service.stations_service as stations_service
from model.stations_model import getMeteorologicalStationsSession, getMeteorologicalStationsEngine

engine = getMeteorologicalStationsEngine()
models.Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = getMeteorologicalStationsSession()
    try:
        yield db
    finally:
        db.close()


@app.get("/hello")
def read_all_stations(db: Session = Depends(get_db)):
    stations = stations_service.get_station_info(db)
    return stations


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
