EXTRACTION_PROMPT = """أنت نظام ذكاء اصطناعي متخصص في تحليل فواتير ومستندات محلات الأدوات الصحية.

حلل الصورة أو النص المقدم واستخرج المعلومات التالية بالشكل المحدد:

{format_instructions}

important rules:
- استخدم الجنيه المصري (EGP) كعملة افتراضية
- إذا لم تجد معلومة، أعد null
- أعد النتيجة كـ JSON فقط، بدون أي نص إضافي
- تأكد من أن الأرقام صحيحية
"""

INVOICE_PROMPT = """حلل فاتورة محل الأدوات الصحية واستخرج:
- رقم الفاتورة والتاريخ
- بيانات العميل أو المورد
- قائمة المنتجات (الاسم، الكمية، السعر)
- المجموع والضريبة والإجمالي

أعد النتيجة بالشكل التالي كـ JSON فقط:
{
    "source_type": "invoice",
    "invoice": {
        "invoice_number": "رقم الفاتورة",
        "date": "YYYY-MM-DD",
        "customer": {"name": "اسم العميل", "phone": "الهاتف", "address": "العنوان"},
        "supplier": {"name": "اسم المورد"},
        "products": [
            {"name": "اسم المنتج", "sku": "الكود", "quantity": 1, "unit_price": 100.0, "total": 100.0, "unit": "piece"}
        ],
        "subtotal": 100.0,
        "tax": 14.0,
        "total": 114.0,
        "payment_method": "cash"
    },
    "confidence": 0.9
}
"""

PRODUCT_LIST_PROMPT = """حلل قائمة منتجات واستخرج كل منتج مع:
- الاسم والكود
- الكمية والسعر
- الوحدة

أعد النتيجة بالشكل التالي كـ JSON فقط:
{
    "source_type": "product_list",
    "products": [
        {"name": "اسم المنتج", "sku": "الكود", "quantity": 10, "unit_price": 50.0, "total": 500.0, "unit": "piece"}
    ],
    "confidence": 0.9
}
"""

PRICE_LIST_PROMPT = """حلل قائمة أسعار واستخرج:
- اسم المنتج
- السعر
- العملة

أعد النتيجة بالشكل التالي كـ JSON فقط:
{
    "source_type": "price_list",
    "prices": [
        {"product_name": "اسم المنتج", "price": 100.0, "currency": "EGP"}
    ],
    "confidence": 0.9
}
"""

DEBT_LEDGER_PROMPT = """حلل دفتر ذمة واستخرج:
- اسم العميل
- المبلغ
- الوصف
- التاريخ

أعد النتيجة بالشكل التالي كـ JSON فقط:
{
    "source_type": "debt_ledger",
    "debt_entries": [
        {"customer_name": "اسم العميل", "amount": 5000.0, "description": "وصف", "date": "YYYY-MM-DD"}
    ],
    "confidence": 0.9
}
"""

TEXT_ANALYSIS_PROMPT = """حلل النص التالي واستخرج أي معلومات مالية أو تجارية ذات صلة:
- منتجات وأسعار
- عملاء وموردين
- ديون ومدفوعات
- فواتير

أعد النتيجة بالشكل التالي كـ JSON فقط:
{
    "source_type": "text",
    "products": [],
    "prices": [],
    "debt_entries": [],
    "confidence": 0.8,
    "notes": "ملاحظات إضافية"
}
"""
