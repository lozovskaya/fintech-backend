from fastapi import FastAPI
from dependencies import get_task_scheduler
from routers import application_router
from models import database

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(application_router.router)

# Setup background schedulers
scheduler = get_task_scheduler()
scheduler.start_scheduler()

@app.get("/", summary="A welcome message", description="Gets the name of the service")
async def root():
    return {"message": "Service Origination"}