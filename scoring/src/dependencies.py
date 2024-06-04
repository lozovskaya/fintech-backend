from models import database
from collections.abc import Callable, Coroutine
from typing import Any

from common.repo.session import get_repository, get_repository_callable
from models.models import ApplicationScored
from common.repo.repository import DatabaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


get_repo_dep: Callable[[AsyncSession], DatabaseRepository] = get_repository_callable(database.engine, ApplicationScored)

def get_repo() -> Coroutine[Any, Any, DatabaseRepository]:
    return get_repository(database.engine, ApplicationScored)
