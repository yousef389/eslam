from __future__ import annotations

from typing import Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.domain.enums import UserRole
from app.infrastructure.database import async_session_factory
from app.infrastructure.repositories.user_repository import UserRepositoryImpl

security_scheme = HTTPBearer()

role_permissions: dict[str, list[str]] = {
    "admin": ["*"],
    "manager": [
        "products:read", "products:write",
        "customers:read", "customers:write",
        "suppliers:read", "suppliers:write",
        "orders:read", "orders:write",
        "reports:read",
        "accounting:read", "accounting:write",
    ],
    "staff": [
        "products:read",
        "customers:read", "customers:write",
        "orders:read", "orders:write",
    ],
    "cashier": [
        "products:read",
        "customers:read",
        "orders:read",
        "accounting:read", "accounting:write",
    ],
}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise UnauthorizedException("Invalid or expired token")

    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type")

    jti = payload.get("jti")
    if jti:
        from app.infrastructure.cache import redis_client

        if await redis_client.get(f"token_revoked:{jti}"):
            raise UnauthorizedException("Token has been revoked")

        user_id = payload.get("sub")
        if user_id:
            revoked_all = await redis_client.get(f"revoked_all:{user_id}")
            if revoked_all:
                raise UnauthorizedException("All tokens revoked")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    async with async_session_factory() as session:
        repo = UserRepositoryImpl(session)
        user = await repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise UnauthorizedException("User account is inactive")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "full_name": user.full_name,
    }


async def get_current_user_from_refresh(token: str) -> dict:
    payload = decode_token(token)

    if payload is None:
        raise UnauthorizedException("Invalid or expired refresh token")

    if payload.get("type") != "refresh":
        raise UnauthorizedException("Invalid token type")

    jti = payload.get("jti")
    if jti:
        from app.infrastructure.cache import redis_client

        if await redis_client.get(f"token_revoked:{jti}"):
            raise UnauthorizedException("Refresh token has been revoked")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload")

    async with async_session_factory() as session:
        repo = UserRepositoryImpl(session)
        user = await repo.get_by_id(user_id)

    if not user:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise UnauthorizedException("User account is inactive")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "full_name": user.full_name,
    }


def require_role(*roles: UserRole) -> Callable:
    async def role_checker(request: Request) -> dict:
        user = request.state.user
        if not user:
            raise UnauthorizedException()

        user_role = user.get("role")
        if user_role not in [r.value for r in roles]:
            raise ForbiddenException(
                f"Required role: {', '.join(r.value for r in roles)}"
            )
        return user

    return role_checker


def require_permission(permission: str) -> Callable:
    async def permission_checker(request: Request) -> dict:
        user = request.state.user
        if not user:
            raise UnauthorizedException()

        user_role = user.get("role", "")
        permissions = role_permissions.get(user_role, [])

        if "*" in permissions or permission in permissions:
            return user

        raise ForbiddenException(f"Missing permission: {permission}")

    return permission_checker
