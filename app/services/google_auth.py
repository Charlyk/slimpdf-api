"""Google OAuth token verification service."""

from dataclasses import dataclass
from datetime import datetime, timezone

from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import User, Account


@dataclass
class GoogleUserInfo:
    """Verified Google user information."""

    google_id: str
    email: str
    email_verified: bool
    name: str | None
    picture: str | None


class GoogleAuthError(Exception):
    """Raised when Google token verification fails."""

    pass


class GoogleAuthService:
    """Service for Google OAuth token verification."""

    def __init__(self):
        self._request = requests.Request()

    async def verify_token(self, token: str) -> GoogleUserInfo:
        """
        Verify Google ID token and extract user info.

        Args:
            token: Google ID token from frontend

        Returns:
            GoogleUserInfo with verified claims

        Raises:
            GoogleAuthError: If verification fails
        """
        settings = get_settings()
        if not settings.google_client_id:
            raise GoogleAuthError("Google OAuth not configured")

        try:
            idinfo = id_token.verify_oauth2_token(
                token, self._request, settings.google_client_id
            )
            if idinfo.get("iss") not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise GoogleAuthError("Invalid token issuer")

            return GoogleUserInfo(
                google_id=idinfo["sub"],
                email=idinfo["email"],
                email_verified=idinfo.get("email_verified", False),
                name=idinfo.get("name"),
                picture=idinfo.get("picture"),
            )
        except ValueError as e:
            raise GoogleAuthError(f"Invalid token: {e}")

    async def find_or_create_user(
        self, db: AsyncSession, info: GoogleUserInfo
    ) -> tuple[User, bool]:
        """
        Find existing user or create new one from Google info.

        Matching logic (in priority order):
        1. Existing Account with provider='google' and provider_account_id=google_id
        2. Existing User with matching email (link Google account)
        3. Create new User + Account

        Args:
            db: Database session
            info: Verified Google user information

        Returns:
            Tuple of (User, is_new_user)
        """
        # 1. Check for existing Google account
        result = await db.execute(
            select(Account).where(
                Account.provider == "google",
                Account.provider_account_id == info.google_id,
            )
        )
        account = result.scalar_one_or_none()

        if account:
            result = await db.execute(select(User).where(User.id == account.user_id))
            return result.scalar_one(), False

        # 2. Check for existing user by email
        result = await db.execute(select(User).where(User.email == info.email))
        user = result.scalar_one_or_none()

        if user:
            # Link Google account to existing user
            db.add(
                Account(
                    user_id=user.id,
                    type="oauth",
                    provider="google",
                    provider_account_id=info.google_id,
                )
            )
            await db.commit()
            return user, False

        # 3. Create new user
        user = User(
            email=info.email,
            email_verified=datetime.now(timezone.utc) if info.email_verified else None,
            name=info.name,
            image=info.picture,
            plan="free",
        )
        db.add(user)
        await db.flush()

        db.add(
            Account(
                user_id=user.id,
                type="oauth",
                provider="google",
                provider_account_id=info.google_id,
            )
        )
        await db.commit()
        await db.refresh(user)

        return user, True


_service = GoogleAuthService()


def get_google_auth_service() -> GoogleAuthService:
    """Dependency for getting Google auth service instance."""
    return _service
