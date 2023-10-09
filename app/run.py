from fastapi import FastAPI


app = FastAPI()

app.include_router(router1, prefix="/api/v1")
app.include_router(router2, prefix="/api/v1")
