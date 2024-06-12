import asyncio
from collections.abc import Callable, Coroutine
from functools import lru_cache
import logging
from typing import Any
from common.kafka.create_config import create_kafka_config_from_settings
from common.kafka.consumer_manager import KafkaConsumer
from common.kafka.producer_manager import KafkaProducer
from models import database
from clients.scoring_client import ScoringClient

from common.repo.session import get_repository, get_repository_callable
from models.models import Application
from common.repo.repository import DatabaseRepository
from config.config import OriginationSettings
from common.repo.create_db_url import create_db_url_from_settings
from common.settings.urls import SCORING_SERVICE_URL
from tasks.scheduler import TasksScheduler
from sqlalchemy.ext.asyncio import AsyncSession

@lru_cache
def get_settings():
    return OriginationSettings()

def get_repo() -> Coroutine[Any, Any, DatabaseRepository]:
    return get_repository(engine, Application)

def get_scoring_client():
    client = ScoringClient(base_url=SCORING_SERVICE_URL)
    return client


def get_task_scheduler():
    return TasksScheduler(scoring_client=get_scoring_client(), get_repo=get_repo, settings=get_settings(), kafka_producer_scoring_request=kafka_producer_scoring_request)


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

def get_kafka_producer_scoring_request():
    return kafka_producer_scoring_request
    
loop = asyncio.get_event_loop()

kafka_consumer_new_agreements = KafkaConsumer(get_kafka_consumer_config())
kafka_consumer_scoring_response = KafkaConsumer(get_kafka_consumer_config())

kafka_producer_scoring_request = KafkaProducer(get_kafka_producer_config())

engine = database.get_engine(create_db_url_from_settings(get_settings()))

get_repo_dep: Callable[[AsyncSession], DatabaseRepository] = get_repository_callable(engine, Application)
    
MIN_TIME_BETWEEN_APPLICATIONS_IN_SEC = get_settings().min_time_between_applications_in_sec

logging.basicConfig(level=logging.INFO)