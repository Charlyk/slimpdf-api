"""Origin validation middleware for protecting internal API endpoints."""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import get_settings

settings = get_settings()

# Path prefixes that require Origin validation (frontend-only endpoints)
PROTECTED_PREFIXES = ["/v1/auth", "/v1/billing", "/v1/keys"]

# Paths exempt from Origin validation (use their own auth mechanisms)
EXEMPT_PATHS = ["/v1/billing/webhook"]


class OriginValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate Origin header for protected endpoints.

    This ensures that internal endpoints (auth, billing, api-keys) can only
    be accessed from the SlimPDF frontend, not from arbitrary scripts or tools.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Skip validation for public endpoints
        if not self._is_protected_path(path):
            return await call_next(request)

        # Skip validation for exempt paths (webhooks use signature verification)
        if path in EXEMPT_PATHS:
            return await call_next(request)

        # Allow OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Validate Origin header
        origin = request.headers.get("origin")
        if not self._is_allowed_origin(origin):
            raise HTTPException(
                status_code=403,
                detail="Forbidden: Invalid or missing Origin header"
            )

        return await call_next(request)

    def _is_protected_path(self, path: str) -> bool:
        """Check if the path requires Origin validation."""
        return any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES)

    def _is_allowed_origin(self, origin: str | None) -> bool:
        """Check if the Origin is in the allowed list."""
        if origin is None:
            return False
        return origin in settings.cors_origins
