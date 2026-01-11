"""Custom exceptions for SlimPDF API."""

from fastapi import HTTPException, status


class SlimPDFException(Exception):
    """Base exception for SlimPDF."""

    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class FileProcessingError(SlimPDFException):
    """Raised when file processing fails (Ghostscript, PyMuPDF, etc.)."""

    pass


class FileSizeLimitError(SlimPDFException):
    """Raised when file exceeds size limit for user's tier."""

    def __init__(self, max_size_mb: int, actual_size_mb: float):
        self.max_size_mb = max_size_mb
        self.actual_size_mb = actual_size_mb
        super().__init__(
            f"File size {actual_size_mb:.1f}MB exceeds limit of {max_size_mb}MB"
        )


class RateLimitError(SlimPDFException):
    """Raised when user exceeds daily usage limit."""

    def __init__(self, tool: str, limit: int):
        self.tool = tool
        self.limit = limit
        super().__init__(
            f"Daily limit of {limit} {tool} operations reached. Upgrade to Pro for unlimited access."
        )


class AuthenticationError(SlimPDFException):
    """Raised when authentication fails."""

    pass


class InvalidApiKeyError(AuthenticationError):
    """Raised when API key is invalid or revoked."""

    def __init__(self):
        super().__init__("Invalid or revoked API key")


class ExpiredTokenError(AuthenticationError):
    """Raised when JWT token has expired."""

    def __init__(self):
        super().__init__("Token has expired")


class JobNotFoundError(SlimPDFException):
    """Raised when job ID is not found."""

    def __init__(self, job_id: str):
        self.job_id = job_id
        super().__init__(f"Job {job_id} not found")


class JobExpiredError(SlimPDFException):
    """Raised when job download has expired."""

    def __init__(self, job_id: str):
        self.job_id = job_id
        super().__init__(f"Download link for job {job_id} has expired")


class InvalidFileTypeError(SlimPDFException):
    """Raised when uploaded file type is not supported."""

    def __init__(self, expected: str, actual: str):
        self.expected = expected
        self.actual = actual
        super().__init__(f"Expected {expected} file, got {actual}")


class FileCountLimitError(SlimPDFException):
    """Raised when too many files are uploaded for user's tier."""

    def __init__(self, max_count: int, actual_count: int):
        self.max_count = max_count
        self.actual_count = actual_count
        super().__init__(
            f"Too many files ({actual_count}). Maximum allowed: {max_count}"
        )


# HTTP Exception helpers for FastAPI
def http_file_processing_error(detail: str) -> HTTPException:
    """Create HTTP 500 exception for file processing errors."""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail,
    )


def http_file_size_limit_error(max_size_mb: int, actual_size_mb: float) -> HTTPException:
    """Create HTTP 413 exception for file size limit errors."""
    return HTTPException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail=f"File size {actual_size_mb:.1f}MB exceeds limit of {max_size_mb}MB",
    )


def http_rate_limit_error(tool: str, limit: int) -> HTTPException:
    """Create HTTP 429 exception for rate limit errors."""
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=f"Daily limit of {limit} {tool} operations reached. Upgrade to Pro for unlimited access.",
    )


def http_authentication_error(detail: str = "Authentication required") -> HTTPException:
    """Create HTTP 401 exception for authentication errors."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def http_not_found_error(detail: str) -> HTTPException:
    """Create HTTP 404 exception for not found errors."""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


def http_invalid_file_type_error(expected: str, actual: str) -> HTTPException:
    """Create HTTP 400 exception for invalid file type errors."""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Expected {expected} file, got {actual}",
    )
