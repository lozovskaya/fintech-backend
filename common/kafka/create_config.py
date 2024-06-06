from typing import Dict
from pydantic_settings import BaseSettings


def create_kafka_config_from_settings(settings: BaseSettings) -> Dict:
    return {"bootstrap_servers": f"{settings.kafka_host}:{settings.kafka_port}"}