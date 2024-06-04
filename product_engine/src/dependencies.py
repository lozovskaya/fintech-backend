from models import database
from clients.origination_client import OriginationClient
from tasks.scheduler import TasksScheduler
from collections.abc import Callable, Coroutine
from typing import Any
from common.repo.repository import DatabaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from common.repo.session import get_repository, get_repository_callable


def get_repo_dep(model) -> Callable[[AsyncSession], DatabaseRepository]:
    return get_repository_callable(database.engine, model)


def get_repo(model) -> Coroutine[Any, Any, DatabaseRepository]:
    return get_repository(database.engine, model)


def get_origination_client():
    client = OriginationClient(base_url=ORIGINATION_URL)
    return client


def get_task_scheduler():
    return TasksScheduler(origination_client=get_origination_client(), get_repo=get_repo)

ORIGINATION_URL = "http://host.docker.internal:90"