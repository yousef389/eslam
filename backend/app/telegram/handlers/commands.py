import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.telegram.services.api_client import ERPAPIClient
from app.telegram.config import telegram_settings

logger = logging.getLogger(__name__)

api_client = ERPAPIClient()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً! أنا بوت نظام ERP للأدوات الصحية\n\n"
        "الأوامر المتاحة:\n"
        "/products - عرض المنتجات\n"
        "/customers - عرض العملاء\n"
        "/debts - عرض الديون\n"
        "/help - المساعدة\n\n"
        "يمكنك إرسال صورة فاتورة لتحليلها تلقائياً"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "دليل استخدام بوت ERP للأدوات الصحية\n\n"
        "الأوامر:\n"
        "/start - بدء استخدام البوت\n"
        "/products - عرض قائمة المنتجات\n"
        "/customers - عرض قائمة العملاء\n"
        "/debts - عرض الديون\n"
        "/help - عرض هذه المساعدة\n\n"
        "التحليل بالذكاء الاصطناعي:\n"
        "📸 أرسل صورة فاتورة لتحليلها تلقائياً\n"
        "📄 أرسل ملف PDF لتحليله\n\n"
        "يمكنك كتابة أي نص مالي لتحليله"
    )


async def products_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if telegram_settings.TELEGRAM_ALLOWED_USERS:
        if user_id not in telegram_settings.TELEGRAM_ALLOWED_USERS:
            await update.message.reply_text("ليس لديك صلاحية للوصول لهذه البيانات.")
            return

    await update.message.reply_text("جاري تحميل المنتجات...")

    token = await _get_token(context)
    if not token:
        await update.message.reply_text(
            "لم يتم العثور على بيانات تسجيل الدخول.\n"
            "يرجى تسجيل الدخول أولاً عبر الـ API."
        )
        return

    products = await api_client.get_products(token)
    if not products:
        await update.message.reply_text("لا توجد منتجات حالياً.")
        return

    lines = ["📦 *قائمة المنتجات*\n"]
    for i, product in enumerate(products[:20], 1):
        name = product.get("name", "غير محدد")
        sku = product.get("sku", "")
        price = product.get("selling_price") or product.get("unit_price", 0)
        quantity = product.get("quantity", 0)
        lines.append(
            f"{i}. {name}"
        )
        if sku:
            lines.append(f"   الكود: {sku}")
        lines.append(f"   السعر: {price} EGP | الكمية: {quantity}")
        lines.append("")

    if len(products) > 20:
        lines.append(f"و {len(products) - 20} منتج إضافي...")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def customers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if telegram_settings.TELEGRAM_ALLOWED_USERS:
        if user_id not in telegram_settings.TELEGRAM_ALLOWED_USERS:
            await update.message.reply_text("ليس لديك صلاحية للوصول لهذه البيانات.")
            return

    await update.message.reply_text("جاري تحميل العملاء...")

    token = await _get_token(context)
    if not token:
        await update.message.reply_text(
            "لم يتم العثور على بيانات تسجيل الدخول.\n"
            "يرجى تسجيل الدخول أولاً عبر الـ API."
        )
        return

    customers = await api_client.get_customers(token)
    if not customers:
        await update.message.reply_text("لا يوجد عملاء حالياً.")
        return

    lines = ["👥 *قائمة العملاء*\n"]
    for i, customer in enumerate(customers[:20], 1):
        name = customer.get("name", "غير محدد")
        phone = customer.get("phone", "")
        address = customer.get("address", "")
        lines.append(f"{i}. {name}")
        if phone:
            lines.append(f"   الهاتف: {phone}")
        if address:
            lines.append(f"   العنوان: {address}")
        lines.append("")

    if len(customers) > 20:
        lines.append(f"و {len(customers) - 20} عميل إضافي...")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def debts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if telegram_settings.TELEGRAM_ALLOWED_USERS:
        if user_id not in telegram_settings.TELEGRAM_ALLOWED_USERS:
            await update.message.reply_text("ليس لديك صلاحية للوصول لهذه البيانات.")
            return

    await update.message.reply_text("جاري تحميل الديون...")

    token = await _get_token(context)
    if not token:
        await update.message.reply_text(
            "لم يتم العثور على بيانات تسجيل الدخول.\n"
            "يرجى تسجيل الدخول أولاً عبر الـ API."
        )
        return

    debts = await api_client.get_customer_debts(token)
    if not debts:
        await update.message.reply_text("لا توجد ديون حالياً.")
        return

    lines = ["📋 *قائمة الديون*\n"]
    total_debt = 0
    for i, debt in enumerate(debts[:20], 1):
        customer_name = debt.get("customer_name", "غير محدد")
        amount = debt.get("amount", 0)
        description = debt.get("description", "")
        total_debt += float(amount)
        lines.append(f"{i}. {customer_name}: {amount} EGP")
        if description:
            lines.append(f"   الوصف: {description}")
        lines.append("")

    lines.append(f"**الإجمالي: {total_debt:.2f} EGP**")

    if len(debts) > 20:
        lines.append(f"\nو {len(debts) - 20} سجل إضافي...")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def _get_token(context: ContextTypes.DEFAULT_TYPE) -> str | None:
    if context.user_data and "token" in context.user_data:
        return context.user_data["token"]
    return None
