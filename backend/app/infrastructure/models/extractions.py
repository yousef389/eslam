from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base
from app.domain.enums import ExtractionStatus


class ExtractionModel(Base):
    __tablename__ = "extractions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    image_url: Mapped[str] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(String(50), default="api")
    status: Mapped[str] = mapped_column(String(20), default=ExtractionStatus.PENDING.value)
    raw_text: Mapped[str | None] = mapped_column(nullable=True)
    extracted_data: Mapped[str | None] = mapped_column(nullable=True)
    review_notes: Mapped[str | None] = mapped_column(nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
