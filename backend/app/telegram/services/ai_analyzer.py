import logging
from typing import Optional

from app.ai.service import AIService
from app.ai.models import (
    ExtractedCustomer,
    ExtractedDebtEntry,
    ExtractedInvoice,
    ExtractedPrice,
    ExtractedProduct,
    ExtractionResult,
)

logger = logging.getLogger(__name__)


class TelegramAIAnalyzer:
    def __init__(self):
        self.ai_service = AIService()

    async def analyze_photo(
        self, image_bytes: bytes, mime_type: str
    ) -> str:
        result = await self.ai_service.extract_from_image(image_bytes, mime_type)
        return self.format_result(result)

    async def analyze_document(
        self, file_bytes: bytes, filename: str
    ) -> str:
        if filename.lower().endswith(".pdf"):
            result = await self.ai_service.extract_from_pdf(file_bytes)
        else:
            result = await self.ai_service.analyze_text(
                file_bytes.decode("utf-8", errors="ignore")
            )
        return self.format_result(result)

    def format_result(self, result: ExtractionResult) -> str:
        if result.confidence == 0.0 and result.notes:
            return f"❌ حدث خطأ أثناء التحليل:\n{result.notes}"

        lines = []
        lines.append("📊 *نتيجة التحليل*")
        lines.append(f"نوع المستند: {self._source_type_arabic(result.source_type)}")
        lines.append(f"الثقة: {result.confidence * 100:.0f}%")
        lines.append("")

        if result.invoice:
            lines.append(self._format_invoice(result.invoice))

        if result.products:
            lines.append("📦 *المنتجات:*")
            for p in result.products:
                lines.append(self._format_product(p))
            lines.append("")

        if result.prices:
            lines.append("💰 *الأسعار:*")
            for p in result.prices:
                lines.append(self._format_price(p))
            lines.append("")

        if result.debt_entries:
            lines.append("📋 *الديون:*")
            for d in result.debt_entries:
                lines.append(self._format_debt(d))
            lines.append("")

        if result.notes:
            lines.append(f"📝 *ملاحظات:* {result.notes}")

        return "\n".join(lines)

    def _format_invoice(self, invoice: ExtractedInvoice) -> str:
        lines = ["🧾 *فاتورة*"]
        if invoice.invoice_number:
            lines.append(f"رقم الفاتورة: {invoice.invoice_number}")
        if invoice.date:
            lines.append(f"التاريخ: {invoice.date.strftime('%Y-%m-%d')}")
        if invoice.customer and invoice.customer.name:
            lines.append(f"العميل: {invoice.customer.name}")
        if invoice.supplier and invoice.supplier.name:
            lines.append(f"المورد: {invoice.supplier.name}")
        lines.append("")
        if invoice.products:
            lines.append("📦 *المنتجات:*")
            for p in invoice.products:
                lines.append(self._format_product(p))
            lines.append("")
        if invoice.subtotal > 0:
            lines.append(f"المجموع الفرعي: {invoice.subtotal} EGP")
        if invoice.tax > 0:
            lines.append(f"الضريبة: {invoice.tax} EGP")
        if invoice.total > 0:
            lines.append(f"**الإجمالي: {invoice.total} EGP**")
        if invoice.payment_method:
            lines.append(f"طريقة الدفع: {invoice.payment_method}")
        lines.append("")
        return "\n".join(lines)

    def _format_product(self, product: ExtractedProduct) -> str:
        parts = [f"  • {product.name}"]
        if product.sku:
            parts.append(f"({product.sku})")
        if product.quantity > 0:
            parts.append(f"الكمية: {product.quantity}")
        if product.unit_price > 0:
            parts.append(f"السعر: {product.unit_price} EGP")
        if product.total > 0:
            parts.append(f"الإجمالي: {product.total} EGP")
        return " | ".join(parts)

    def _format_price(self, price: ExtractedPrice) -> str:
        return f"  • {price.product_name}: {price.price} {price.currency}"

    def _format_debt(self, debt: ExtractedDebtEntry) -> str:
        parts = [f"  • {debt.customer_name}: {debt.amount} EGP"]
        if debt.description:
            parts.append(f"({debt.description})")
        if debt.date:
            parts.append(f"[{debt.date.strftime('%Y-%m-%d')}]")
        return " ".join(parts)

    def _source_type_arabic(self, source_type: str) -> str:
        mapping = {
            "invoice": "فاتورة",
            "product_list": "قائمة منتجات",
            "price_list": "قائمة أسعار",
            "debt_ledger": "دفتر ذمة",
            "text": "نص",
        }
        return mapping.get(source_type, source_type)
