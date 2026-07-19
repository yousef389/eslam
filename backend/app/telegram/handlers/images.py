import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.telegram.services.ai_analyzer import TelegramAIAnalyzer
from app.telegram.services.file_processor import FileProcessor

logger = logging.getLogger(__name__)

analyzer = TelegramAIAnalyzer()


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    await update.message.reply_text("جاري تحليل الصورة...")

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()
        mime_type = "image/jpeg"

        if file.file_path:
            if file.file_path.lower().endswith(".png"):
                mime_type = "image/png"
            elif file.file_path.lower().endswith(".webp"):
                mime_type = "image/webp"

        response = await analyzer.analyze_photo(bytes(file_bytes), mime_type)
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        logger.error("Photo analysis failed: %s", e)
        await update.message.reply_text(
            "حدث خطأ أثناء تحليل الصورة.\n"
            "يرجى التأكد من أن الصورة واضحة وواضحة."
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.document:
        return

    document = update.message.document
    if not document.file_name:
        await update.message.reply_text("يرجى إرسال ملف باسم صحيح.")
        return

    filename = document.file_name.lower()
    if not (filename.endswith(".pdf") or filename.endswith(".png") or
            filename.endswith(".jpg") or filename.endswith(".jpeg")):
        await update.message.reply_text(
            "الصيغة غير مدعومة.\n"
            "يرجى إرسال ملف PDF أو صورة (PNG/JPG)."
        )
        return

    await update.message.reply_text("جاري تحليل الملف...")

    try:
        file_bytes, fname = await FileProcessor.download_file(
            context.bot, document.file_id
        )

        if filename.endswith(".pdf"):
            response = await analyzer.analyze_document(file_bytes, fname)
        else:
            mime_type = FileProcessor.get_mime_type(fname)
            response = await analyzer.analyze_photo(file_bytes, mime_type)

        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        logger.error("Document analysis failed: %s", e)
        await update.message.reply_text(
            "حدث خطأ أثناء تحليل الملف.\n"
            "يرجى المحاولة مرة أخرى."
        )
