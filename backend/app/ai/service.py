import logging
from typing import Optional

from app.ai.models import ExtractionResult
from app.ai.providers.factory import AIProviderFactory

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self._provider = None

    async def _get_provider(self):
        if self._provider is None:
            self._provider = await AIProviderFactory.get_provider()
        return self._provider

    async def extract_from_image(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> ExtractionResult:
        provider = await self._get_provider()
        return await provider.extract_from_image(image_bytes, mime_type)

    async def extract_from_pdf(self, pdf_bytes: bytes) -> ExtractionResult:
        provider = await self._get_provider()
        return await provider.extract_from_pdf(pdf_bytes)

    async def analyze_text(self, text: str) -> ExtractionResult:
        provider = await self._get_provider()
        return await provider.analyze_text(text)

    async def analyze_image(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> ExtractionResult:
        provider = await self._get_provider()
        return await provider.analyze_image(image_bytes, mime_type)
