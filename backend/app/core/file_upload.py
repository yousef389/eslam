from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path

import magic

from app.core.exceptions import ValidationException

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_FILE_SIZE = 10 * 1024 * 1024

EXTENSION_TO_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".pdf": "application/pdf",
}


class SecureFileUpload:
    @staticmethod
    def validate_file(
        file_bytes: bytes, filename: str, allowed_types: set[str]
    ) -> tuple[bool, str]:
        if len(file_bytes) > MAX_FILE_SIZE:
            return False, f"File size exceeds maximum of {MAX_FILE_SIZE // (1024 * 1024)}MB"

        if len(file_bytes) == 0:
            return False, "Empty file"

        mime = magic.from_buffer(file_bytes, mime=True)

        if mime not in allowed_types:
            return False, f"File type '{mime}' is not allowed"

        ext = Path(filename).suffix.lower()
        expected_mime = EXTENSION_TO_MIME.get(ext)

        if expected_mime and expected_mime != mime:
            return False, f"File extension '{ext}' does not match detected type '{mime}'"

        return True, mime

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        filename = os.path.basename(filename)
        filename = unicodedata.normalize("NFKD", filename)
        filename = re.sub(r"[^\w\s\-.]", "", filename)
        filename = re.sub(r"[-\s]+", "-", filename).strip("-_")
        filename = filename.lstrip(".")

        if not filename:
            filename = "unnamed_file"

        return filename[:255]

    @staticmethod
    async def save_file(file_bytes: bytes, filename: str, upload_dir: str) -> str:
        is_valid, result = SecureFileUpload.validate_file(
            file_bytes, filename, ALLOWED_DOCUMENT_TYPES | ALLOWED_IMAGE_TYPES
        )
        if not is_valid:
            raise ValidationException(result)

        safe_name = SecureFileUpload.sanitize_filename(filename)
        upload_path = Path(upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)

        file_path = upload_path / safe_name

        counter = 1
        while file_path.exists():
            stem = file_path.stem
            suffix = file_path.suffix
            file_path = upload_path / f"{stem}_{counter}{suffix}"
            counter += 1

        file_path.write_bytes(file_bytes)
        return str(file_path)
