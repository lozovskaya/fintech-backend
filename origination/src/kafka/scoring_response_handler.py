import logging
from flask import json

from dependencies import get_repo
from cruds import crud_applications
from models.enums import ApplicationStatus



async def scoring_response_handler(msg):
    message = json.loads(msg.value.decode('ascii'))
    logging.info(f"Message from Kafka consumer scoring response: {message}")
    async for repository in get_repo():
        new_status = ApplicationStatus[message["scoring_result"]]
        await crud_applications.update_status_of_agreement_id(repository, int(message["agreement_id"]), new_status)
    