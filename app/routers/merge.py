"""Merge PDF router."""

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
from app.services.merge import MergeService, get_merge_service
from app.services.file_manager import FileManager, get_file_manager
from app.middleware.rate_limit import MergeRateLimit, set_rate_limit_headers
from app.i18n import get_translator, Messages

router = APIRouter(prefix="/v1", tags=["merge"])
settings = get_settings()


class MergeResponse(BaseModel):
    """Response for merge endpoint."""

    job_id: str = Field(..., description="Unique job identifier", example="550e8400-e29b-41d4-a716-446655440000")
    status: str = Field(..., description="Job status", example="pending")
    message: str = Field(..., description="Status message", example="Files uploaded. Merge processing started.")
    file_count: int = Field(..., description="Number of files being merged", example=3)


async def process_merge(
    job_id: UUID,
    input_paths: list[str],
    output_path: str,
    db: AsyncSession,
    merge_service: MergeService,
    file_manager: FileManager,
) -> None:
    """Background task to process PDF merge."""
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

        # Perform merge
        result = await merge_service.merge(
            input_paths=input_files,
            output_path=output_file,
            preserve_bookmarks=True,
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


@router.post("/merge", status_code=status.HTTP_202_ACCEPTED, response_model=MergeResponse)
async def merge_pdfs(
    response: Response,
    background_tasks: BackgroundTasks,
    rate_limit: MergeRateLimit,
    files: Annotated[
        list[UploadFile],
        File(description="PDF files to merge (in order)"),
    ],
    db: AsyncSession = Depends(get_db),
    merge_service: MergeService = Depends(get_merge_service),
    file_manager: FileManager = Depends(get_file_manager),
) -> MergeResponse:
    """
    Merge multiple PDF files into one.

    Upload multiple PDFs and receive a job ID. Files are merged in the
    order they are uploaded. Use the job ID to check status and download
    the merged file when ready.

    **Authentication:**
    - No API key: Free tier limits apply (rate limited)
    - With API key: Pro tier limits (unlimited)

    **Limits:**
    - Free tier: Up to 5 PDFs, max 20MB each
    - Pro tier: Up to 50 PDFs, max 100MB each
    """
    if not files:
        raise http_invalid_file_type_error("PDF files", "no files")

    # Get tier limits from rate limiter
    is_pro = rate_limit["is_pro"]
    max_files = settings.max_files_merge_pro if is_pro else settings.max_files_merge_free
    max_size_mb = settings.max_file_size_pro_mb if is_pro else settings.max_file_size_free_mb

    # Check file count
    if len(files) > max_files:
        raise FileCountLimitError(max_files, len(files))

    # Validate all files are PDFs
    for f in files:
        if not f.filename or not f.filename.lower().endswith(".pdf"):
            raise http_invalid_file_type_error("PDF", f.filename or "unknown")

    # Save all uploaded files with size limit enforced during upload
    try:
        input_paths = await file_manager.save_uploads(files, max_size_mb=max_size_mb)
    except FileSizeLimitError as e:
        raise http_file_size_limit_error(e.max_size_mb, e.actual_size_mb)

    total_size = sum(file_manager.get_file_size(p) for p in input_paths)

    # Create output path
    output_path = file_manager.create_output_path(suffix=".pdf")

    # Create job record
    job = Job(
        tool=ToolType.MERGE,
        status=JobStatus.PENDING,
        input_filename=f"{len(files)} files",
        original_size=total_size,
        expires_at=file_manager.get_expiry_time(is_pro),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Queue background processing
    background_tasks.add_task(
        process_merge,
        job.id,
        [str(p) for p in input_paths],
        str(output_path),
        db,
        merge_service,
        file_manager,
    )

    set_rate_limit_headers(response, rate_limit)

    t = get_translator()
    return MergeResponse(
        job_id=str(job.id),
        status="pending",
        message=t(Messages.MERGE_STARTED),
        file_count=len(files),
    )
