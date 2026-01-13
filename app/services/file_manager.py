"""File management service for handling temporary file storage."""

import os
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.config import get_settings
from app.exceptions import FileSizeLimitError

settings = get_settings()


class FileManager:
    """Manages temporary file storage for PDF processing."""

    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or settings.temp_file_dir)
        self._directories_initialized = False

    def _ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        if self._directories_initialized:
            return
        (self.base_dir / "uploads").mkdir(parents=True, exist_ok=True)
        (self.base_dir / "processed").mkdir(parents=True, exist_ok=True)
        self._directories_initialized = True

    def _generate_filename(self, original_filename: str | None = None) -> str:
        """Generate a unique filename with UUID."""
        file_id = str(uuid.uuid4())
        if original_filename:
            ext = Path(original_filename).suffix.lower()
            return f"{file_id}{ext}"
        return file_id

    @property
    def uploads_dir(self) -> Path:
        """Get the uploads directory path."""
        self._ensure_directories()
        return self.base_dir / "uploads"

    @property
    def processed_dir(self) -> Path:
        """Get the processed files directory path."""
        self._ensure_directories()
        return self.base_dir / "processed"

    async def save_upload(self, file: UploadFile, max_size_mb: float | None = None) -> Path:
        """
        Save an uploaded file to the uploads directory with optional size limit.

        Streams the file in chunks and enforces the size limit during upload,
        preventing large files from being fully written to disk.

        Args:
            file: FastAPI UploadFile object
            max_size_mb: Maximum allowed file size in MB. If None, no limit is enforced.

        Returns:
            Path to the saved file

        Raises:
            FileSizeLimitError: If file exceeds max_size_mb during upload
        """
        filename = self._generate_filename(file.filename)
        file_path = self.uploads_dir / filename

        max_size_bytes = int(max_size_mb * 1024 * 1024) if max_size_mb else None
        total_bytes = 0
        chunk_size = 64 * 1024  # 64KB chunks

        try:
            async with aiofiles.open(file_path, "wb") as f:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break

                    total_bytes += len(chunk)

                    # Check size limit before writing
                    if max_size_bytes and total_bytes > max_size_bytes:
                        raise FileSizeLimitError(
                            max_size_mb=int(max_size_mb),
                            actual_size_mb=total_bytes / (1024 * 1024),
                        )

                    await f.write(chunk)

        except FileSizeLimitError:
            # Clean up partial file
            self.delete_file(file_path)
            raise

        return file_path

    async def save_uploads(
        self, files: list[UploadFile], max_size_mb: float | None = None
    ) -> list[Path]:
        """
        Save multiple uploaded files with optional size limit per file.

        Args:
            files: List of FastAPI UploadFile objects
            max_size_mb: Maximum allowed size per file in MB. If None, no limit.

        Returns:
            List of paths to saved files

        Raises:
            FileSizeLimitError: If any file exceeds max_size_mb. Previously saved
                files from this batch are cleaned up before raising.
        """
        paths = []
        try:
            for file in files:
                path = await self.save_upload(file, max_size_mb)
                paths.append(path)
        except FileSizeLimitError:
            # Clean up all files saved so far
            self.delete_files(paths)
            raise
        return paths

    def create_output_path(self, original_filename: str | None = None, suffix: str = ".pdf") -> Path:
        """
        Create a path for processed output file.

        Args:
            original_filename: Original filename for extension detection
            suffix: File suffix if no original filename

        Returns:
            Path for the output file
        """
        if original_filename:
            ext = Path(original_filename).suffix.lower() or suffix
        else:
            ext = suffix

        filename = f"{uuid.uuid4()}{ext}"
        return self.processed_dir / filename

    def get_file_size(self, file_path: Path) -> int:
        """
        Get file size in bytes.

        Args:
            file_path: Path to the file

        Returns:
            File size in bytes
        """
        return file_path.stat().st_size

    def get_file_size_mb(self, file_path: Path) -> float:
        """
        Get file size in megabytes.

        Args:
            file_path: Path to the file

        Returns:
            File size in MB
        """
        return self.get_file_size(file_path) / (1024 * 1024)

    def delete_file(self, file_path: Path) -> bool:
        """
        Delete a file.

        Args:
            file_path: Path to the file to delete

        Returns:
            True if file was deleted, False if it didn't exist
        """
        try:
            file_path.unlink()
            return True
        except FileNotFoundError:
            return False

    def delete_files(self, file_paths: list[Path]) -> int:
        """
        Delete multiple files.

        Args:
            file_paths: List of paths to delete

        Returns:
            Number of files deleted
        """
        count = 0
        for path in file_paths:
            if self.delete_file(path):
                count += 1
        return count

    def file_exists(self, file_path: Path) -> bool:
        """Check if a file exists."""
        return file_path.exists() and file_path.is_file()

    def cleanup_expired_files(self, max_age_hours: int = 24) -> int:
        """
        Delete files older than max_age_hours.

        Args:
            max_age_hours: Maximum age in hours before deletion

        Returns:
            Number of files deleted
        """
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        deleted = 0

        for directory in [self.uploads_dir, self.processed_dir]:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff:
                        self.delete_file(file_path)
                        deleted += 1

        return deleted

    def get_expiry_time(self, is_pro: bool) -> datetime:
        """
        Get expiry time for a file based on user tier.

        Args:
            is_pro: Whether user has Pro subscription

        Returns:
            Datetime when file should expire
        """
        hours = settings.file_expiry_pro_hours if is_pro else settings.file_expiry_free_hours
        return datetime.now(timezone.utc) + timedelta(hours=hours)


# Global instance
file_manager = FileManager()


def get_file_manager() -> FileManager:
    """Dependency for getting file manager instance."""
    return file_manager
