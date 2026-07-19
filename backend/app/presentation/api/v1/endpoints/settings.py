from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.settings_use_cases import (
    GetSettingUseCase,
    ListSettingsUseCase,
    UpdateSettingUseCase,
    UpdateSettingsBulkUseCase,
)
from app.core.dependencies import get_current_user, require_role
from app.domain.enums import UserRole
from app.infrastructure.database import get_db
from app.infrastructure.repositories.system_setting_repository import SystemSettingRepositoryImpl

router = APIRouter()


class SettingUpdate(BaseModel):
    value: str


class SettingsBulkUpdate(BaseModel):
    settings: dict[str, str]


@router.get("/")
async def list_settings(
    group: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = SystemSettingRepositoryImpl(db)
    use_case = ListSettingsUseCase(repo)
    settings = await use_case.execute(group)
    return {"success": True, "data": settings}


@router.get("/{key}")
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = SystemSettingRepositoryImpl(db)
    use_case = GetSettingUseCase(repo)
    setting = await use_case.execute(key)
    if not setting:
        return {"success": False, "detail": "Setting not found"}
    return {"success": True, "data": setting}


@router.put("/{key}")
async def update_setting(
    key: str,
    request: SettingUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.ADMIN)),
):
    repo = SystemSettingRepositoryImpl(db)
    use_case = UpdateSettingUseCase(repo)
    setting = await use_case.execute(key, request.value)
    return {"success": True, "data": setting, "message": "Setting updated"}


@router.put("/")
async def update_settings_bulk(
    request: SettingsBulkUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.ADMIN)),
):
    repo = SystemSettingRepositoryImpl(db)
    use_case = UpdateSettingsBulkUseCase(repo)
    settings = await use_case.execute(request.settings)
    return {"success": True, "data": settings, "message": "Settings updated"}
