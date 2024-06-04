from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/scoring"

Base = declarative_base()
engine = create_async_engine(DATABASE_URL)