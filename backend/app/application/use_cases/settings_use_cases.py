from __future__ import annotations

from typing import List, Optional

from app.domain.enums import SettingsGroup
from app.domain.repositories import SystemSettingRepository


class ListSettingsUseCase:
    def __init__(self, repo: SystemSettingRepository):
        self.repo = repo

    async def execute(self, group: Optional[str] = None) -> List[dict]:
        if group:
            settings_group = SettingsGroup(group)
            settings = await self.repo.get_by_group(settings_group)
        else:
            settings = await self.repo.get_all_settings()

        return [
            {
                "id": s.id,
                "key": s.key,
                "value": "" if s.is_secret and s.value else s.value,
                "group": s.group.value,
                "description": s.description,
                "is_secret": s.is_secret,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in settings
        ]


class GetSettingUseCase:
    def __init__(self, repo: SystemSettingRepository):
        self.repo = repo

    async def execute(self, key: str) -> Optional[dict]:
        setting = await self.repo.get_by_key(key)
        if not setting:
            return None
        return {
            "id": setting.id,
            "key": setting.key,
            "value": "" if setting.is_secret and setting.value else setting.value,
            "group": setting.group.value,
            "description": setting.description,
            "is_secret": setting.is_secret,
        }


class UpdateSettingUseCase:
    def __init__(self, repo: SystemSettingRepository):
        self.repo = repo

    async def execute(self, key: str, value: str) -> dict:
        setting = await self.repo.get_by_key(key)
        if not setting:
            raise ValueError(f"Setting '{key}' not found")

        setting.value = value
        updated = await self.repo.update(setting)
        return {
            "id": updated.id,
            "key": updated.key,
            "value": "" if updated.is_secret and updated.value else updated.value,
            "group": updated.group.value,
            "description": updated.description,
            "is_secret": updated.is_secret,
        }


class UpdateSettingsBulkUseCase:
    def __init__(self, repo: SystemSettingRepository):
        self.repo = repo

    async def execute(self, settings: dict[str, str]) -> List[dict]:
        results = []
        for key, value in settings.items():
            setting = await self.repo.get_by_key(key)
            if setting:
                setting.value = value
                updated = await self.repo.update(setting)
                results.append({
                    "id": updated.id,
                    "key": updated.key,
                    "value": "" if updated.is_secret and updated.value else updated.value,
                    "group": updated.group.value,
                })
        return results
