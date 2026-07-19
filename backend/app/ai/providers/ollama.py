import json
import re
import logging
import base64
from decimal import Decimal
from typing import Optional

import httpx

from app.ai.models import (
    ExtractedCustomer,
    ExtractedDebtEntry,
    ExtractedInvoice,
    ExtractedPrice,
    ExtractedProduct,
    ExtractionResult,
)
from app.ai.prompts import EXTRACTION_PROMPT, TEXT_ANALYSIS_PROMPT
from app.ai.providers.base import AIProvider

logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2", temperature: float = 0.1, max_tokens: int = 4096):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def _chat_completion(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    },
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")

    async def extract_from_image(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> ExtractionResult:
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        prompt = EXTRACTION_PROMPT.format(
            format_instructions=self._get_format_instructions()
        )
        try:
            messages = [
                {
                    "role": "user",
                    "content": f"{prompt}\n\nImage (base64): {b64_image}",
                }
            ]
            response_text = await self._chat_completion(messages)
            return self._parse_to_result(response_text)
        except Exception as e:
            logger.error("Ollama image analysis failed: %s", e)
            return ExtractionResult(
                source_type="text",
                confidence=0.0,
                notes=f"Analysis failed: {str(e)}",
            )

    async def extract_from_pdf(self, pdf_bytes: bytes) -> ExtractionResult:
        try:
            import pdfplumber
            import io

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)

            return await self.analyze_text(text)
        except Exception as e:
            logger.error("Ollama PDF analysis failed: %s", e)
            return ExtractionResult(
                source_type="text",
                confidence=0.0,
                notes=f"PDF analysis failed: {str(e)}",
            )

    async def analyze_text(self, text: str) -> ExtractionResult:
        prompt = TEXT_ANALYSIS_PROMPT + "\n\nالنص المحلل:\n" + text
        try:
            messages = [{"role": "user", "content": prompt}]
            response_text = await self._chat_completion(messages)
            return self._parse_to_result(response_text)
        except Exception as e:
            logger.error("Ollama text analysis failed: %s", e)
            return ExtractionResult(
                source_type="text",
                confidence=0.0,
                notes=f"Analysis failed: {str(e)}",
            )

    async def analyze_image(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> ExtractionResult:
        return await self.extract_from_image(image_bytes, mime_type)

    def _parse_response(self, response_text: str) -> dict:
        text = response_text.strip()
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*", "", text)
        text = text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse JSON response: %s", e)
            return {}

    def _parse_to_result(self, response_text: str) -> ExtractionResult:
        data = self._parse_response(response_text)
        if not data:
            return ExtractionResult(
                source_type="text",
                raw_text=response_text,
                confidence=0.0,
                notes="Failed to parse AI response",
            )

        source_type = data.get("source_type", "text")
        invoice = None
        if "invoice" in data and data["invoice"]:
            inv_data = data["invoice"]
            customer = None
            if inv_data.get("customer"):
                customer = ExtractedCustomer(**inv_data["customer"])
            supplier = None
            if inv_data.get("supplier"):
                supplier = ExtractedCustomer(**inv_data["supplier"])
            products = []
            for p in inv_data.get("products", []):
                products.append(
                    ExtractedProduct(
                        name=p.get("name", ""),
                        sku=p.get("sku"),
                        quantity=p.get("quantity", 0),
                        unit_price=Decimal(str(p.get("unit_price", 0))),
                        total=Decimal(str(p.get("total", 0))),
                        unit=p.get("unit", "piece"),
                    )
                )
            invoice = ExtractedInvoice(
                invoice_number=inv_data.get("invoice_number"),
                date=self._parse_date(inv_data.get("date")),
                customer=customer,
                supplier=supplier,
                products=products,
                subtotal=Decimal(str(inv_data.get("subtotal", 0))),
                tax=Decimal(str(inv_data.get("tax", 0))),
                total=Decimal(str(inv_data.get("total", 0))),
                payment_method=inv_data.get("payment_method"),
                confidence=inv_data.get("confidence", 0.0),
            )

        products = []
        for p in data.get("products", []):
            products.append(
                ExtractedProduct(
                    name=p.get("name", ""),
                    sku=p.get("sku"),
                    quantity=p.get("quantity", 0),
                    unit_price=Decimal(str(p.get("unit_price", 0))),
                    total=Decimal(str(p.get("total", 0))),
                    unit=p.get("unit", "piece"),
                )
            )

        prices = []
        for p in data.get("prices", []):
            prices.append(
                ExtractedPrice(
                    product_name=p.get("product_name", ""),
                    price=Decimal(str(p.get("price", 0))),
                    currency=p.get("currency", "EGP"),
                    confidence=p.get("confidence", 0.0),
                )
            )

        debt_entries = []
        for d in data.get("debt_entries", []):
            debt_entries.append(
                ExtractedDebtEntry(
                    customer_name=d.get("customer_name", ""),
                    amount=Decimal(str(d.get("amount", 0))),
                    description=d.get("description", ""),
                    date=self._parse_date(d.get("date")),
                    confidence=d.get("confidence", 0.0),
                )
            )

        return ExtractionResult(
            source_type=source_type,
            raw_text=response_text,
            invoice=invoice,
            products=products,
            prices=prices,
            debt_entries=debt_entries,
            confidence=data.get("confidence", 0.0),
            notes=data.get("notes"),
        )

    def _parse_date(self, date_str: Optional[str]):
        if not date_str:
            return None
        from datetime import datetime
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def _get_format_instructions(self) -> str:
        return """{
    "source_type": "invoice|product_list|price_list|debt_ledger|text",
    "invoice": {
        "invoice_number": "string",
        "date": "YYYY-MM-DD",
        "customer": {"name": "string", "phone": "string", "address": "string"},
        "supplier": {"name": "string"},
        "products": [{"name": "string", "sku": "string", "quantity": 0, "unit_price": 0.0, "total": 0.0, "unit": "piece"}],
        "subtotal": 0.0,
        "tax": 0.0,
        "total": 0.0,
        "payment_method": "string"
    },
    "products": [{"name": "string", "sku": "string", "quantity": 0, "unit_price": 0.0, "total": 0.0, "unit": "piece"}],
    "prices": [{"product_name": "string", "price": 0.0, "currency": "EGP"}],
    "debt_entries": [{"customer_name": "string", "amount": 0.0, "description": "string", "date": "YYYY-MM-DD"}],
    "confidence": 0.9,
    "notes": "optional notes"
}"""
