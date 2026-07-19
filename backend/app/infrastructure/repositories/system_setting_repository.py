from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import SettingsGroup
from app.domain.repositories import SystemSettingRepository
from app.domain.entities import SystemSetting
from app.infrastructure.models.system_settings import SystemSettingModel


class SystemSettingRepositoryImpl(SystemSettingRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: SystemSettingModel) -> SystemSetting:
        return SystemSetting(
            id=model.id,
            key=model.key,
            value=model.value,
            group=SettingsGroup(model.group),
            description=model.description,
            is_secret=model.is_secret,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: SystemSetting) -> SystemSettingModel:
        return SystemSettingModel(
            id=entity.id,
            key=entity.key,
            value=entity.value,
            group=entity.group.value,
            description=entity.description,
            is_secret=entity.is_secret,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: str) -> Optional[SystemSetting]:
        stmt = select(SystemSettingModel).where(SystemSettingModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[SystemSetting], int]:
        count_stmt = select(func.count()).select_from(SystemSettingModel)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = select(SystemSettingModel).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(stmt)
        items = [self._to_entity(m) for m in result.scalars().all()]
        return items, total

    async def create(self, entity: SystemSetting) -> SystemSetting:
        model = self._to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, entity: SystemSetting) -> SystemSetting:
        model = self._to_model(entity)
        await self._session.merge(model)
        await self._session.flush()
        return entity

    async def delete(self, id: str) -> bool:
        stmt = select(SystemSettingModel).where(SystemSettingModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def get_by_key(self, key: str) -> Optional[SystemSetting]:
        stmt = select(SystemSettingModel).where(SystemSettingModel.key == key)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def get_by_group(self, group: SettingsGroup) -> List[SystemSetting]:
        stmt = select(SystemSettingModel).where(SystemSettingModel.group == group.value)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_all_settings(self) -> List[SystemSetting]:
        stmt = select(SystemSettingModel).order_by(SystemSettingModel.group, SystemSettingModel.key)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def set_setting(
        self,
        key: str,
        value: str,
        group: SettingsGroup,
        description: str = "",
        is_secret: bool = False,
    ) -> SystemSetting:
        existing = await self.get_by_key(key)
        if existing:
            existing.value = value
            existing.updated_at = datetime.utcnow()
            await self.update(existing)
            return existing

        entity = SystemSetting(
            key=key,
            value=value,
            group=group,
            description=description,
            is_secret=is_secret,
        )
        return await self.create(entity)


from datetime import datetime
