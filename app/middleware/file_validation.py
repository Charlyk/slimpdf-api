"""File validation middleware and dependencies."""

from typing import Annotated

from fastapi import Depends, UploadFile

from app.config import get_settings
from app.exceptions import (
    http_file_size_limit_error,
    http_invalid_file_type_error,
    FileCountLimitError,
)

settings = get_settings()


# Supported file types
PDF_EXTENSIONS = {".pdf"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp", ".gif"}
PDF_MIME_TYPES = {"application/pdf"}
IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/tiff",
    "image/bmp",
    "image/gif",
}


def validate_pdf_file(file: UploadFile, max_size_mb: float) -> None:
    """
    Validate that a file is a valid PDF within size limits.

    Args:
        file: Uploaded file
        max_size_mb: Maximum allowed size in MB

    Raises:
        HTTPException: If validation fails
    """
    # Check filename extension
    if not file.filename:
        raise http_invalid_file_type_error("PDF", "no filename")

    ext = file.filename.lower().split(".")[-1] if "." in file.filename else ""
    if f".{ext}" not in PDF_EXTENSIONS:
        raise http_invalid_file_type_error("PDF", f".{ext}")

    # Check content type if available
    if file.content_type and file.content_type not in PDF_MIME_TYPES:
        # Allow application/octet-stream as browsers sometimes use it
        if file.content_type != "application/octet-stream":
            raise http_invalid_file_type_error("PDF", file.content_type)

    # Note: File size is checked after saving since UploadFile.size
    # may not be reliable before reading


def validate_image_file(file: UploadFile, max_size_mb: float) -> None:
    """
    Validate that a file is a valid image within size limits.

    Args:
        file: Uploaded file
        max_size_mb: Maximum allowed size in MB

    Raises:
        HTTPException: If validation fails
    """
    if not file.filename:
        raise http_invalid_file_type_error("image", "no filename")

    ext = file.filename.lower().split(".")[-1] if "." in file.filename else ""
    if f".{ext}" not in IMAGE_EXTENSIONS:
        raise http_invalid_file_type_error(
            "JPG, PNG, WebP, TIFF, BMP, or GIF",
            f".{ext}",
        )


class FileSizeValidator:
    """Dependency for validating file sizes based on user tier."""

    def __init__(self, file_type: str = "pdf"):
        """
        Initialize validator.

        Args:
            file_type: Type of file to validate ("pdf" or "image")
        """
        self.file_type = file_type

    def get_max_size_mb(self, is_pro: bool) -> float:
        """Get maximum file size for user tier."""
        if self.file_type == "image":
            return 20 if is_pro else 5
        return settings.max_file_size_pro_mb if is_pro else settings.max_file_size_free_mb

    def get_max_file_count(self, is_pro: bool, tool: str) -> int:
        """Get maximum file count for user tier and tool."""
        if tool == "merge":
            return settings.max_files_merge_pro if is_pro else settings.max_files_merge_free
        if tool == "image_to_pdf":
            return settings.max_images_pro if is_pro else settings.max_images_free
        return 1

    def validate_single(self, file: UploadFile, is_pro: bool = False) -> None:
        """Validate a single file."""
        max_size = self.get_max_size_mb(is_pro)

        if self.file_type == "pdf":
            validate_pdf_file(file, max_size)
        else:
            validate_image_file(file, max_size)

    def validate_multiple(
        self,
        files: list[UploadFile],
        tool: str,
        is_pro: bool = False,
    ) -> None:
        """Validate multiple files."""
        max_count = self.get_max_file_count(is_pro, tool)

        if len(files) > max_count:
            raise FileCountLimitError(max_count, len(files))

        for file in files:
            self.validate_single(file, is_pro)


# Pre-configured validators
pdf_validator = FileSizeValidator("pdf")
image_validator = FileSizeValidator("image")


def get_pdf_validator() -> FileSizeValidator:
    """Dependency for PDF validation."""
    return pdf_validator


def get_image_validator() -> FileSizeValidator:
    """Dependency for image validation."""
    return image_validator


# Type aliases
PdfValidator = Annotated[FileSizeValidator, Depends(get_pdf_validator)]
ImageValidator = Annotated[FileSizeValidator, Depends(get_image_validator)]
