from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.config.app_prefix import evacuate_prefix

app = FastAPI()


@app.get("/hello")
def read_all_stations():

    return 'hello world'


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
