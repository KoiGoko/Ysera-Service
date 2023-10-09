from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

import app.services.meteorological.model.stations_model as models
import app.services.meteorological.services.stations_service as stations_service
from app.services.meteorological.stations_database import SessionLocal, engine

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
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
