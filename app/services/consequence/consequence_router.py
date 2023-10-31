import io

from fastapi import FastAPI
from starlette.responses import StreamingResponse

from app.cors.handle_cors import handle_cors
from nc_to_vector import create_upload_file

app = FastAPI()


@app.get("/consequence/evacuate", )
def read_all_stations():
    nc_file = 'dose01.nc'
    dose_data_bytes = create_upload_file()

    return StreamingResponse(io.BytesIO(dose_data_bytes))


handle_cors(app, origins=["http://localhost", "http://localhost:8003"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8003)
