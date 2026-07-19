import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.telegram.services.ai_analyzer import TelegramAIAnalyzer
from app.telegram.services.api_client import ERPAPIClient

logger = logging.getLogger(__name__)

analyzer = TelegramAIAnalyzer()
api_client = ERPAPIClient()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    if text.startswith("/"):
        return

    await update.message.reply_text("جاري تحليل النص...")

    try:
        from app.ai.service import AIService

        ai = AIService()
        result = await ai.analyze_text(text)
        response = analyzer.format_result(result)
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        logger.error("Text analysis failed: %s", e)
        await update.message.reply_text(
            "حدث خطأ أثناء تحليل النص.\nيرجى المحاولة مرة أخرى."
        )
