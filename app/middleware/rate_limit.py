"""Rate limiting middleware and dependencies."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.exceptions import RateLimitError, http_rate_limit_error
from app.services.usage import UsageService, get_usage_service
from app.middleware.api_key import get_api_key_user
from app.middleware.auth import CurrentUser

settings = get_settings()

bearer_scheme = HTTPBearer(auto_error=False)


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.

    Handles X-Forwarded-For header for proxy setups.
    """
    # Check for forwarded header (common with proxies/load balancers)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP in the chain (original client)
        return forwarded.split(",")[0].strip()

    # Check for X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct client IP
    if request.client:
        return request.client.host

    return "unknown"


class RateLimitChecker:
    """Dependency for checking rate limits with optional API key authentication."""

    def __init__(self, tool: str):
        self.tool = tool

    async def __call__(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
        db: AsyncSession = Depends(get_db),
        usage_service: UsageService = Depends(get_usage_service),
    ) -> dict:
        """
        Check rate limit for the tool.

        If a valid API key is provided, the user gets Pro access (no rate limits).
        Otherwise, free tier rate limits are applied based on IP address.

        Returns user context if allowed, raises exception if rate limited.
        """
        user_id: UUID | None = None
        is_pro = False
        api_user: CurrentUser | None = None

        # Try to authenticate via API key
        if credentials and credentials.credentials.startswith("sk_"):
            try:
                api_user = await get_api_key_user(request, credentials, db)
                if api_user:
                    user_id = api_user.id
                    is_pro = True
            except Exception:
                # Invalid API key - fall through to free tier
                pass

        # Get client IP for anonymous rate limiting
        ip_address = get_client_ip(request)

        # Pro users skip rate limiting
        if is_pro:
            return {
                "user_id": user_id,
                "ip_address": ip_address,
                "is_pro": True,
                "usage_count": 0,
                "usage_limit": 0,  # 0 means unlimited
            }

        # Check rate limit for free tier
        allowed, current, limit = await usage_service.check_rate_limit(
            db=db,
            tool=self.tool,
            user_id=user_id,
            ip_address=ip_address,
            is_pro=is_pro,
        )

        if not allowed:
            raise http_rate_limit_error(self.tool, limit)

        return {
            "user_id": user_id,
            "ip_address": ip_address,
            "is_pro": is_pro,
            "usage_count": current,
            "usage_limit": limit,
        }


# Pre-configured rate limit checkers for each tool
compress_rate_limit = RateLimitChecker("compress")
merge_rate_limit = RateLimitChecker("merge")
image_to_pdf_rate_limit = RateLimitChecker("image_to_pdf")


# Type aliases for dependency injection
CompressRateLimit = Annotated[dict, Depends(compress_rate_limit)]
MergeRateLimit = Annotated[dict, Depends(merge_rate_limit)]
ImageToPdfRateLimit = Annotated[dict, Depends(image_to_pdf_rate_limit)]
