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
        use_case = RegisterUseCase(repo)
        try:
            await use_case.execute("admin", "admin@erp.com", "admin123", "Administrator", "admin")
            await db.commit()
            logger.info("Admin user seeded")
        except Exception:
            await db.rollback()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")

    try:
        await create_tables()
        await seed_admin_user()
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
