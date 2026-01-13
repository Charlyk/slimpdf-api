"""Middleware for SlimPDF API."""

from app.middleware.rate_limit import (
    RateLimitChecker,
    get_client_ip,
    compress_rate_limit,
    merge_rate_limit,
    image_to_pdf_rate_limit,
    CompressRateLimit,
    MergeRateLimit,
    ImageToPdfRateLimit,
    set_rate_limit_headers,
)
from app.middleware.file_validation import (
    FileSizeValidator,
    pdf_validator,
    image_validator,
    get_pdf_validator,
    get_image_validator,
    PdfValidator,
    ImageValidator,
    validate_pdf_file,
    validate_image_file,
)
from app.middleware.auth import (
    TokenPayload,
    CurrentUser,
    create_access_token,
    decode_token,
    get_current_user_optional,
    get_current_user,
    get_current_pro_user,
    OptionalUser,
    RequiredUser,
    ProUser,
)
from app.middleware.api_key import (
    generate_api_key,
    verify_api_key,
    get_api_key_user,
    get_api_key_user_required,
    create_api_key_for_user,
    revoke_api_key,
    ApiKeyUser,
    OptionalApiKeyUser,
)

__all__ = [
    # Rate limiting
    "RateLimitChecker",
    "get_client_ip",
    "compress_rate_limit",
    "merge_rate_limit",
    "image_to_pdf_rate_limit",
    "CompressRateLimit",
    "MergeRateLimit",
    "ImageToPdfRateLimit",
    "set_rate_limit_headers",
    # File validation
    "FileSizeValidator",
    "pdf_validator",
    "image_validator",
    "get_pdf_validator",
    "get_image_validator",
    "PdfValidator",
    "ImageValidator",
    "validate_pdf_file",
    "validate_image_file",
    # JWT Auth
    "TokenPayload",
    "CurrentUser",
    "create_access_token",
    "decode_token",
    "get_current_user_optional",
    "get_current_user",
    "get_current_pro_user",
    "OptionalUser",
    "RequiredUser",
    "ProUser",
    # API Key Auth
    "generate_api_key",
    "verify_api_key",
    "get_api_key_user",
    "get_api_key_user_required",
    "create_api_key_for_user",
    "revoke_api_key",
    "ApiKeyUser",
    "OptionalApiKeyUser",
]
