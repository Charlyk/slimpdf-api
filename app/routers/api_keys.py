"""API key management router for Pro users."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import ProUser
from app.middleware.api_key import create_api_key_for_user, revoke_api_key
from app.models import ApiKey

router = APIRouter(prefix="/api/v1/keys", tags=["api-keys"])


class ApiKeyResponse(BaseModel):
    """Response for API key info."""

    id: str
    name: str
    key_prefix: str
    created_at: datetime
    last_used_at: datetime | None
    is_active: bool


class ApiKeyCreateResponse(BaseModel):
    """Response when creating a new API key."""

    id: str
    name: str
    key: str  # Full key - only shown once!
    key_prefix: str
    created_at: datetime
    message: str


class ApiKeyCreateRequest(BaseModel):
    """Request to create a new API key."""

    name: str = "Default"


@router.get("", response_model=list[ApiKeyResponse])
async def list_api_keys(
    current_user: ProUser,
    db: AsyncSession = Depends(get_db),
) -> list[ApiKeyResponse]:
    """
    List all API keys for the current user.

    Requires Pro subscription.
    """
    result = await db.execute(
        select(ApiKey)
        .where(ApiKey.user_id == current_user.id)
        .order_by(ApiKey.created_at.desc())
    )
    keys = result.scalars().all()

    return [
        ApiKeyResponse(
            id=str(key.id),
            name=key.name,
            key_prefix=key.key_prefix,
            created_at=key.created_at,
            last_used_at=key.last_used_at,
            is_active=key.is_active,
        )
        for key in keys
    ]


@router.post("", response_model=ApiKeyCreateResponse)
async def create_api_key(
    current_user: ProUser,
    request: ApiKeyCreateRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiKeyCreateResponse:
    """
    Create a new API key.

    **Important:** The full API key is only shown once. Store it securely.

    Requires Pro subscription.
    """
    # Check if user has too many keys (limit to 5)
    result = await db.execute(
        select(ApiKey)
        .where(
            ApiKey.user_id == current_user.id,
            ApiKey.revoked_at.is_(None),
        )
    )
    existing_keys = result.scalars().all()

    if len(existing_keys) >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum of 5 active API keys allowed",
        )

    full_key, api_key = await create_api_key_for_user(
        db=db,
        user_id=current_user.id,
        name=request.name,
    )

    return ApiKeyCreateResponse(
        id=str(api_key.id),
        name=api_key.name,
        key=full_key,
        key_prefix=api_key.key_prefix,
        created_at=api_key.created_at,
        message="Store this key securely - it cannot be retrieved again!",
    )


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: ProUser,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Revoke an API key.

    Requires Pro subscription.
    """
    try:
        key_uuid = UUID(key_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid key ID",
        )

    revoked = await revoke_api_key(
        db=db,
        key_id=key_uuid,
        user_id=current_user.id,
    )

    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found or already revoked",
        )

    return {"message": "API key revoked successfully"}
