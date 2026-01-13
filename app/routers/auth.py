"""Authentication router for user verification and session management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import (
    CurrentUser,
    create_access_token,
    get_current_user,
    get_current_user_optional,
    OptionalUser,
    RequiredUser,
)
from app.services.firebase_auth import (
    FirebaseAuthError,
    FirebaseAuthService,
    get_firebase_auth_service,
)
from app.services.usage import UsageService, get_usage_service

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class UserResponse(BaseModel):
    """Response for user info endpoint."""

    id: str = Field(..., description="User ID", example="550e8400-e29b-41d4-a716-446655440000")
    email: str | None = Field(None, description="User email address", example="user@example.com")
    name: str | None = Field(None, description="User display name", example="John Doe")
    plan: str = Field(..., description="Subscription plan (free, pro)", example="pro")
    is_pro: bool = Field(..., description="Whether user has Pro subscription", example=True)


class UsageResponse(BaseModel):
    """Response for usage info endpoint."""

    compress: dict = Field(..., description="Compression usage stats", example={"used": 1, "limit": 2, "remaining": 1})
    merge: dict = Field(..., description="Merge usage stats", example={"used": 0, "limit": 2, "remaining": 2})
    image_to_pdf: dict = Field(..., description="Image-to-PDF usage stats", example={"used": 2, "limit": 2, "remaining": 0})


class MeResponse(BaseModel):
    """Response for /me endpoint."""

    user: UserResponse = Field(..., description="User information")
    usage: UsageResponse = Field(..., description="Today's usage statistics")


class FirebaseAuthRequest(BaseModel):
    """Request for Firebase authentication."""

    id_token: str = Field(..., description="Firebase ID token from frontend")


class AuthTokenResponse(BaseModel):
    """Response with backend JWT token."""

    access_token: str = Field(..., description="Backend JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: UserResponse = Field(..., description="Authenticated user info")
    is_new_user: bool = Field(..., description="Whether this is a newly created account")


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


@router.post("/firebase", response_model=AuthTokenResponse)
async def firebase_auth(
    request: FirebaseAuthRequest,
    db: AsyncSession = Depends(get_db),
    firebase_service: FirebaseAuthService = Depends(get_firebase_auth_service),
) -> AuthTokenResponse:
    """
    Authenticate with Firebase.

    Exchange a Firebase ID token for a backend JWT access token.
    Supports all Firebase auth providers (Google, Apple, email/password, etc.).
    Creates a new user account if one doesn't exist.
    """
    try:
        firebase_info = await firebase_service.verify_token(request.id_token)
    except FirebaseAuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    user, is_new_user = await firebase_service.find_or_create_user(db, firebase_info)

    settings = get_settings()
    access_token = create_access_token(
        user_id=str(user.id),
        email=user.email,
        name=user.name,
        plan=user.plan,
    )

    return AuthTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.jwt_expiry_hours * 3600,
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            plan=user.plan,
            is_pro=user.is_pro,
        ),
        is_new_user=is_new_user,
    )
