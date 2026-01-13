"""Firebase Authentication service for verifying ID tokens."""

import json
from dataclasses import dataclass

import firebase_admin
from firebase_admin import auth, credentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import User, Account


@dataclass
class FirebaseUserInfo:
    """Verified Firebase user information."""

    uid: str
    email: str | None
    email_verified: bool
    name: str | None
    picture: str | None
    provider: str  # google.com, apple.com, password, etc.


class FirebaseAuthError(Exception):
    """Raised when Firebase token verification fails."""

    pass


class FirebaseAuthService:
    """Service for Firebase ID token verification."""

    _initialized: bool = False

    def __init__(self):
        self._initialize_firebase()

    def _initialize_firebase(self) -> None:
        """Initialize Firebase Admin SDK if not already initialized."""
        if FirebaseAuthService._initialized:
            return

        settings = get_settings()
        if not settings.firebase_credentials_json:
            return

        try:
            cred_dict = json.loads(settings.firebase_credentials_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            FirebaseAuthService._initialized = True
        except (json.JSONDecodeError, ValueError) as e:
            raise FirebaseAuthError(f"Invalid Firebase credentials: {e}")

    async def verify_token(self, token: str) -> FirebaseUserInfo:
        """
        Verify Firebase ID token and extract user info.

        Args:
            token: Firebase ID token from frontend

        Returns:
            FirebaseUserInfo with verified claims

        Raises:
            FirebaseAuthError: If verification fails
        """
        if not FirebaseAuthService._initialized:
            raise FirebaseAuthError("Firebase not configured")

        try:
            decoded = auth.verify_id_token(token)

            # Get the sign-in provider
            firebase_info = decoded.get("firebase", {})
            provider = firebase_info.get("sign_in_provider", "unknown")

            return FirebaseUserInfo(
                uid=decoded["uid"],
                email=decoded.get("email"),
                email_verified=decoded.get("email_verified", False),
                name=decoded.get("name"),
                picture=decoded.get("picture"),
                provider=provider,
            )
        except auth.InvalidIdTokenError as e:
            raise FirebaseAuthError(f"Invalid token: {e}")
        except auth.ExpiredIdTokenError:
            raise FirebaseAuthError("Token expired")
        except auth.RevokedIdTokenError:
            raise FirebaseAuthError("Token revoked")
        except auth.CertificateFetchError as e:
            raise FirebaseAuthError(f"Failed to fetch certificates: {e}")
        except Exception as e:
            raise FirebaseAuthError(f"Token verification failed: {e}")

    async def find_or_create_user(
        self, db: AsyncSession, info: FirebaseUserInfo
    ) -> tuple[User, bool]:
        """
        Find existing user or create new one from Firebase info.

        Matching logic (in priority order):
        1. Existing Account with provider='firebase' and provider_account_id=uid
        2. Existing User with matching email (link Firebase account)
        3. Create new User + Account

        Args:
            db: Database session
            info: Verified Firebase user information

        Returns:
            Tuple of (User, is_new_user)
        """
        from datetime import datetime, timezone

        # 1. Check for existing Firebase account
        result = await db.execute(
            select(Account).where(
                Account.provider == "firebase",
                Account.provider_account_id == info.uid,
            )
        )
        account = result.scalar_one_or_none()

        if account:
            result = await db.execute(select(User).where(User.id == account.user_id))
            user = result.scalar_one()
            # Update user info if changed
            updated = False
            if info.name and user.name != info.name:
                user.name = info.name
                updated = True
            if info.picture and user.image != info.picture:
                user.image = info.picture
                updated = True
            if updated:
                await db.commit()
                await db.refresh(user)
            return user, False

        # 2. Check for existing user by email
        if info.email:
            result = await db.execute(select(User).where(User.email == info.email))
            user = result.scalar_one_or_none()

            if user:
                # Link Firebase account to existing user
                db.add(
                    Account(
                        user_id=user.id,
                        type="oauth",
                        provider="firebase",
                        provider_account_id=info.uid,
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
                provider="firebase",
                provider_account_id=info.uid,
            )
        )
        await db.commit()
        await db.refresh(user)

        return user, True


_service: FirebaseAuthService | None = None


def get_firebase_auth_service() -> FirebaseAuthService:
    """Dependency for getting Firebase auth service instance."""
    global _service
    if _service is None:
        _service = FirebaseAuthService()
    return _service
