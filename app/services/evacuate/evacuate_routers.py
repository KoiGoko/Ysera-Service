from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.config.app_prefix import evacuate_prefix


@app.get(f"{evacuate_prefix}/hello")
def read_all_stations():
    return 'hello world'
