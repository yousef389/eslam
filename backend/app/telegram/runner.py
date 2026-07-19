import asyncio
import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.telegram.config import telegram_settings
from app.telegram.handlers.commands import (
    customers_command,
    debts_command,
    help_command,
    products_command,
    start_command,
)
from app.telegram.handlers.images import handle_document, handle_photo
from app.telegram.handlers.messages import handle_message

logger = logging.getLogger(__name__)


def create_bot():
    app = ApplicationBuilder().token(telegram_settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("products", products_command))
    app.add_handler(CommandHandler("customers", customers_command))
    app.add_handler(CommandHandler("debts", debts_command))

    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    return app


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    if not telegram_settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set")
        return

    logger.info("Starting Telegram bot...")
    app = create_bot()
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
