

import logging
from flask import json


async def new_agreement_handler(msg):
    message = json.loads(msg.value.decode('ascii'))
    logging.info(f"Message from Kafka consumer: {message}")