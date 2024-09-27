from fastapi import FastAPI
from models import database
from dependencies import get_task_scheduler
from routers import product_router, agreement_router

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(product_router.router)
app.include_router(agreement_router.router)

# Setup background schedulers
scheduler = get_task_scheduler()
scheduler.start_scheduler()

@app.get("/", summary="A welcome message", description="Gets the name of the service")
async def root():
    return {"message": "Product Engine service."}