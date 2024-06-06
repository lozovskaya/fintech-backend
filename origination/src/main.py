from contextlib import asynccontextmanager
from fastapi import FastAPI
from dependencies import get_settings, get_task_scheduler, kafka_consumer, loop
from kafka.new_agreement_hangler import new_agreement_handler
from routers import application_router


@asynccontextmanager
async def lifespan(_ : FastAPI):
    topicname = get_settings().kafka_topic_agreement
    await kafka_consumer.create(topicname, new_agreement_handler)
    loop.create_task(kafka_consumer.start())
    yield
    await kafka_consumer.stop()
    
    
app = FastAPI(lifespan=lifespan)

app.include_router(application_router.router)

# Setup background schedulers
scheduler = get_task_scheduler()
scheduler.start_scheduler()

@app.get("/", summary="A welcome message", description="Gets the name of the service")
async def root():
    return {"message": "Service Origination"}