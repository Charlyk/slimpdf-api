"""PDF compression service using Ghostscript."""

import asyncio
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from app.exceptions import FileProcessingError


class CompressionQuality(str, Enum):
    """Compression quality presets mapping to Ghostscript settings."""

    LOW = "screen"      # 72 dpi - smallest file size
    MEDIUM = "ebook"    # 150 dpi - balanced
    HIGH = "printer"    # 300 dpi - high quality
    MAXIMUM = "prepress"  # 300 dpi, color preserving


# DPI values for each quality level
QUALITY_DPI = {
    CompressionQuality.LOW: 72,
    CompressionQuality.MEDIUM: 150,
    CompressionQuality.HIGH: 300,
    CompressionQuality.MAXIMUM: 300,
}


@dataclass
class CompressionResult:
    """Result of a PDF compression operation."""

    output_path: Path
    original_size: int
    compressed_size: int
    quality: str
    dpi: int

    @property
    def reduction_percent(self) -> float:
        """Calculate compression reduction percentage."""
        if self.original_size == 0:
            return 0.0
        return round((1 - self.compressed_size / self.original_size) * 100, 1)

    @property
    def compression_ratio(self) -> float:
        """Calculate compression ratio."""
        if self.compressed_size == 0:
            return 0.0
        return round(self.original_size / self.compressed_size, 2)


class CompressionService:
    """Service for compressing PDFs using Ghostscript."""

    def __init__(self, gs_command: str | None = None):
        """
        Initialize compression service.

        Args:
            gs_command: Optional Ghostscript command. If None, will be found lazily.
        """
        self._gs_command = gs_command

    @property
    def gs_command(self) -> str:
        """Get Ghostscript command, finding it lazily if needed."""
        if self._gs_command is None:
            self._gs_command = self._find_ghostscript()
        return self._gs_command

    def _find_ghostscript(self) -> str:
        """Find the Ghostscript executable."""
        # Try common Ghostscript command names
        for cmd in ["gs", "gswin64c", "gswin32c"]:
            try:
                subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    check=True,
                )
                return cmd
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        raise FileProcessingError("Ghostscript not found. Please install Ghostscript.")

    def _build_gs_command(
        self,
        input_path: Path,
        output_path: Path,
        quality: CompressionQuality | str,
        custom_dpi: int | None = None,
    ) -> list[str]:
        """Build Ghostscript command with appropriate settings."""
        # Get quality setting
        if isinstance(quality, str):
            quality = CompressionQuality(quality)

        pdf_setting = f"/{quality.value}"
        dpi = custom_dpi or QUALITY_DPI.get(quality, 150)

        cmd = [
            self.gs_command,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={pdf_setting}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            # Image downsampling settings
            "-dDownsampleColorImages=true",
            "-dDownsampleGrayImages=true",
            "-dDownsampleMonoImages=true",
            f"-dColorImageResolution={dpi}",
            f"-dGrayImageResolution={dpi}",
            f"-dMonoImageResolution={dpi}",
            # Output
            f"-sOutputFile={output_path}",
            str(input_path),
        ]
        return cmd

    async def compress(
        self,
        input_path: Path,
        output_path: Path,
        quality: CompressionQuality | str = CompressionQuality.MEDIUM,
        custom_dpi: int | None = None,
    ) -> CompressionResult:
        """
        Compress a PDF file using Ghostscript.

        Args:
            input_path: Path to input PDF
            output_path: Path for compressed output
            quality: Compression quality preset
            custom_dpi: Optional custom DPI override

        Returns:
            CompressionResult with output path and statistics

        Raises:
            FileProcessingError: If compression fails
        """
        if not input_path.exists():
            raise FileProcessingError(f"Input file not found: {input_path}")

        # Ensure quality is enum
        if isinstance(quality, str):
            try:
                quality = CompressionQuality(quality)
            except ValueError:
                quality = CompressionQuality.MEDIUM

        original_size = input_path.stat().st_size
        dpi = custom_dpi or QUALITY_DPI.get(quality, 150)

        cmd = self._build_gs_command(input_path, output_path, quality, custom_dpi)

        try:
            # Run Ghostscript asynchronously
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise FileProcessingError(f"Ghostscript failed: {error_msg}")

            if not output_path.exists():
                raise FileProcessingError("Compression produced no output file")

            compressed_size = output_path.stat().st_size

            return CompressionResult(
                output_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size,
                quality=quality.value,
                dpi=dpi,
            )

        except asyncio.CancelledError:
            # Clean up partial output if cancelled
            if output_path.exists():
                output_path.unlink()
            raise
        except subprocess.SubprocessError as e:
            raise FileProcessingError(f"Failed to run Ghostscript: {e}")

    async def compress_to_target_size(
        self,
        input_path: Path,
        output_path: Path,
        target_size_mb: float,
        max_iterations: int = 5,
    ) -> CompressionResult:
        """
        Compress PDF to achieve target file size.

        Uses iterative compression with decreasing DPI to reach target.

        Args:
            input_path: Path to input PDF
            output_path: Path for compressed output
            target_size_mb: Target file size in MB
            max_iterations: Maximum compression attempts

        Returns:
            CompressionResult with output path and statistics

        Raises:
            FileProcessingError: If target cannot be achieved
        """
        target_size_bytes = int(target_size_mb * 1024 * 1024)
        original_size = input_path.stat().st_size

        # If already under target, just copy or do light compression
        if original_size <= target_size_bytes:
            return await self.compress(input_path, output_path, CompressionQuality.HIGH)

        # Start with medium quality and adjust
        dpi_values = [150, 120, 96, 72, 50, 36]
        best_result: CompressionResult | None = None

        for i, dpi in enumerate(dpi_values):
            if i >= max_iterations:
                break

            # Use temporary output for iterations
            temp_output = output_path.with_suffix(f".temp{i}.pdf")

            try:
                result = await self.compress(
                    input_path,
                    temp_output,
                    CompressionQuality.LOW,
                    custom_dpi=dpi,
                )

                # Check if we hit target
                if result.compressed_size <= target_size_bytes:
                    # Move to final output
                    temp_output.rename(output_path)
                    result.output_path = output_path
                    return result

                # Keep track of best result
                if best_result is None or result.compressed_size < best_result.compressed_size:
                    if best_result and best_result.output_path.exists():
                        best_result.output_path.unlink()
                    best_result = result
                else:
                    temp_output.unlink()

            except FileProcessingError:
                if temp_output.exists():
                    temp_output.unlink()
                continue

        # Return best result even if target not achieved
        if best_result:
            if best_result.output_path != output_path:
                best_result.output_path.rename(output_path)
                best_result.output_path = output_path
            return best_result

        raise FileProcessingError(
            f"Could not compress file to target size of {target_size_mb}MB"
        )


# Global instance
compression_service = CompressionService()


def get_compression_service() -> CompressionService:
    """Dependency for getting compression service instance."""
    return compression_service
