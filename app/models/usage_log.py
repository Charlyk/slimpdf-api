import uuid
from datetime import datetime

from sqlalchemy import Text, DateTime, ForeignKey, BigInteger, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UsageLog(Base):
    """Usage log model for tracking tool usage and rate limiting."""

    __tablename__ = "usage_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    tool: Mapped[str] = mapped_column(Text, nullable=False)  # compress, merge, image_to_pdf
    input_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    output_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    file_count: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    api_request: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    ip_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
