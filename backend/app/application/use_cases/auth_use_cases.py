from __future__ import annotations

from datetime import datetime

from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.domain.entities import User
from app.domain.enums import UserRole


class LoginUseCase:
    def __init__(self, users_repo):
        self.users_repo = users_repo

    async def execute(self, username: str, password: str) -> dict:
        user = await self.users_repo.get_by_username(username)
        if not user:
            raise UnauthorizedException("Invalid username or password")

        if not user.is_active:
            raise UnauthorizedException("Account is inactive")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid username or password")

        user.last_login = datetime.utcnow()
        await self.users_repo.update(user)

        token_data = {"sub": user.id, "role": user.role.value}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }


class RegisterUseCase:
    def __init__(self, users_repo):
        self.users_repo = users_repo

    async def execute(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: str = "staff",
    ) -> str:
        existing = await self.users_repo.get_by_username(username)
        if existing:
            raise ConflictException(f"Username '{username}' already exists")

        existing_email = await self.users_repo.get_by_email(email)
        if existing_email:
            raise ConflictException(f"Email '{email}' already exists")

        try:
            user_role = UserRole(role)
        except ValueError:
            raise ValidationException(f"Invalid role: {role}")

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=get_password_hash(password),
            role=user_role,
        )

        created = await self.users_repo.create(user)
        return created.id


class RefreshTokenUseCase:
    def __init__(self, users_repo):
        self.users_repo = users_repo

    async def execute(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload:
            raise UnauthorizedException("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid token payload")

        user = await self.users_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        if not user.is_active:
            raise UnauthorizedException("Account is inactive")

        token_data = {"sub": user.id, "role": user.role.value}
        new_access = create_access_token(token_data)
        new_refresh = create_refresh_token(token_data)

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }


class LogoutUseCase:
    def __init__(self, token_revocation_service):
        self.token_revocation_service = token_revocation_service

    async def execute(self, jti: str, expires_at: datetime) -> None:
        await self.token_revocation_service.revoke_token(jti, expires_at)


class ChangePasswordUseCase:
    def __init__(self, users_repo):
        self.users_repo = users_repo

    async def execute(
        self, user_id: str, old_password: str, new_password: str
    ) -> None:
        user = await self.users_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)

        if not verify_password(old_password, user.password_hash):
            raise UnauthorizedException("Current password is incorrect")

        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        await self.users_repo.update(user)


class GetCurrentUserUseCase:
    def __init__(self, users_repo):
        self.users_repo = users_repo

    async def execute(self, user_id: str) -> User:
        user = await self.users_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        return user
