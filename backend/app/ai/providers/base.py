from abc import ABC, abstractmethod
from typing import Optional

from app.ai.models import ExtractionResult


class AIProvider(ABC):
    @abstractmethod
    async def extract_from_image(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> ExtractionResult:
        pass

    @abstractmethod
    async def extract_from_pdf(self, pdf_bytes: bytes) -> ExtractionResult:
        pass

    @abstractmethod
    async def analyze_text(self, text: str) -> ExtractionResult:
        pass

    @abstractmethod
    async def analyze_image(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> ExtractionResult:
        pass
