"""Language detection middleware for i18n support."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.i18n.translations import (
    set_language,
    DEFAULT_LANGUAGE,
    TRANSLATIONS,
    SupportedLanguage,
)


def parse_accept_language(header: str | None) -> SupportedLanguage:
    """
    Parse the Accept-Language header and return the best matching language.

    Supports formats like:
    - "en"
    - "en-US"
    - "en-US,en;q=0.9,es;q=0.8"

    Returns the first supported language found, or the default language.
    """
    if not header:
        return DEFAULT_LANGUAGE

    # Parse language preferences with quality values
    languages = []
    for part in header.split(","):
        part = part.strip()
        if not part:
            continue

        # Handle quality value (e.g., "en;q=0.9")
        if ";q=" in part:
            lang, q = part.split(";q=")
            try:
                quality = float(q)
            except ValueError:
                quality = 0.0
        else:
            lang = part
            quality = 1.0

        # Normalize language code (e.g., "en-US" -> "en")
        lang = lang.strip().split("-")[0].lower()
        languages.append((lang, quality))

    # Sort by quality (highest first)
    languages.sort(key=lambda x: x[1], reverse=True)

    # Find first supported language
    for lang, _ in languages:
        if lang in TRANSLATIONS:
            return lang  # type: ignore

    return DEFAULT_LANGUAGE


class LanguageMiddleware(BaseHTTPMiddleware):
    """
    Middleware to detect and set the request language.

    Language detection priority:
    1. X-Language header (explicit override)
    2. Accept-Language header (browser preference)
    3. Default language (English)

    The detected language is stored in the request state and context var
    for use by downstream handlers.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Check for explicit language header first
        language = request.headers.get("X-Language")

        if not language:
            # Fall back to Accept-Language header
            language = parse_accept_language(
                request.headers.get("Accept-Language")
            )
        else:
            # Normalize and validate explicit language
            language = language.split("-")[0].lower()
            if language not in TRANSLATIONS:
                language = DEFAULT_LANGUAGE

        # Set language in context var (thread-safe)
        set_language(language)  # type: ignore

        # Also store in request state for easy access
        request.state.language = language

        response = await call_next(request)

        # Add Content-Language header to response
        response.headers["Content-Language"] = language

        return response
