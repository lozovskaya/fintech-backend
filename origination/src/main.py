from fastapi import FastAPI
from routers import application_router
from models import database

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(application_router.router)


@app.get("/", summary="A welcome message", description="Gets the name of the service")
async def root():
    return {"message": "Service Origination"}