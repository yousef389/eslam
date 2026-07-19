from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import UserRole
from app.domain.repositories import UserRepository
from app.domain.entities import User
from app.infrastructure.models.users import UserModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        username=model.username,
        email=model.email,
        full_name=model.full_name,
        password_hash=model.password_hash,
        role=UserRole(model.role),
        is_active=model.is_active,
        last_login=model.last_login,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(entity: User) -> UserModel:
    return UserModel(
        id=entity.id,
        username=entity.username,
        email=entity.email,
        full_name=entity.full_name,
        password_hash=entity.password_hash,
        role=entity.role.value,
        is_active=entity.is_active,
        last_login=entity.last_login,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, UserModel)

    async def get_by_id(self, id: str) -> Optional[User]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[User], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: User) -> User:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: User) -> User:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.username = entity.username
            model.email = entity.email
            model.full_name = entity.full_name
            model.password_hash = entity.password_hash
            model.role = entity.role.value
            model.is_active = entity.is_active
            model.last_login = entity.last_login
            model.updated_at = entity.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return _model_to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return _model_to_entity(model) if model else None
