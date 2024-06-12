import logging
from flask import json
from dependencies import get_settings, product_engine_client, kafka_producer
from models.schemas import KafkaProducerScoringResponseMessage
from models.enums import ScoringStatus


async def scoring_request_handler(msg):
    message = json.loads(msg.value.decode('ascii'))
    logging.info(f"Message from Kafka consumer: {message}")
    agreements = product_engine_client.get_all_active_agreements_by_client(message["client_id"])
    if len(agreements) == 1 and agreements[0] == message["agreement_id"]:
        logging.info(f"Sending to {get_settings().kafka_topic_scoring_response}: {message['agreement_id']}, {ScoringStatus.APPROVED.name}")
        await kafka_producer.send_message(get_settings().kafka_topic_scoring_response, 
                                    KafkaProducerScoringResponseMessage(agreement_id=int(message["agreement_id"]), 
                                                                        scoring_result=ScoringStatus.APPROVED.name))
    else:
        logging.info(f"Sending to {get_settings().kafka_topic_scoring_response}: {message['agreement_id']}, {ScoringStatus.REJECTED.name}")
        await kafka_producer.send_message(get_settings().kafka_topic_scoring_response, 
                                    KafkaProducerScoringResponseMessage(agreement_id=int(message["agreement_id"]), 
                                                                        scoring_result=ScoringStatus.REJECTED.name))