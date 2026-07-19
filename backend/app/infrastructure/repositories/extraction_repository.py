import json
from typing import Optional, Tuple, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Extraction
from app.domain.enums import ExtractionStatus
from app.domain.repositories import ExtractionRepository
from app.infrastructure.models.extractions import ExtractionModel

from .base import BaseRepositoryImpl


def _model_to_entity(model: ExtractionModel) -> Extraction:
    extracted_data = {}
    if model.extracted_data:
        try:
            extracted_data = json.loads(model.extracted_data)
        except (json.JSONDecodeError, TypeError):
            extracted_data = {}

    return Extraction(
        id=model.id,
        image_url=model.image_url,
        source=model.source,
        status=ExtractionStatus(model.status),
        raw_text=model.raw_text or "",
        extracted_data=extracted_data,
        review_notes=model.review_notes or "",
        reviewed_by=model.reviewed_by,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(entity: Extraction) -> ExtractionModel:
    return ExtractionModel(
        id=entity.id,
        image_url=entity.image_url,
        source=entity.source,
        status=entity.status.value,
        raw_text=entity.raw_text or None,
        extracted_data=json.dumps(entity.extracted_data) if entity.extracted_data else None,
        review_notes=entity.review_notes or None,
        reviewed_by=entity.reviewed_by,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class ExtractionRepositoryImpl(ExtractionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = BaseRepositoryImpl(session, ExtractionModel)

    async def get_by_id(self, id: str) -> Optional[Extraction]:
        model = await self._repo.get_by_id(id)
        return _model_to_entity(model) if model else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> Tuple[List[Extraction], int]:
        models, total = await self._repo.get_all(page, per_page)
        return [_model_to_entity(m) for m in models], total

    async def create(self, entity: Extraction) -> Extraction:
        model = _entity_to_model(entity)
        created = await self._repo.create(model)
        return _model_to_entity(created)

    async def update(self, entity: Extraction) -> Extraction:
        model = await self._repo.get_by_id(entity.id)
        if not model:
            model = _entity_to_model(entity)
        else:
            model.image_url = entity.image_url
            model.source = entity.source
            model.status = entity.status.value
            model.raw_text = entity.raw_text or None
            model.extracted_data = json.dumps(entity.extracted_data) if entity.extracted_data else None
            model.review_notes = entity.review_notes or None
            model.reviewed_by = entity.reviewed_by
            model.updated_at = entity.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, id: str) -> bool:
        return await self._repo.delete(id)

    async def get_pending(self, page: int = 1, per_page: int = 20) -> Tuple[List[Extraction], int]:
        base_filter = ExtractionModel.status == ExtractionStatus.PENDING.value

        count_stmt = select(func.count()).select_from(ExtractionModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(ExtractionModel)
            .where(base_filter)
            .order_by(ExtractionModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total

    async def get_by_status(
        self, status: ExtractionStatus, page: int = 1, per_page: int = 20
    ) -> Tuple[List[Extraction], int]:
        base_filter = ExtractionModel.status == status.value

        count_stmt = select(func.count()).select_from(ExtractionModel).where(base_filter)
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar() or 0

        stmt = (
            select(ExtractionModel)
            .where(base_filter)
            .order_by(ExtractionModel.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self._session.execute(stmt)
        models = list(result.scalars().all())
        return [_model_to_entity(m) for m in models], total
