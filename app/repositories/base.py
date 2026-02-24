import math
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> ModelType | None:
        return await self.session.get(self.model, id)

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        order_by: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[ModelType], int]:
        """Return (items, total_count)."""
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(self.model, key):
                    col = getattr(self.model, key)
                    query = query.where(col == value)
                    count_query = count_query.where(col == value)

        total = (await self.session.execute(count_query)).scalar() or 0

        if order_by:
            desc = order_by.startswith("-")
            col_name = order_by.lstrip("-")
            if hasattr(self.model, col_name):
                col = getattr(self.model, col_name)
                query = query.order_by(col.desc() if desc else col.asc())

        query = query.offset(offset).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        return items, total

    async def create(self, **kwargs: Any) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelType, **kwargs: Any) -> ModelType:
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.session.delete(instance)
        await self.session.flush()

    @staticmethod
    def calc_pages(total: int, size: int) -> int:
        return max(1, math.ceil(total / size))
