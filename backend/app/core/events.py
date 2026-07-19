from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.cache import redis_client
from app.infrastructure.database import engine, Base, async_session_factory
from app.infrastructure.models import *  # noqa: F401 - import all models
from app.core.token_revocation import TokenRevocationService

logger = logging.getLogger("app.lifecycle")

token_revocation_service = TokenRevocationService(redis_client)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def seed_admin_user():
    from app.infrastructure.repositories.user_repository import UserRepositoryImpl
    from app.application.use_cases.auth_use_cases import RegisterUseCase

    async with async_session_factory() as db:
        repo = UserRepositoryImpl(db)
        existing = await repo.get_by_username("admin")
        if existing:
            logger.info("Admin user already exists, skipping seed")
            return
        use_case = RegisterUseCase(repo)
        try:
            await use_case.execute(
                "admin",
                "admin@erp.com",
                "Admin@12345",
                "Administrator",
                "admin",
            )
            await db.commit()
            logger.info("Admin user seeded successfully")
        except Exception as e:
            await db.rollback()
            logger.warning("Admin seed skipped: %s", e)


async def seed_default_settings():
    from app.infrastructure.repositories.system_setting_repository import SystemSettingRepositoryImpl
    from app.domain.enums import SettingsGroup

    default_settings = [
        ("ai_provider", "gemini", SettingsGroup.AI, "AI Provider (gemini/openai/ollama)", False),
        ("ai_gemini_api_key", "", SettingsGroup.AI, "Gemini API Key", True),
        ("ai_gemini_model", "gemini-1.5-flash", SettingsGroup.AI, "Gemini Model", False),
        ("ai_temperature", "0.1", SettingsGroup.AI, "AI Temperature", False),
        ("ai_max_tokens", "4096", SettingsGroup.AI, "AI Max Tokens", False),
        ("ai_openai_api_key", "", SettingsGroup.AI, "OpenAI API Key", True),
        ("ai_openai_model", "gpt-4", SettingsGroup.AI, "OpenAI Model", False),
        ("ai_ollama_url", "http://localhost:11434", SettingsGroup.AI, "Ollama URL", False),
        ("ai_ollama_model", "llama2", SettingsGroup.AI, "Ollama Model", False),

        ("telegram_bot_token", "", SettingsGroup.TELEGRAM, "Telegram Bot Token", True),
        ("telegram_chat_id", "", SettingsGroup.TELEGRAM, "Telegram Chat ID", False),
        ("telegram_webhook_url", "", SettingsGroup.TELEGRAM, "Telegram Webhook URL", False),

        ("backend_url", "http://localhost:8000", SettingsGroup.API, "Backend URL", False),
        ("api_version", "v1", SettingsGroup.API, "API Version", False),

        ("jwt_secret_key", "", SettingsGroup.SECURITY, "JWT Secret Key", True),
        ("session_timeout_minutes", "30", SettingsGroup.SECURITY, "Session Timeout (minutes)", False),

        ("store_name", "الأدوات الصحية", SettingsGroup.STORE, "Store Name", False),
        ("store_logo", "", SettingsGroup.STORE, "Store Logo URL", False),
        ("store_phone", "", SettingsGroup.STORE, "Store Phone", False),
        ("store_address", "", SettingsGroup.STORE, "Store Address", False),
    ]

    async with async_session_factory() as db:
        repo = SystemSettingRepositoryImpl(db)
        try:
            for key, value, group, description, is_secret in default_settings:
                existing = await repo.get_by_key(key)
                if not existing:
                    await repo.set_setting(key, value, group, description, is_secret)
            await db.commit()
            logger.info("Default settings seeded")
        except Exception as e:
            await db.rollback()
            logger.warning("Settings seed failed: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")

    try:
        await create_tables()
        await seed_admin_user()
        await seed_default_settings()
    except Exception as e:
        logger.warning(f"Database init failed: {e}")

    try:
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")

    try:
        await token_revocation_service.init()
        logger.info("Token revocation service initialized")
    except Exception as e:
        logger.warning(f"Token revocation service init failed: {e}")

    yield

    logger.info("Shutting down application...")

    try:
        await token_revocation_service.close()
    except Exception:
        pass

    try:
        await redis_client.aclose()
    except Exception:
        pass

    logger.info("Shutdown complete")
