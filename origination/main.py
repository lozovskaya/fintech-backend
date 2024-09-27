from fastapi import FastAPI
from src.routers import application_router
from src.models import database

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(application_router.router)

@app.get("/")
async def root():
    return {"message": "Service Origination"}