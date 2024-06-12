from contextlib import asynccontextmanager
from fastapi import FastAPI
from dependencies import get_settings, get_task_scheduler, kafka_consumer_new_agreements, kafka_consumer_scoring_response, loop, kafka_producer_scoring_request
from kafka.new_agreement_hangler import new_agreement_handler
from kafka.scoring_response_handler import scoring_response_handler
from routers import application_router


@asynccontextmanager
async def lifespan(_ : FastAPI):
    topicname_new_agreement = get_settings().kafka_topic_agreement
    await kafka_consumer_new_agreements.create(topicname_new_agreement, new_agreement_handler)
    loop.create_task(kafka_consumer_new_agreements.start())
    kafka_topic_scoring_response = get_settings().kafka_topic_scoring_response
    await kafka_consumer_scoring_response.create(kafka_topic_scoring_response, scoring_response_handler)
    loop.create_task(kafka_consumer_scoring_response.start())
    
    await kafka_producer_scoring_request.create()
    await kafka_producer_scoring_request.start()
    
    yield
    
    await kafka_consumer_new_agreements.stop()
    await kafka_consumer_scoring_response.stop()
    await kafka_producer_scoring_request.stop()
    
    
app = FastAPI(lifespan=lifespan)

app.include_router(application_router.router)

# Setup background schedulers
scheduler = get_task_scheduler()
scheduler.start_scheduler()

@app.get("/", summary="A welcome message", description="Gets the name of the service")
async def root():
    return {"message": "Service Origination"}