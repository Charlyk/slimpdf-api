"""API key authentication for Pro users."""

import hashlib
import secrets
from datetime import datetime
from typing import Annotated
from uuid import UUID

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import http_authentication_error
from app.models import ApiKey, User
from app.middleware.auth import CurrentUser

bearer_scheme = HTTPBearer(auto_error=False)


def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a new API key.

    Returns:
        Tuple of (full_key, key_prefix, key_hash)
    """
    # Generate random bytes and create key
    random_bytes = secrets.token_bytes(32)
    key_suffix = secrets.token_urlsafe(32)
    full_key = f"sk_live_{key_suffix}"

    # Create prefix for display (first 12 chars after sk_live_)
    key_prefix = f"sk_live_{key_suffix[:8]}..."

    # Hash the key for storage
    key_hash = bcrypt.hashpw(full_key.encode(), bcrypt.gensalt()).decode()

    return full_key, key_prefix, key_hash


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against its hash.

    Args:
        plain_key: The plain text API key
        hashed_key: The bcrypt hash stored in database

    Returns:
        True if key matches
    """
    try:
        return bcrypt.checkpw(plain_key.encode(), hashed_key.encode())
    except Exception:
        return False


async def get_api_key_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser | None:
    """
    Authenticate user via API key.

    Returns None if no API key provided or if not an API key format.
    """
    if not credentials:
        return None

    token = credentials.credentials

    # Only handle API keys (start with sk_)
    if not token.startswith("sk_"):
        return None

    # Find API key by checking all active keys
    # Note: In production, use a more efficient lookup
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.revoked_at.is_(None)
        )
    )
    api_keys = result.scalars().all()

    matching_key: ApiKey | None = None
    for key in api_keys:
        if verify_api_key(token, key.key_hash):
            matching_key = key
            break

    if not matching_key:
        raise http_authentication_error("Invalid API key")

    # Update last used timestamp
    await db.execute(
        update(ApiKey)
        .where(ApiKey.id == matching_key.id)
        .values(last_used_at=datetime.utcnow())
    )

    # Get the user
    result = await db.execute(
        select(User).where(User.id == matching_key.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise http_authentication_error("API key user not found")

    if not user.is_pro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API access requires Pro subscription",
        )

    return CurrentUser(
        id=user.id,
        email=user.email,
        name=user.name,
        plan=user.plan,
        is_pro=True,
    )


async def get_api_key_user_required(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """
    Require API key authentication.

    Raises HTTPException if not authenticated with valid API key.
    """
    if not credentials:
        raise http_authentication_error("API key required")

    token = credentials.credentials

    if not token.startswith("sk_"):
        raise http_authentication_error("Invalid API key format. Expected sk_live_...")

    user = await get_api_key_user(request, credentials, db)

    if not user:
        raise http_authentication_error("Invalid API key")

    return user


async def create_api_key_for_user(
    db: AsyncSession,
    user_id: UUID,
    name: str = "Default",
) -> tuple[str, ApiKey]:
    """
    Create a new API key for a user.

    Args:
        db: Database session
        user_id: User ID
        name: Name for the API key

    Returns:
        Tuple of (plain_key, ApiKey model)
        Note: plain_key is only returned once and cannot be retrieved later
    """
    full_key, key_prefix, key_hash = generate_api_key()

    api_key = ApiKey(
        user_id=user_id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=name,
    )

    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return full_key, api_key


async def revoke_api_key(
    db: AsyncSession,
    key_id: UUID,
    user_id: UUID,
) -> bool:
    """
    Revoke an API key.

    Args:
        db: Database session
        key_id: API key ID
        user_id: User ID (for authorization)

    Returns:
        True if key was revoked
    """
    result = await db.execute(
        update(ApiKey)
        .where(
            ApiKey.id == key_id,
            ApiKey.user_id == user_id,
            ApiKey.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.utcnow())
    )
    await db.commit()
    return result.rowcount > 0


# Type aliases
ApiKeyUser = Annotated[CurrentUser, Depends(get_api_key_user_required)]
OptionalApiKeyUser = Annotated[CurrentUser | None, Depends(get_api_key_user)]
