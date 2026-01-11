"""Authentication middleware for JWT and API key verification."""

from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.exceptions import http_authentication_error
from app.models import User

settings = get_settings()

# Security scheme
bearer_scheme = HTTPBearer(auto_error=False)


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # User ID
    email: str | None = None
    name: str | None = None
    plan: str = "free"
    exp: datetime | None = None


class CurrentUser(BaseModel):
    """Current authenticated user."""

    id: UUID
    email: str | None = None
    name: str | None = None
    plan: str = "free"
    is_pro: bool = False

    @classmethod
    def from_db_user(cls, user: User) -> "CurrentUser":
        """Create from database user model."""
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            plan=user.plan,
            is_pro=user.is_pro,
        )


def create_access_token(
    user_id: str,
    email: str | None = None,
    name: str | None = None,
    plan: str = "free",
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: User ID (string UUID)
        email: User email
        name: User name
        plan: User plan (free/pro)
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiry_hours)

    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "plan": plan,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> TokenPayload:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return TokenPayload(**payload)
    except JWTError as e:
        raise http_authentication_error(f"Invalid token: {e}")


async def get_current_user_optional(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser | None:
    """
    Get current user if authenticated, None otherwise.

    Use this for endpoints that work for both authenticated and anonymous users.
    """
    if not credentials:
        return None

    token = credentials.credentials

    # Check if it's an API key (starts with sk_)
    if token.startswith("sk_"):
        # API key authentication is handled separately
        return None

    try:
        payload = decode_token(token)

        # Optionally verify user exists in database
        user_id = UUID(payload.sub)
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            return CurrentUser.from_db_user(user)

        # Return from token if user not in DB (e.g., NextAuth user)
        return CurrentUser(
            id=user_id,
            email=payload.email,
            name=payload.name,
            plan=payload.plan,
            is_pro=payload.plan == "pro",
        )

    except Exception:
        return None


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUser:
    """
    Get current authenticated user.

    Raises HTTPException if not authenticated.
    """
    if not credentials:
        raise http_authentication_error("Authentication required")

    token = credentials.credentials

    # Check if it's an API key
    if token.startswith("sk_"):
        raise http_authentication_error("Use API key authentication endpoint")

    payload = decode_token(token)

    try:
        user_id = UUID(payload.sub)
    except ValueError:
        raise http_authentication_error("Invalid user ID in token")

    # Try to get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user:
        return CurrentUser.from_db_user(user)

    # Return from token if user not in DB
    return CurrentUser(
        id=user_id,
        email=payload.email,
        name=payload.name,
        plan=payload.plan,
        is_pro=payload.plan == "pro",
    )


async def get_current_pro_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """
    Get current user and verify they have Pro subscription.

    Raises HTTPException if not Pro.
    """
    if not current_user.is_pro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pro subscription required for this feature",
        )
    return current_user


# Type aliases for dependency injection
OptionalUser = Annotated[CurrentUser | None, Depends(get_current_user_optional)]
RequiredUser = Annotated[CurrentUser, Depends(get_current_user)]
ProUser = Annotated[CurrentUser, Depends(get_current_pro_user)]
