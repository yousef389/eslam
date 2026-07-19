from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    GOOGLE_API_KEY: str = ""
    AI_MODEL: str = "gemini-1.5-flash"
    AI_TEMPERATURE: float = 0.1
    AI_MAX_TOKENS: int = 4096

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_ai_settings() -> AISettings:
    return AISettings()
