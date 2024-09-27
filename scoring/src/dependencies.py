from functools import lru_cache
from models import database
from collections.abc import Callable, Coroutine
from typing import Any

from common.repo.session import get_repository, get_repository_callable
from models.models import ApplicationScored
from common.repo.repository import DatabaseRepository
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import ScoringSettings
from common.repo.create_db_url import create_db_url_from_settings


@lru_cache
def get_settings():
    return ScoringSettings()


def get_repo() -> Coroutine[Any, Any, DatabaseRepository]:
    return get_repository(engine, ApplicationScored)

engine = database.get_engine(create_db_url_from_settings(get_settings()))
get_repo_dep: Callable[[AsyncSession], DatabaseRepository] = get_repository_callable(engine, ApplicationScored)
