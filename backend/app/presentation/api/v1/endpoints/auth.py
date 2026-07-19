from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
)
from app.application.use_cases.auth_use_cases import (
    ChangePasswordUseCase,
    LoginUseCase,
    RefreshTokenUseCase,
    RegisterUseCase,
)
from app.core.dependencies import get_current_user
from app.infrastructure.database import get_db
from app.infrastructure.repositories.user_repository import UserRepositoryImpl

from pydantic import BaseModel

router = APIRouter()


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRepositoryImpl(db)
    use_case = LoginUseCase(repo)
    result = await use_case.execute(request.username, request.password)
    return {"success": True, "data": result, "message": "Login successful"}


@router.post("/register")
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = UserRepositoryImpl(db)
    use_case = RegisterUseCase(repo)
    user_id = await use_case.execute(
        request.username,
        request.email,
        request.password,
        request.full_name,
        request.role,
    )
    return {"success": True, "data": {"user_id": user_id}, "message": "Registration successful"}


@router.post("/refresh")
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    repo = UserRepositoryImpl(db)
    use_case = RefreshTokenUseCase(repo)
    result = await use_case.execute(request.refresh_token)
    return {"success": True, "data": result}


@router.post("/logout")
async def logout(user=Depends(get_current_user)):
    return {"success": True, "message": "Logged out"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    repo = UserRepositoryImpl(db)
    use_case = ChangePasswordUseCase(repo)
    await use_case.execute(user["id"], request.old_password, request.new_password)
    return {"success": True, "message": "Password changed"}


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    return {"success": True, "data": user}
