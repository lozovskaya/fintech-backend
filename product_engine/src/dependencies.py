import asyncio
from functools import lru_cache
import logging
from common.kafka.create_config import create_kafka_config_from_settings
from common.kafka.producer_manager import KafkaProducer
from common.kafka.consumer_manager import KafkaConsumer
from models import database
from clients.origination_client import OriginationClient
from config.config import ProductEngineSettings
from common.settings.urls import ORIGINATION_URL
from helpers.payment_plan_creator import PaymentPlanHelper
from tasks.scheduler import TasksScheduler
from collections.abc import Callable, Coroutine
from typing import Any
from common.repo.repository import DatabaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from common.repo.session import get_repository, get_repository_callable
from common.repo.create_db_url import create_db_url_from_settings

@lru_cache
def get_settings():
    return ProductEngineSettings()

def get_repo_dep(model) -> Callable[[AsyncSession], DatabaseRepository]:
    return get_repository_callable(engine, model)


def get_repo(model) -> Coroutine[Any, Any, DatabaseRepository]:
    return get_repository(engine, model)


def get_origination_client():
    client = OriginationClient(base_url=ORIGINATION_URL)
    return client


def get_task_scheduler():
    return TasksScheduler(origination_client=get_origination_client(), get_repo=get_repo)

@lru_cache
def get_kafka_config():
    config = create_kafka_config_from_settings(get_settings())
    config["loop"] = loop
    return config

@lru_cache
def get_kafka_consumer_config():
    config = create_kafka_config_from_settings(get_settings())
    config["loop"] = loop
    config["group_id"] = get_settings().group_id
    return config


def get_kafka_producer():
    return kafka_producer
    
loop = asyncio.get_event_loop()
engine = database.get_engine(create_db_url_from_settings(get_settings()))
kafka_producer = KafkaProducer(get_kafka_config())
kafka_consumer = KafkaConsumer(get_kafka_consumer_config())
payment_plan_helper = PaymentPlanHelper()
logging.basicConfig(level=logging.INFO)