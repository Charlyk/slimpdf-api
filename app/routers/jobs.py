"""Jobs router for status and download endpoints."""

from datetime import datetime
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.exceptions import http_not_found_error
from app.models import Job, JobStatus

router = APIRouter(prefix="/v1", tags=["jobs"])
settings = get_settings()


class JobStatusResponse(BaseModel):
    """Response for job status endpoint."""

    job_id: str = Field(..., description="Unique job identifier", example="550e8400-e29b-41d4-a716-446655440000")
    status: str = Field(..., description="Job status (pending, processing, completed, failed)", example="completed")
    tool: str = Field(..., description="Tool used (compress, merge, image_to_pdf)", example="compress")
    original_size: int | None = Field(None, description="Original file size in bytes", example=5242880)
    output_size: int | None = Field(None, description="Output file size in bytes", example=1048576)
    reduction_percent: float | None = Field(None, description="Size reduction percentage (for compression)", example=80.0)
    download_url: str | None = Field(None, description="URL to download processed file", example="/v1/download/550e8400-e29b-41d4-a716-446655440000")
    expires_at: datetime | None = Field(None, description="When the download link expires")
    error_message: str | None = Field(None, description="Error message if job failed")
    created_at: datetime = Field(..., description="When the job was created")
    completed_at: datetime | None = Field(None, description="When the job completed")


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> JobStatusResponse:
    """
    Get the status of a processing job.

    Returns the current status, and when completed, includes
    download URL and file statistics.
    """
    try:
        job_uuid = UUID(job_id)
    except ValueError:
        raise http_not_found_error(f"Job {job_id} not found")

    job = await db.get(Job, job_uuid)
    if not job:
        raise http_not_found_error(f"Job {job_id} not found")

    # Build response
    response = JobStatusResponse(
        job_id=str(job.id),
        status=job.status,
        tool=job.tool,
        original_size=job.original_size,
        output_size=job.output_size,
        reduction_percent=job.reduction_percent,
        expires_at=job.expires_at,
        error_message=job.error_message,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )

    # Add download URL if completed and not expired
    if job.status == JobStatus.COMPLETED.value and not job.is_expired:
        response.download_url = f"/v1/download/{job_id}"

    return response


@router.get("/download/{job_id}")
async def download_file(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """
    Download the processed file.

    Returns the processed PDF file if the job is completed
    and the download link hasn't expired.
    """
    try:
        job_uuid = UUID(job_id)
    except ValueError:
        raise http_not_found_error(f"Job {job_id} not found")

    job = await db.get(Job, job_uuid)
    if not job:
        raise http_not_found_error(f"Job {job_id} not found")

    # Check job status
    if job.status == JobStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Job is still pending. Please wait.",
        )

    if job.status == JobStatus.PROCESSING.value:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Job is still processing. Please wait.",
        )

    if job.status == JobStatus.FAILED.value:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job failed: {job.error_message or 'Unknown error'}",
        )

    # Check expiry
    if job.is_expired:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Download link has expired.",
        )

    # Check file exists
    if not job.file_path:
        raise http_not_found_error("Output file not found")

    file_path = Path(job.file_path)
    if not file_path.exists():
        raise http_not_found_error("Output file not found")

    # Determine filename for download
    if job.input_filename:
        # Use original filename with suffix
        base_name = Path(job.input_filename).stem
        download_filename = f"{base_name}_{job.tool}.pdf"
    else:
        download_filename = f"{job.tool}_{job_id[:8]}.pdf"

    return FileResponse(
        path=file_path,
        filename=download_filename,
        media_type="application/pdf",
    )
