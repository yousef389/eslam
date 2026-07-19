import json
import re
import logging
from decimal import Decimal
from typing import Optional

import google.generativeai as genai

from app.ai.config import ai_settings
from app.ai.models import (
    ExtractedCustomer,
    ExtractedDebtEntry,
    ExtractedInvoice,
    ExtractedPrice,
    ExtractedProduct,
    ExtractionResult,
)
from app.ai.prompts import (
    EXTRACTION_PROMPT,
    TEXT_ANALYSIS_PROMPT,
)

logger = logging.getLogger(__name__)

genai.configure(api_key=ai_settings.GOOGLE_API_KEY)


class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel(ai_settings.AI_MODEL)

    async def extract_from_image(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> ExtractionResult:
        image_data = {"mime_type": mime_type, "data": image_bytes}
        prompt = EXTRACTION_PROMPT.format(
            format_instructions=self._get_format_instructions()
        )
        try:
            response = self.model.generate_content(
                [prompt, image_data],
                generation_config=genai.types.GenerationConfig(
                    temperature=ai_settings.AI_TEMPERATURE,
                    max_output_tokens=ai_settings.AI_MAX_TOKENS,
                ),
            )
            return self._parse_to_result(response.text)
        except Exception as e:
            logger.error("AI image analysis failed: %s", e)
            return ExtractionResult(
                source_type="text",
                confidence=0.0,
                notes=f"Analysis failed: {str(e)}",
            )

    async def extract_from_pdf(self, pdf_bytes: bytes) -> ExtractionResult:
        pdf_data = {"mime_type": "application/pdf", "data": pdf_bytes}
        prompt = EXTRACTION_PROMPT.format(
            format_instructions=self._get_format_instructions()
        )
        try:
            response = self.model.generate_content(
                [prompt, pdf_data],
                generation_config=genai.types.GenerationConfig(
                    temperature=ai_settings.AI_TEMPERATURE,
                    max_output_tokens=ai_settings.AI_MAX_TOKENS,
                ),
            )
            return self._parse_to_result(response.text)
        except Exception as e:
            logger.error("AI PDF analysis failed: %s", e)
            return ExtractionResult(
                source_type="text",
                confidence=0.0,
                notes=f"Analysis failed: {str(e)}",
            )

    async def analyze_text(self, text: str) -> ExtractionResult:
        prompt = TEXT_ANALYSIS_PROMPT + "\n\nالنص المحلل:\n" + text
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=ai_settings.AI_TEMPERATURE,
                    max_output_tokens=ai_settings.AI_MAX_TOKENS,
                ),
            )
            return self._parse_to_result(response.text)
        except Exception as e:
            logger.error("AI text analysis failed: %s", e)
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
            logger.debug("Raw response text: %s", response_text)
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
        source_type = self._determine_source_type(data)
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

    def _determine_source_type(self, data: dict) -> str:
        if "source_type" in data:
            return data["source_type"]
        if "invoice" in data and data["invoice"]:
            return "invoice"
        if "debt_entries" in data and data["debt_entries"]:
            return "debt_ledger"
        if "prices" in data and data["prices"] and not data.get("products"):
            return "price_list"
        if "products" in data and data["products"]:
            return "product_list"
        return "text"

    def _parse_date(self, date_str: Optional[str]) -> Optional["datetime"]:
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

