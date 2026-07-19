from typing import Any, Generic, List, Optional, Tuple, Type

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import BaseRepository, T


class BaseRepositoryImpl(BaseRepository[T], Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]) -> None:
        self._session = session
        self._model = model

    async def get_by_id(self, id: str) -> Optional[T]:
        stmt = select(self._model).where(self._model.id == id)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[T], int]:
        count_stmt = select(func.count()).select_from(self._model)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = select(self._model).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def create(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self._session.merge(entity)
        await self._session.flush()
        return entity

    async def delete(self, id: str) -> bool:
        entity = await self.get_by_id(id)
        if entity:
            await self._session.delete(entity)
            await self._session.flush()
            return True
        return False
