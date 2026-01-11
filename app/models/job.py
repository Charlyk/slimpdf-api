import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class JobStatus(str, Enum):
    """Job processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ToolType(str, Enum):
    """Available PDF tools."""

    COMPRESS = "compress"
    MERGE = "merge"
    IMAGE_TO_PDF = "image_to_pdf"


class Job(Base):
    """Job model for tracking file processing tasks."""

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    tool: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        Text, default=JobStatus.PENDING, server_default="pending"
    )
    input_filename: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_filename: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    output_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    @property
    def is_expired(self) -> bool:
        """Check if job download has expired."""
        return datetime.utcnow() > self.expires_at.replace(tzinfo=None)

    @property
    def reduction_percent(self) -> float | None:
        """Calculate compression reduction percentage."""
        if self.original_size and self.output_size:
            return round((1 - self.output_size / self.original_size) * 100, 1)
        return None
