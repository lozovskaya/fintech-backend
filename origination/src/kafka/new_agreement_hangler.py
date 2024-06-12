import logging
from flask import json

from dependencies import get_repo, kafka_producer_scoring_request, get_settings
from cruds import crud_applications
from models.enums import ApplicationStatus
from models.schemas import ApplicationKafkaRequestToScoring

async def new_agreement_handler(msg):
    message = json.loads(msg.value.decode('ascii'))
    logging.info(f"Message from Kafka consumer, new_agreement: {message}")
    message["status"] = ApplicationStatus.CREATED.name
    async for repository in get_repo():
            await crud_applications.create_application(repository, message)
            await kafka_producer_scoring_request.send_message(get_settings().kafka_topic_scoring_request,
                                                                ApplicationKafkaRequestToScoring(agreement_id=message["agreement_id"], 
                                                                                                 client_id=message["client_id"]))

