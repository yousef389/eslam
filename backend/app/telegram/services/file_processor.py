import os
import mimetypes
from typing import Tuple

from app.ai.service import AIService
from app.ai.models import ExtractionResult


class FileProcessor:
    _ai_service: AIService = None

    @classmethod
    def _get_ai_service(cls) -> AIService:
        if cls._ai_service is None:
            cls._ai_service = AIService()
        return cls._ai_service

    @staticmethod
    async def download_file(bot, file_id: str) -> Tuple[bytes, str]:
        file = await bot.get_file(file_id)
        file_bytes = await file.download_as_bytearray()
        filename = file.file_path.split("/")[-1] if file.file_path else "unknown_file"
        return bytes(file_bytes), filename

    @staticmethod
    def get_mime_type(filename: str) -> str:
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"

    @classmethod
    async def process_image(
        cls, file_bytes: bytes, mime_type: str
    ) -> ExtractionResult:
        ai = cls._get_ai_service()
        return await ai.extract_from_image(file_bytes, mime_type)

    @classmethod
    async def process_pdf(cls, file_bytes: bytes) -> ExtractionResult:
        ai = cls._get_ai_service()
        return await ai.extract_from_pdf(file_bytes)
