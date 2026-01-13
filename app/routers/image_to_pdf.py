"""Image to PDF router."""

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
    http_invalid_file_type_error,
    FileCountLimitError,
)
from app.models import Job, JobStatus, ToolType
from app.services.image_convert import (
    ImageConvertService,
    PageSize,
    get_image_convert_service,
)
from app.services.file_manager import FileManager, get_file_manager
from app.middleware.rate_limit import ImageToPdfRateLimit, set_rate_limit_headers
from app.services.usage import UsageService, get_usage_service
from app.i18n import get_translator, Messages

router = APIRouter(prefix="/v1", tags=["image-to-pdf"])
settings = get_settings()


class ImageToPdfResponse(BaseModel):
    """Response for image-to-pdf endpoint."""

    job_id: str = Field(..., description="Unique job identifier", example="550e8400-e29b-41d4-a716-446655440000")
    status: str = Field(..., description="Job status", example="pending")
    message: str = Field(..., description="Status message", example="Images uploaded. Conversion started.")
    image_count: int = Field(..., description="Number of images being converted", example=5)


async def process_image_to_pdf(
    job_id: UUID,
    input_paths: list[str],
    output_path: str,
    page_size: str,
    db: AsyncSession,
    image_service: ImageConvertService,
    file_manager: FileManager,
) -> None:
    """Background task to process image to PDF conversion."""
    from pathlib import Path

    job = await db.get(Job, job_id)
    if not job:
        return

    try:
        # Update status to processing
        job.status = JobStatus.PROCESSING
        await db.commit()

        input_files = [Path(p) for p in input_paths]
        output_file = Path(output_path)

        # Calculate total input size
        total_input_size = sum(f.stat().st_size for f in input_files)

        # Parse page size
        try:
            page_size_enum = PageSize(page_size)
        except ValueError:
            page_size_enum = PageSize.A4

        # Perform conversion
        if len(input_files) == 1:
            result = await image_service.convert_single(
                image_path=input_files[0],
                output_path=output_file,
                page_size=page_size_enum,
            )
        else:
            result = await image_service.convert_multiple(
                image_paths=input_files,
                output_path=output_file,
                page_size=page_size_enum,
            )

        # Update job with results
        job.status = JobStatus.COMPLETED
        job.output_filename = output_file.name
        job.file_path = str(output_file)
        job.original_size = total_input_size
        job.output_size = result.output_size
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()

    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        await db.commit()

    finally:
        # Clean up input files
        for path in input_paths:
            file_manager.delete_file(Path(path))


@router.post("/image-to-pdf", status_code=status.HTTP_202_ACCEPTED, response_model=ImageToPdfResponse)
async def convert_images_to_pdf(
    response: Response,
    background_tasks: BackgroundTasks,
    rate_limit: ImageToPdfRateLimit,
    files: Annotated[
        list[UploadFile],
        File(description="Image files to convert (in order)"),
    ],
    page_size: Annotated[
        str,
        Form(description="Page size: a4, letter, or original"),
    ] = "a4",
    db: AsyncSession = Depends(get_db),
    image_service: ImageConvertService = Depends(get_image_convert_service),
    file_manager: FileManager = Depends(get_file_manager),
    usage_service: UsageService = Depends(get_usage_service),
) -> ImageToPdfResponse:
    """
    Convert images to a PDF document.

    Upload images and receive a job ID. Images are added to the PDF in the
    order they are uploaded. Use the job ID to check status and download
    the PDF when ready.

    **Authentication:**
    - No API key: Free tier limits apply (rate limited)
    - With API key: Pro tier limits (unlimited)

    **Supported formats:** JPG, PNG, WebP, TIFF, BMP, GIF

    **Page sizes:**
    - `a4`: A4 paper size (210mm x 297mm)
    - `letter`: US Letter size (8.5" x 11")
    - `original`: Keep original image dimensions

    **Limits:**
    - Free tier: Up to 10 images, max 5MB each
    - Pro tier: Up to 100 images, max 20MB each
    """
    if not files:
        raise http_invalid_file_type_error("image files", "no files")

    # Get tier limits from rate limiter
    is_pro = rate_limit["is_pro"]
    max_images = settings.max_images_pro if is_pro else settings.max_images_free
    max_size_mb = 20 if is_pro else 5  # Image size limits

    # Check file count
    if len(files) > max_images:
        raise FileCountLimitError(max_images, len(files))

    # Validate all files are images
    for f in files:
        if not f.filename or not image_service.is_supported_format(f.filename):
            raise http_invalid_file_type_error(
                "JPG, PNG, WebP, TIFF, BMP, GIF",
                f.filename or "unknown",
            )

    # Save all uploaded files with size limit enforced during upload
    try:
        input_paths = await file_manager.save_uploads(files, max_size_mb=max_size_mb)
    except FileSizeLimitError as e:
        raise http_file_size_limit_error(e.max_size_mb, e.actual_size_mb)

    total_size = sum(file_manager.get_file_size(p) for p in input_paths)

    # Log usage for rate limiting (must happen after rate check passes)
    await usage_service.log_usage(
        db=db,
        tool="image_to_pdf",
        user_id=rate_limit["user_id"],
        ip_address=rate_limit["ip_address"],
        input_size_bytes=total_size,
        file_count=len(files),
    )

    # Create output path
    output_path = file_manager.create_output_path(suffix=".pdf")

    # Create job record
    job = Job(
        tool=ToolType.IMAGE_TO_PDF,
        status=JobStatus.PENDING,
        input_filename=f"{len(files)} images",
        original_size=total_size,
        expires_at=file_manager.get_expiry_time(is_pro),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Queue background processing
    background_tasks.add_task(
        process_image_to_pdf,
        job.id,
        [str(p) for p in input_paths],
        str(output_path),
        page_size,
        db,
        image_service,
        file_manager,
    )

    set_rate_limit_headers(response, rate_limit)

    t = get_translator()
    return ImageToPdfResponse(
        job_id=str(job.id),
        status="pending",
        message=t(Messages.IMAGE_TO_PDF_STARTED),
        image_count=len(files),
    )
