"""Message keys for internationalization."""


class Messages:
    """Constants for all translatable message keys."""

    # File validation errors
    FILE_SIZE_EXCEEDED = "file_size_exceeded"
    FILE_TYPE_INVALID = "file_type_invalid"
    FILE_COUNT_EXCEEDED = "file_count_exceeded"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # Authentication errors
    AUTH_REQUIRED = "auth_required"
    AUTH_INVALID_TOKEN = "auth_invalid_token"
    AUTH_TOKEN_EXPIRED = "auth_token_expired"
    AUTH_INVALID_USER_ID = "auth_invalid_user_id"
    AUTH_USE_API_KEY_ENDPOINT = "auth_use_api_key_endpoint"
    AUTH_PRO_REQUIRED = "auth_pro_required"

    # API key errors
    API_KEY_INVALID = "api_key_invalid"
    API_KEY_REVOKED = "api_key_revoked"
    API_KEY_REQUIRED = "api_key_required"
    API_KEY_INVALID_FORMAT = "api_key_invalid_format"
    API_KEY_USER_NOT_FOUND = "api_key_user_not_found"
    API_KEY_PRO_REQUIRED = "api_key_pro_required"
    API_KEY_MAX_LIMIT = "api_key_max_limit"
    API_KEY_STORE_WARNING = "api_key_store_warning"
    API_KEY_NOT_FOUND = "api_key_not_found"
    API_KEY_REVOKED_SUCCESS = "api_key_revoked_success"
    API_KEY_INVALID_ID = "api_key_invalid_id"

    # Job errors
    JOB_NOT_FOUND = "job_not_found"
    JOB_EXPIRED = "job_expired"
    JOB_PENDING = "job_pending"
    JOB_PROCESSING = "job_processing"
    JOB_FAILED = "job_failed"
    JOB_FILE_NOT_FOUND = "job_file_not_found"

    # Success messages
    COMPRESS_STARTED = "compress_started"
    MERGE_STARTED = "merge_started"
    IMAGE_TO_PDF_STARTED = "image_to_pdf_started"

    # Billing errors
    BILLING_ALREADY_PRO = "billing_already_pro"
    BILLING_USER_NOT_FOUND = "billing_user_not_found"
    BILLING_STRIPE_NOT_CONFIGURED = "billing_stripe_not_configured"
    BILLING_NO_ACCOUNT = "billing_no_account"
    BILLING_MISSING_SIGNATURE = "billing_missing_signature"
    BILLING_INVALID_SIGNATURE = "billing_invalid_signature"

    # Origin validation
    ORIGIN_FORBIDDEN = "origin_forbidden"
