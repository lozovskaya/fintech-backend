from contextlib import asynccontextmanager
from fastapi import FastAPI
from dependencies import get_task_scheduler, kafka_producer
from routers import product_router, agreement_router


@asynccontextmanager
async def lifespan(_ : FastAPI):
    await kafka_producer.create()
    await kafka_producer.start()
    yield
    await kafka_producer.stop()


app = FastAPI(lifespan=lifespan)

app.include_router(product_router.router)
app.include_router(agreement_router.router)

# Setup background schedulers
scheduler = get_task_scheduler()
scheduler.start_scheduler()


@app.get("/", summary="A welcome message", description="Gets the name of the service")
async def root():
    return {"message": "Product Engine service."}