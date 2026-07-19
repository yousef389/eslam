from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto import ExtractionCreate, ExtractionReview
from app.application.use_cases.extraction_use_cases import (
    CreateExtractionUseCase,
    GetExtractionUseCase,
    ListExtractionsUseCase,
    ReviewExtractionUseCase,
)
from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenException, NotFoundException
from app.infrastructure.database import get_db
from app.infrastructure.repositories.extraction_repository import ExtractionRepositoryImpl

router = APIRouter()


def _extraction_to_dict(extraction):
    return {
        "id": extraction.id,
        "image_url": extraction.image_url,
        "source": extraction.source,
        "status": extraction.status.value if hasattr(extraction.status, "value") else extraction.status,
        "raw_text": extraction.raw_text,
        "extracted_data": extraction.extracted_data,
        "review_notes": extraction.review_notes,
        "reviewed_by": extraction.reviewed_by,
        "created_at": extraction.created_at.isoformat() if extraction.created_at else None,
        "updated_at": extraction.updated_at.isoformat() if extraction.updated_at else None,
    }


@router.get("/")
async def list_extractions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ExtractionRepositoryImpl(db)
    use_case = ListExtractionsUseCase(repo)
    extractions, total = await use_case.execute(page, per_page, status)
    return {
        "success": True,
        "data": [_extraction_to_dict(e) for e in extractions],
        "meta": {"total": total, "page": page, "per_page": per_page},
    }


@router.get("/{extraction_id}")
async def get_extraction(
    extraction_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ExtractionRepositoryImpl(db)
    use_case = GetExtractionUseCase(repo)
    extraction = await use_case.execute(extraction_id)
    return {"success": True, "data": _extraction_to_dict(extraction)}


@router.post("/")
async def create_extraction(
    request: ExtractionCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = ExtractionRepositoryImpl(db)
    use_case = CreateExtractionUseCase(repo)
    extraction = await use_case.execute(
        image_url=request.image_url,
        source=request.source,
        raw_text=request.raw_text,
    )
    return {"success": True, "data": _extraction_to_dict(extraction), "message": "Extraction created"}


@router.put("/{extraction_id}/review")
async def review_extraction(
    extraction_id: str,
    request: ExtractionReview,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    role = user.get("role", "")
    if role not in ("admin", "manager"):
        raise ForbiddenException("Only admin or manager can review extractions")

    repo = ExtractionRepositoryImpl(db)
    use_case = ReviewExtractionUseCase(repo)
    extraction = await use_case.execute(
        extraction_id=extraction_id,
        status=request.status,
        review_notes=request.review_notes,
        reviewed_by=user["id"],
    )
    return {"success": True, "data": _extraction_to_dict(extraction), "message": "Extraction reviewed"}
