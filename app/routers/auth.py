"""Authentication router for user verification and session management."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import (
    CurrentUser,
    get_current_user,
    get_current_user_optional,
    OptionalUser,
    RequiredUser,
)
from app.services.usage import UsageService, get_usage_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class UserResponse(BaseModel):
    """Response for user info endpoint."""

    id: str
    email: str | None
    name: str | None
    plan: str
    is_pro: bool


class UsageResponse(BaseModel):
    """Response for usage info endpoint."""

    compress: dict
    merge: dict
    image_to_pdf: dict


class MeResponse(BaseModel):
    """Response for /me endpoint."""

    user: UserResponse
    usage: UsageResponse


@router.get("/me", response_model=MeResponse)
async def get_current_user_info(
    current_user: RequiredUser,
    db: AsyncSession = Depends(get_db),
    usage_service: UsageService = Depends(get_usage_service),
) -> MeResponse:
    """
    Get current user information and usage stats.

    Requires authentication via JWT token.
    """
    # Get today's usage
    usage = await usage_service.get_today_remaining(
        db=db,
        user_id=current_user.id,
        is_pro=current_user.is_pro,
    )

    return MeResponse(
        user=UserResponse(
            id=str(current_user.id),
            email=current_user.email,
            name=current_user.name,
            plan=current_user.plan,
            is_pro=current_user.is_pro,
        ),
        usage=UsageResponse(**usage),
    )


@router.get("/verify")
async def verify_token(
    current_user: OptionalUser,
) -> dict:
    """
    Verify if the current token is valid.

    Returns user info if authenticated, or indicates anonymous access.
    """
    if current_user:
        return {
            "authenticated": True,
            "user_id": str(current_user.id),
            "plan": current_user.plan,
            "is_pro": current_user.is_pro,
        }

    return {
        "authenticated": False,
        "user_id": None,
        "plan": "free",
        "is_pro": False,
    }
