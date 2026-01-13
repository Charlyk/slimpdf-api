"""PDF compression service using Ghostscript."""

import asyncio
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from app.exceptions import FileProcessingError


class CompressionQuality(str, Enum):
    """Compression quality presets.

    Note: Quality refers to OUTPUT quality, not compression level.
    - LOW quality = Maximum compression, smallest files
    - MAXIMUM quality = Minimal compression, best quality
    """

    LOW = "low"           # Maximum compression, 72 dpi
    MEDIUM = "medium"     # Balanced, 150 dpi
    HIGH = "high"         # Good quality, 200 dpi
    MAXIMUM = "maximum"   # Best quality, 300 dpi


# Settings for each quality level
# QFactor: 0.0 = best quality, larger values = more compression (max ~2.5)
# Subsampling: [1 1 1 1] = no subsampling, [2 1 1 2] = 4:2:0 chroma subsampling
QUALITY_SETTINGS = {
    CompressionQuality.LOW: {
        "dpi": 50,
        "qfactor": 2.4,  # Maximum compression
        "subsampling": "[2 1 1 2]",  # 4:2:0 chroma subsampling for smaller files
        "pdfsettings": "/screen",
    },
    CompressionQuality.MEDIUM: {
        "dpi": 72,
        "qfactor": 1.8,  # High compression
        "subsampling": "[2 1 1 2]",
        "pdfsettings": "/ebook",
    },
    CompressionQuality.HIGH: {
        "dpi": 100,
        "qfactor": 1.0,  # Medium compression
        "subsampling": "[1 1 1 1]",  # No subsampling for better quality
        "pdfsettings": "/ebook",
    },
    CompressionQuality.MAXIMUM: {
        "dpi": 150,
        "qfactor": 0.4,  # Light compression, best quality
        "subsampling": "[1 1 1 1]",
        "pdfsettings": "/printer",
    },
}

# Backwards compatibility
QUALITY_DPI = {
    CompressionQuality.LOW: 72,
    CompressionQuality.MEDIUM: 120,
    CompressionQuality.HIGH: 150,
    CompressionQuality.MAXIMUM: 200,
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
        custom_qfactor: float | None = None,
    ) -> list[str]:
        """Build Ghostscript command with appropriate settings."""
        # Get quality setting
        if isinstance(quality, str):
            try:
                quality = CompressionQuality(quality)
            except ValueError:
                quality = CompressionQuality.MEDIUM

        settings = QUALITY_SETTINGS.get(quality, QUALITY_SETTINGS[CompressionQuality.MEDIUM])
        dpi = custom_dpi or settings["dpi"]
        qfactor = custom_qfactor or settings["qfactor"]
        pdf_setting = settings["pdfsettings"]
        subsampling = settings.get("subsampling", "[1 1 1 1]")

        # Build PostScript command for JPEG quality settings
        # QFactor: 0.0 = best quality, higher = more compression
        # HSamples/VSamples: [1 1 1 1] = no subsampling, [2 1 1 2] = 4:2:0 chroma subsampling
        ps_quality_settings = (
            f"<< /ColorACSImageDict << /QFactor {qfactor} /Blend 1 "
            f"/HSamples {subsampling} /VSamples {subsampling} >> "
            f"/GrayACSImageDict << /QFactor {qfactor} /Blend 1 "
            f"/HSamples {subsampling} /VSamples {subsampling} >> >> setdistillerparams"
        )

        cmd = [
            self.gs_command,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={pdf_setting}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            # Output file (must be before -c/-f)
            f"-sOutputFile={output_path}",
            # Optimization flags
            "-dDetectDuplicateImages=true",
            "-dCompressFonts=true",
            "-dSubsetFonts=true",
            "-dEmbedAllFonts=false",  # Don't embed fonts already in the system
            "-dPrinted=false",  # Optimize for screen viewing
            # Image compression settings
            "-dAutoFilterColorImages=false",
            "-dAutoFilterGrayImages=false",
            "-dColorImageFilter=/DCTEncode",
            "-dGrayImageFilter=/DCTEncode",
            f"-dColorImageResolution={dpi}",
            f"-dGrayImageResolution={dpi}",
            f"-dMonoImageResolution={dpi}",
            # Image downsampling - force it even if image is smaller
            "-dDownsampleColorImages=true",
            "-dDownsampleGrayImages=true",
            "-dDownsampleMonoImages=true",
            "-dColorImageDownsampleType=/Bicubic",
            "-dGrayImageDownsampleType=/Bicubic",
            "-dMonoImageDownsampleType=/Bicubic",
            "-dColorImageDownsampleThreshold=1.0",
            "-dGrayImageDownsampleThreshold=1.0",
            "-dMonoImageDownsampleThreshold=1.0",
            # PassThroughJPEGImages=false forces re-encoding of JPEGs
            "-dPassThroughJPEGImages=false",
            # PostScript command for JPEG quality
            "-c", ps_quality_settings,
            # Input file flag and input file
            "-f", str(input_path),
        ]
        return cmd

    async def compress(
        self,
        input_path: Path,
        output_path: Path,
        quality: CompressionQuality | str = CompressionQuality.MEDIUM,
        custom_dpi: int | None = None,
        custom_qfactor: float | None = None,
    ) -> CompressionResult:
        """
        Compress a PDF file using Ghostscript.

        Args:
            input_path: Path to input PDF
            output_path: Path for compressed output
            quality: Compression quality preset
            custom_dpi: Optional custom DPI override
            custom_qfactor: Optional custom QFactor (0.0=best quality, higher=more compression)

        Returns:
            CompressionResult with output path and statistics.
            If compression results in a larger file, returns the original file.

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
        settings = QUALITY_SETTINGS.get(quality, QUALITY_SETTINGS[CompressionQuality.MEDIUM])
        dpi = custom_dpi or settings["dpi"]

        # Use a temporary path for compression
        temp_output = output_path.with_suffix(".temp.pdf")

        cmd = self._build_gs_command(
            input_path, temp_output, quality, custom_dpi, custom_qfactor
        )

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

            if not temp_output.exists():
                raise FileProcessingError("Compression produced no output file")

            compressed_size = temp_output.stat().st_size

            # If compression made file bigger, use original instead
            if compressed_size >= original_size:
                temp_output.unlink()
                shutil.copy2(input_path, output_path)
                return CompressionResult(
                    output_path=output_path,
                    original_size=original_size,
                    compressed_size=original_size,
                    quality=quality.value,
                    dpi=dpi,
                )

            # Use compressed file
            temp_output.rename(output_path)

            return CompressionResult(
                output_path=output_path,
                original_size=original_size,
                compressed_size=compressed_size,
                quality=quality.value,
                dpi=dpi,
            )

        except asyncio.CancelledError:
            # Clean up partial output if cancelled
            if temp_output.exists():
                temp_output.unlink()
            if output_path.exists():
                output_path.unlink()
            raise
        except subprocess.SubprocessError as e:
            if temp_output.exists():
                temp_output.unlink()
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
