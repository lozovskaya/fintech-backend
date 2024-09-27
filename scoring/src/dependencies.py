import asyncio
from functools import lru_cache
import logging
from common.kafka.create_config import create_kafka_config_from_settings
from common.kafka.consumer_manager import KafkaConsumer
from common.kafka.producer_manager import KafkaProducer
from models import database
from collections.abc import Callable, Coroutine
from typing import Any

from common.repo.session import get_repository, get_repository_callable
from models.models import ApplicationScored
from common.repo.repository import DatabaseRepository
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import ScoringSettings
from common.repo.create_db_url import create_db_url_from_settings
from clients.product_engine_client import ProductEngineClient
from common.settings.urls import PRODUCT_ENGINE_URL


@lru_cache
def get_settings():
    return ScoringSettings()


def get_repo() -> Coroutine[Any, Any, DatabaseRepository]:
    return get_repository(engine, ApplicationScored)

def get_product_engine_client():
    client = ProductEngineClient(base_url=PRODUCT_ENGINE_URL)
    return client


@lru_cache
def get_kafka_consumer_config():
    config = create_kafka_config_from_settings(get_settings())
    config["loop"] = loop
    config["group_id"] = get_settings().group_id
    return config

@lru_cache
def get_kafka_producer_config():
    config = create_kafka_config_from_settings(get_settings())
    config["loop"] = loop
    return config
    
loop = asyncio.get_event_loop()

kafka_consumer = KafkaConsumer(get_kafka_consumer_config())
kafka_producer = KafkaProducer(get_kafka_producer_config())

product_engine_client = get_product_engine_client()

engine = database.get_engine(create_db_url_from_settings(get_settings()))
get_repo_dep: Callable[[AsyncSession], DatabaseRepository] = get_repository_callable(engine, ApplicationScored)
logging.basicConfig(level=logging.INFO)