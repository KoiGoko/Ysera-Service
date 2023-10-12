from fastapi import FastAPI, Depends
import uvicorn

from app.cors.handle_cors import handle_cors
from app.services.meteorological import meteorological_routers
from app.services.meteorological.meteorological_routers import meteorological_router, get_db

from fastapi import FastAPI
from app.cors.handle_cors import handle_cors

app = FastAPI()

# Include nuclear routes
app.include_router(meteorological_routers.meteorological_router, tags=["meteorological"], dependencies=[Depends(get_db)])

if __name__ == "__main__":
    import uvicorn
    handle_cors(app, origins=["http://localhost", "http://localhost:3000"])
    uvicorn.run(app)
