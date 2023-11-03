import uvicorn
from fastapi import FastAPI

from app.cors.handle_cors import handle_cors
from app.services.meteorological.me_routers import router as me_router
from app.services.nuclear.nu_routers import router as nu_router

app = FastAPI()

app.include_router(me_router)
app.include_router(nu_router)

handle_cors(app, origins=["http://localhost", "http://localhost:8001"])
uvicorn.run(app, port=8001)
