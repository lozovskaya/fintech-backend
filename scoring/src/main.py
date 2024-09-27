from contextlib import asynccontextmanager
from fastapi import FastAPI
from dependencies import get_settings, kafka_consumer, loop, kafka_producer
from routers import scoring_router
from kafka.scoring_request_hangler import scoring_request_handler


@asynccontextmanager
async def lifespan(_ : FastAPI):
    topicname = get_settings().kafka_topic_scoring_request
    await kafka_consumer.create(topicname, scoring_request_handler)
    loop.create_task(kafka_consumer.start())
    await kafka_producer.create()
    await kafka_producer.start()
    yield
    await kafka_consumer.stop()
    await kafka_producer.stop()
    
    
app = FastAPI(lifespan=lifespan)


app.include_router(scoring_router.router)

@app.get("/", summary="A welcome message", description="Gets the name of the service")
async def root():
    return {"message": "Scoring Origination"}