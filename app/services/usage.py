"""Usage tracking service for rate limiting and analytics."""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import UsageLog, ToolType

settings = get_settings()


class UsageService:
    """Service for tracking and querying usage statistics."""

    async def log_usage(
        self,
        db: AsyncSession,
        tool: str,
        user_id: UUID | None = None,
        input_size_bytes: int | None = None,
        output_size_bytes: int | None = None,
        file_count: int = 1,
        api_request: bool = False,
        ip_address: str | None = None,
    ) -> UsageLog:
        """
        Log a tool usage event.

        Args:
            db: Database session
            tool: Tool type (compress, merge, image_to_pdf)
            user_id: User ID if authenticated
            input_size_bytes: Input file size
            output_size_bytes: Output file size
            file_count: Number of files processed
            api_request: Whether this was an API request
            ip_address: Client IP address

        Returns:
            Created UsageLog record
        """
        log = UsageLog(
            user_id=user_id,
            tool=tool,
            input_size_bytes=input_size_bytes,
            output_size_bytes=output_size_bytes,
            file_count=file_count,
            api_request=api_request,
            ip_address=ip_address,
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    async def get_daily_usage_count(
        self,
        db: AsyncSession,
        tool: str,
        user_id: UUID | None = None,
        ip_address: str | None = None,
    ) -> int:
        """
        Get usage count for today.

        Args:
            db: Database session
            tool: Tool type to count
            user_id: User ID (for authenticated users)
            ip_address: IP address (for anonymous users)

        Returns:
            Number of uses today
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        query = select(func.count(UsageLog.id)).where(
            UsageLog.tool == tool,
            UsageLog.created_at >= today_start,
        )

        # Filter by user or IP
        if user_id:
            query = query.where(UsageLog.user_id == user_id)
        elif ip_address:
            query = query.where(UsageLog.ip_address == ip_address)
        else:
            return 0

        result = await db.execute(query)
        return result.scalar() or 0

    async def check_rate_limit(
        self,
        db: AsyncSession,
        tool: str,
        user_id: UUID | None = None,
        ip_address: str | None = None,
        is_pro: bool = False,
    ) -> tuple[bool, int, int]:
        """
        Check if user has exceeded rate limit.

        Args:
            db: Database session
            tool: Tool type
            user_id: User ID (for authenticated users)
            ip_address: IP address (for anonymous users)
            is_pro: Whether user has Pro subscription

        Returns:
            Tuple of (allowed, current_count, limit)
        """
        # Pro users have no limits
        if is_pro:
            return True, 0, 0

        # Get limit for tool
        limits = {
            ToolType.COMPRESS: settings.rate_limit_compress_free,
            ToolType.MERGE: settings.rate_limit_merge_free,
            ToolType.IMAGE_TO_PDF: settings.rate_limit_image_to_pdf_free,
            "compress": settings.rate_limit_compress_free,
            "merge": settings.rate_limit_merge_free,
            "image_to_pdf": settings.rate_limit_image_to_pdf_free,
        }
        limit = limits.get(tool, 2)

        # Get current usage
        current = await self.get_daily_usage_count(
            db=db,
            tool=tool,
            user_id=user_id,
            ip_address=ip_address,
        )

        return current < limit, current, limit

    async def get_user_stats(
        self,
        db: AsyncSession,
        user_id: UUID,
        days: int = 30,
    ) -> dict:
        """
        Get usage statistics for a user.

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to include

        Returns:
            Dictionary with usage statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Total counts by tool
        query = select(
            UsageLog.tool,
            func.count(UsageLog.id).label("count"),
            func.sum(UsageLog.input_size_bytes).label("input_bytes"),
            func.sum(UsageLog.output_size_bytes).label("output_bytes"),
        ).where(
            UsageLog.user_id == user_id,
            UsageLog.created_at >= start_date,
        ).group_by(UsageLog.tool)

        result = await db.execute(query)
        rows = result.all()

        stats = {
            "period_days": days,
            "total_operations": 0,
            "total_input_bytes": 0,
            "total_output_bytes": 0,
            "by_tool": {},
        }

        for row in rows:
            stats["by_tool"][row.tool] = {
                "count": row.count,
                "input_bytes": row.input_bytes or 0,
                "output_bytes": row.output_bytes or 0,
            }
            stats["total_operations"] += row.count
            stats["total_input_bytes"] += row.input_bytes or 0
            stats["total_output_bytes"] += row.output_bytes or 0

        return stats

    async def get_today_remaining(
        self,
        db: AsyncSession,
        user_id: UUID | None = None,
        ip_address: str | None = None,
        is_pro: bool = False,
    ) -> dict:
        """
        Get remaining usage for today.

        Args:
            db: Database session
            user_id: User ID
            ip_address: IP address
            is_pro: Whether user has Pro subscription

        Returns:
            Dictionary with remaining counts per tool
        """
        if is_pro:
            return {
                "compress": {"used": 0, "limit": -1, "remaining": -1},
                "merge": {"used": 0, "limit": -1, "remaining": -1},
                "image_to_pdf": {"used": 0, "limit": -1, "remaining": -1},
            }

        result = {}
        tools = [
            ("compress", settings.rate_limit_compress_free),
            ("merge", settings.rate_limit_merge_free),
            ("image_to_pdf", settings.rate_limit_image_to_pdf_free),
        ]

        for tool, limit in tools:
            used = await self.get_daily_usage_count(
                db=db,
                tool=tool,
                user_id=user_id,
                ip_address=ip_address,
            )
            result[tool] = {
                "used": used,
                "limit": limit,
                "remaining": max(0, limit - used),
            }

        return result


# Global instance
usage_service = UsageService()


def get_usage_service() -> UsageService:
    """Dependency for getting usage service instance."""
    return usage_service
