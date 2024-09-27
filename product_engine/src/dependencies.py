from functools import lru_cache
from models import database
from clients.origination_client import OriginationClient
from config.config import ProductEngineSettings
from common.settings.urls import ORIGINATION_URL
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

engine = database.get_engine(create_db_url_from_settings(get_settings()))
