from collections.abc import AsyncGenerator, Callable

from fastapi import Depends
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import DeclarativeBase

from common.repo.repository import DatabaseRepository


async def get_db_session_callable(engine: AsyncEngine) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
    async def func() -> AsyncGenerator[AsyncSession, None]:
        factory = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except exc.SQLAlchemyError:
                await session.rollback()
                raise
    return func


def get_repository_callable(engine : AsyncEngine, model: type[DeclarativeBase]) -> Callable[[AsyncSession], DatabaseRepository]:
    async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
        db_session_func = await get_db_session_callable(engine)
        async for session in db_session_func():
            yield session
    
    def func(session: AsyncSession = Depends(get_db_session)):
        return DatabaseRepository(model, session)
    return func


async def get_repository(engine: AsyncEngine, model: type[DeclarativeBase]) -> AsyncGenerator[DatabaseRepository]:
    get_db_session = await get_db_session_callable(engine)
    async for session in get_db_session():
        yield DatabaseRepository(model, session)