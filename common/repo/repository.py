from typing import Any, Generic, TypeVar

from sqlalchemy import BinaryExpression, ColumnExpressionArgument, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import DeclarativeBase


Model = TypeVar("Model", bound=DeclarativeBase)

class DatabaseRepository(Generic[Model]):
    def __init__(self, model: type[Model], session: AsyncSession) -> None:
        self.model = model
        self.session = session


    async def create(self, data: dict) -> Model:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    

    async def update(self, *expressions: BinaryExpression, data: dict[str, Any]) -> None:
        query = update(self.model).where(*expressions).values(**data)
        await self.session.execute(query)
        await self.session.commit()


    async def delete(self, *expressions: BinaryExpression) -> None:
        query = delete(self.model).where(*expressions)
        await self.session.execute(query)
        await self.session.commit()

        
    async def filter(self, *expressions: BinaryExpression, order_by = None) -> list[Model]:
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        if order_by is not None:
            query = query.order_by(order_by)
        return list(await self.session.scalars(query))
