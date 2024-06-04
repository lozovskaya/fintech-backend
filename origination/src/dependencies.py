from collections.abc import Callable, Coroutine
from typing import Any
from models import database
from clients.scoring_client import ScoringClient

from common.repo.session import get_repository, get_repository_callable, get_db_session_callable
from models.models import Application
from common.repo.repository import DatabaseRepository
from tasks.scheduler import TasksScheduler
from sqlalchemy.ext.asyncio import AsyncSession

get_repo_dep: Callable[[AsyncSession], DatabaseRepository] = get_repository_callable(database.engine, Application)

def get_repo() -> Coroutine[Any, Any, DatabaseRepository]:
    return get_repository(database.engine, Application)

def get_scoring_client():
    client = ScoringClient(base_url=SCORING_SERVICE_URL)
    return client


def get_task_scheduler():
    return TasksScheduler(scoring_client=get_scoring_client(), get_repo=get_repo)

    
PRODUCT_ENGINE_URL = "http://host.docker.internal:80"
SCORING_SERVICE_URL = "http://host.docker.internal:8008"
MIN_TIME_BETWEEN_APPLICATIONS_IN_SEC = 5 * 50 # 5 minutes