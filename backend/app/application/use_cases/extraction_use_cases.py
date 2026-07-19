from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.domain.entities import Extraction
from app.domain.enums import ExtractionStatus


class ListExtractionsUseCase:
    def __init__(self, extractions_repo):
        self.extractions_repo = extractions_repo

    async def execute(
        self,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
    ) -> Tuple[list, int]:
        if status == "pending":
            return await self.extractions_repo.get_pending(page, per_page)
        if status:
            try:
                extraction_status = ExtractionStatus(status)
                return await self.extractions_repo.get_by_status(
                    extraction_status, page, per_page
                )
            except ValueError:
                raise ValidationException(f"Invalid status: {status}")
        return await self.extractions_repo.get_all(page, per_page)


class GetExtractionUseCase:
    def __init__(self, extractions_repo):
        self.extractions_repo = extractions_repo

    async def execute(self, extraction_id: str) -> Extraction:
        extraction = await self.extractions_repo.get_by_id(extraction_id)
        if not extraction:
            raise NotFoundException("Extraction", extraction_id)
        return extraction


class CreateExtractionUseCase:
    def __init__(self, extractions_repo):
        self.extractions_repo = extractions_repo

    async def execute(
        self,
        image_url: Optional[str] = None,
        source: str = "api",
        raw_text: Optional[str] = None,
    ) -> Extraction:
        extraction = Extraction(
            image_url=image_url or "",
            source=source,
            status=ExtractionStatus.PENDING,
            raw_text=raw_text or "",
        )

        return await self.extractions_repo.create(extraction)


class ReviewExtractionUseCase:
    def __init__(self, extractions_repo):
        self.extractions_repo = extractions_repo

    async def execute(
        self,
        extraction_id: str,
        status: str,
        review_notes: Optional[str] = None,
        reviewed_by: Optional[str] = None,
    ) -> Extraction:
        extraction = await self.extractions_repo.get_by_id(extraction_id)
        if not extraction:
            raise NotFoundException("Extraction", extraction_id)

        if extraction.status not in (
            ExtractionStatus.PENDING,
            ExtractionStatus.REVIEWED,
        ):
            raise ConflictException(
                f"Extraction cannot be reviewed in '{extraction.status.value}' status"
            )

        try:
            new_status = ExtractionStatus(status)
        except ValueError:
            raise ValidationException(f"Invalid status: {status}")

        extraction.status = new_status
        extraction.review_notes = review_notes or ""
        extraction.reviewed_by = reviewed_by
        extraction.updated_at = datetime.utcnow()

        return await self.extractions_repo.update(extraction)
