"""Tests for the compression service."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.compression import (
    CompressionService,
    CompressionQuality,
    CompressionResult,
    QUALITY_DPI,
)
from app.exceptions import FileProcessingError


class TestCompressionQuality:
    """Tests for compression quality settings."""

    def test_quality_values(self):
        """Test quality enum values match Ghostscript settings."""
        assert CompressionQuality.LOW.value == "screen"
        assert CompressionQuality.MEDIUM.value == "ebook"
        assert CompressionQuality.HIGH.value == "printer"
        assert CompressionQuality.MAXIMUM.value == "prepress"

    def test_quality_dpi_mapping(self):
        """Test DPI values for each quality level."""
        assert QUALITY_DPI[CompressionQuality.LOW] == 72
        assert QUALITY_DPI[CompressionQuality.MEDIUM] == 150
        assert QUALITY_DPI[CompressionQuality.HIGH] == 300
        assert QUALITY_DPI[CompressionQuality.MAXIMUM] == 300


class TestCompressionResult:
    """Tests for CompressionResult dataclass."""

    def test_reduction_percent(self):
        """Test compression reduction percentage calculation."""
        result = CompressionResult(
            output_path=Path("/tmp/out.pdf"),
            original_size=1000,
            compressed_size=300,
            quality="medium",
            dpi=150,
        )
        assert result.reduction_percent == 70.0

    def test_reduction_percent_zero_original(self):
        """Test reduction percent with zero original size."""
        result = CompressionResult(
            output_path=Path("/tmp/out.pdf"),
            original_size=0,
            compressed_size=0,
            quality="medium",
            dpi=150,
        )
        assert result.reduction_percent == 0.0

    def test_compression_ratio(self):
        """Test compression ratio calculation."""
        result = CompressionResult(
            output_path=Path("/tmp/out.pdf"),
            original_size=1000,
            compressed_size=250,
            quality="medium",
            dpi=150,
        )
        assert result.compression_ratio == 4.0


class TestCompressionService:
    """Tests for CompressionService."""

    @pytest.fixture
    def service(self):
        """Create compression service with mocked Ghostscript."""
        with patch.object(CompressionService, '_find_ghostscript', return_value='gs'):
            return CompressionService()

    def test_init_finds_ghostscript(self, service):
        """Test service initialization finds Ghostscript."""
        assert service.gs_command == 'gs'

    def test_build_gs_command(self, service, temp_dir: Path):
        """Test Ghostscript command building."""
        input_path = temp_dir / "input.pdf"
        output_path = temp_dir / "output.pdf"

        cmd = service._build_gs_command(
            input_path,
            output_path,
            CompressionQuality.MEDIUM,
        )

        assert "gs" in cmd
        assert "-sDEVICE=pdfwrite" in cmd
        assert "-dPDFSETTINGS=/ebook" in cmd
        assert f"-sOutputFile={output_path}" in cmd
        assert str(input_path) in cmd

    def test_build_gs_command_custom_dpi(self, service, temp_dir: Path):
        """Test Ghostscript command with custom DPI."""
        input_path = temp_dir / "input.pdf"
        output_path = temp_dir / "output.pdf"

        cmd = service._build_gs_command(
            input_path,
            output_path,
            CompressionQuality.LOW,
            custom_dpi=96,
        )

        assert "-dColorImageResolution=96" in cmd

    @pytest.mark.asyncio
    async def test_compress_file_not_found(self, service, temp_dir: Path):
        """Test compression fails with nonexistent file."""
        input_path = temp_dir / "nonexistent.pdf"
        output_path = temp_dir / "output.pdf"

        with pytest.raises(FileProcessingError, match="not found"):
            await service.compress(input_path, output_path)

    @pytest.mark.asyncio
    async def test_compress_success(self, service, sample_pdf_path: Path, temp_dir: Path):
        """Test successful compression."""
        output_path = temp_dir / "output.pdf"

        # Mock subprocess execution
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_exec.return_value = mock_process

            # Create output file to simulate Ghostscript output
            output_path.write_bytes(b"compressed pdf content")

            result = await service.compress(
                sample_pdf_path,
                output_path,
                CompressionQuality.MEDIUM,
            )

            assert result.output_path == output_path
            assert result.quality == "ebook"
            assert result.dpi == 150

    @pytest.mark.asyncio
    async def test_compress_ghostscript_failure(self, service, sample_pdf_path: Path, temp_dir: Path):
        """Test handling of Ghostscript failure."""
        output_path = temp_dir / "output.pdf"

        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_process.communicate = AsyncMock(return_value=(b"", b"Error message"))
            mock_exec.return_value = mock_process

            with pytest.raises(FileProcessingError, match="Ghostscript failed"):
                await service.compress(sample_pdf_path, output_path)

    @pytest.mark.asyncio
    async def test_compress_to_target_size_already_small(
        self, service, sample_pdf_path: Path, temp_dir: Path
    ):
        """Test target size compression when file is already small enough."""
        output_path = temp_dir / "output.pdf"

        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_exec.return_value = mock_process

            # Create smaller output file
            output_path.write_bytes(b"x" * 100)

            result = await service.compress_to_target_size(
                sample_pdf_path,
                output_path,
                target_size_mb=10,  # File is already smaller
            )

            assert result.output_path == output_path

    def test_quality_string_conversion(self, service, temp_dir: Path):
        """Test quality string to enum conversion in command building."""
        input_path = temp_dir / "input.pdf"
        output_path = temp_dir / "output.pdf"

        # Test with string value
        cmd = service._build_gs_command(
            input_path,
            output_path,
            "medium",  # String instead of enum
        )

        assert "-dPDFSETTINGS=/ebook" in cmd
