from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import URL


Base = declarative_base()

def get_engine(url : URL):
    return create_async_engine(url)