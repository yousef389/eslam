from pydantic_settings import BaseSettings


class TelegramSettings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    TELEGRAM_ALLOWED_USERS: list[str] = []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


telegram_settings = TelegramSettings()
