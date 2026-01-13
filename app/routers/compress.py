"""Compress PDF router."""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, BackgroundTasks, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.exceptions import (
    FileSizeLimitError,
    http_file_size_limit_error,
    http_file_processing_error,
    http_invalid_file_type_error,
)
from app.models import Job, JobStatus, ToolType
from app.services.compression import (
    CompressionQuality,
    CompressionService,
    get_compression_service,
)
from app.services.file_manager import FileManager, get_file_manager
from app.middleware.rate_limit import CompressRateLimit, set_rate_limit_headers
from app.services.usage import UsageService, get_usage_service
from app.i18n import get_translator, Messages

router = APIRouter(prefix="/v1", tags=["compress"])
settings = get_settings()


class CompressResponse(BaseModel):
    """Response for compress endpoint."""

    job_id: str = Field(..., description="Unique job identifier", example="550e8400-e29b-41d4-a716-446655440000")
    status: str = Field(..., description="Job status", example="pending")
    message: str = Field(..., description="Status message", example="File uploaded. Processing started.")


class CompressStatusResponse(BaseModel):
    """Response for compression job status."""

    job_id: str = Field(..., description="Unique job identifier", example="550e8400-e29b-41d4-a716-446655440000")
    status: str = Field(..., description="Job status (pending, processing, completed, failed)", example="completed")
    original_size: int | None = Field(None, description="Original file size in bytes", example=5242880)
    compressed_size: int | None = Field(None, description="Compressed file size in bytes", example=1048576)
    reduction_percent: float | None = Field(None, description="Size reduction percentage", example=80.0)
    download_url: str | None = Field(None, description="URL to download the compressed file", example="/v1/download/550e8400-e29b-41d4-a716-446655440000")
    expires_at: datetime | None = Field(None, description="When the download link expires")
    error_message: str | None = Field(None, description="Error message if job failed")


async def process_compression(
    job_id: UUID,
    input_path: str,
    output_path: str,
    quality: str,
    target_size_mb: float | None,
    db: AsyncSession,
    compression_service: CompressionService,
    file_manager: FileManager,
) -> None:
    """Background task to process PDF compression."""
    from pathlib import Path

    job = await db.get(Job, job_id)
    if not job:
        return

    try:
        # Update status to processing
        job.status = JobStatus.PROCESSING
        await db.commit()

        input_file = Path(input_path)
        output_file = Path(output_path)

        # Perform compression
        if target_size_mb:
            result = await compression_service.compress_to_target_size(
                input_path=input_file,
                output_path=output_file,
                target_size_mb=target_size_mb,
            )
        else:
            result = await compression_service.compress(
                input_path=input_file,
                output_path=output_file,
                quality=quality,
            )

        # Update job with results
        job.status = JobStatus.COMPLETED
        job.output_filename = output_file.name
        job.file_path = str(output_file)
        job.original_size = result.original_size
        job.output_size = result.compressed_size
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()

    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        await db.commit()

    finally:
        # Clean up input file
        file_manager.delete_file(Path(input_path))


@router.post("/compress", status_code=status.HTTP_202_ACCEPTED, response_model=CompressResponse)
async def compress_pdf(
    response: Response,
    background_tasks: BackgroundTasks,
    rate_limit: CompressRateLimit,
    file: Annotated[UploadFile, File(description="PDF file to compress")],
    quality: Annotated[
        str,
        Form(description="Compression quality: low, medium, high, maximum"),
    ] = "medium",
    target_size_mb: Annotated[
        float | None,
        Form(description="Target file size in MB (Pro only)"),
    ] = None,
    db: AsyncSession = Depends(get_db),
    compression_service: CompressionService = Depends(get_compression_service),
    file_manager: FileManager = Depends(get_file_manager),
    usage_service: UsageService = Depends(get_usage_service),
) -> CompressResponse:
    """
    Compress a PDF file.

    Upload a PDF and receive a job ID. Use the job ID to check status
    and download the compressed file when ready.

    **Authentication:**
    - No API key: Free tier limits apply (rate limited)
    - With API key: Pro tier limits (unlimited)

    **Quality presets:**
    - `low`: 72 DPI - smallest file size
    - `medium`: 150 DPI - balanced (default)
    - `high`: 300 DPI - better quality
    - `maximum`: 300 DPI with color preservation

    **Target size (Pro only):**
    Set `target_size_mb` to compress to a specific file size.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise http_invalid_file_type_error("PDF", file.filename or "unknown")

    # Validate quality
    try:
        quality_enum = CompressionQuality(quality.lower())
    except ValueError:
        quality_enum = CompressionQuality.MEDIUM

    # Get tier limits from rate limiter
    is_pro = rate_limit["is_pro"]
    max_size_mb = settings.max_file_size_pro_mb if is_pro else settings.max_file_size_free_mb

    # Save uploaded file with size limit enforced during upload
    try:
        input_path = await file_manager.save_upload(file, max_size_mb=max_size_mb)
    except FileSizeLimitError as e:
        raise http_file_size_limit_error(e.max_size_mb, e.actual_size_mb)

    # Log usage for rate limiting (must happen after rate check passes)
    await usage_service.log_usage(
        db=db,
        tool="compress",
        user_id=rate_limit["user_id"],
        ip_address=rate_limit["ip_address"],
        input_size_bytes=file_manager.get_file_size(input_path),
    )

    # Create output path
    output_path = file_manager.create_output_path(file.filename)

    # Create job record
    job = Job(
        tool=ToolType.COMPRESS,
        status=JobStatus.PENDING,
        input_filename=file.filename,
        original_size=file_manager.get_file_size(input_path),
        expires_at=file_manager.get_expiry_time(is_pro),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Queue background processing
    background_tasks.add_task(
        process_compression,
        job.id,
        str(input_path),
        str(output_path),
        quality_enum.value,
        target_size_mb,
        db,
        compression_service,
        file_manager,
    )

    set_rate_limit_headers(response, rate_limit)

    t = get_translator()
    return CompressResponse(
        job_id=str(job.id),
        status="pending",
        message=t(Messages.COMPRESS_STARTED),
    )
