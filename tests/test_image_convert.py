"""Tests for the image-to-pdf conversion service."""

import pytest
from pathlib import Path
from PIL import Image

from app.services.image_convert import (
    ImageConvertService,
    ImageConvertResult,
    PageSize,
    PAGE_DIMENSIONS,
    SUPPORTED_FORMATS,
)
from app.exceptions import FileProcessingError, InvalidFileTypeError


class TestPageSize:
    """Tests for PageSize enum."""

    def test_page_size_values(self):
        """Test page size enum values."""
        assert PageSize.A4.value == "a4"
        assert PageSize.LETTER.value == "letter"
        assert PageSize.ORIGINAL.value == "original"

    def test_page_dimensions(self):
        """Test page dimension constants."""
        # A4: 210mm x 297mm ≈ 595 x 842 points
        assert PAGE_DIMENSIONS[PageSize.A4] == (595.276, 841.890)
        # Letter: 8.5" x 11" = 612 x 792 points
        assert PAGE_DIMENSIONS[PageSize.LETTER] == (612, 792)


class TestSupportedFormats:
    """Tests for supported image formats."""

    def test_supported_formats_include_common(self):
        """Test that common formats are supported."""
        assert ".jpg" in SUPPORTED_FORMATS
        assert ".jpeg" in SUPPORTED_FORMATS
        assert ".png" in SUPPORTED_FORMATS
        assert ".webp" in SUPPORTED_FORMATS
        assert ".gif" in SUPPORTED_FORMATS
        assert ".bmp" in SUPPORTED_FORMATS
        assert ".tiff" in SUPPORTED_FORMATS


class TestImageConvertResult:
    """Tests for ImageConvertResult class."""

    def test_result_creation(self, temp_dir: Path):
        """Test result dataclass creation."""
        result = ImageConvertResult(
            output_path=temp_dir / "output.pdf",
            page_count=5,
            output_size=1024,
        )
        assert result.page_count == 5
        assert result.output_size == 1024


class TestImageConvertService:
    """Tests for ImageConvertService."""

    @pytest.fixture
    def service(self):
        """Create image convert service."""
        return ImageConvertService()

    @pytest.fixture
    def create_image(self, temp_dir: Path):
        """Factory to create test images."""
        def _create(filename: str, size: tuple = (100, 100), mode: str = "RGB") -> Path:
            img_path = temp_dir / filename
            img = Image.new(mode, size, color="blue")

            # Determine format from extension
            ext = Path(filename).suffix.lower()
            if ext == ".jpg" or ext == ".jpeg":
                if mode == "RGBA":
                    img = img.convert("RGB")
                img.save(img_path, "JPEG")
            elif ext == ".png":
                img.save(img_path, "PNG")
            elif ext == ".webp":
                img.save(img_path, "WEBP")
            elif ext == ".gif":
                img.save(img_path, "GIF")
            elif ext == ".bmp":
                if mode == "RGBA":
                    img = img.convert("RGB")
                img.save(img_path, "BMP")
            else:
                img.save(img_path)

            return img_path
        return _create

    def test_is_supported_format(self, service):
        """Test format support checking."""
        assert service.is_supported_format("image.jpg") is True
        assert service.is_supported_format("image.jpeg") is True
        assert service.is_supported_format("image.png") is True
        assert service.is_supported_format("image.webp") is True
        assert service.is_supported_format("image.gif") is True
        assert service.is_supported_format("image.bmp") is True
        assert service.is_supported_format("image.tiff") is True
        assert service.is_supported_format("image.pdf") is False
        assert service.is_supported_format("image.doc") is False

    def test_validate_image_invalid_extension(self, service, temp_dir: Path):
        """Test validation fails for invalid extension."""
        invalid_path = temp_dir / "test.txt"
        invalid_path.write_text("not an image")

        with pytest.raises(InvalidFileTypeError):
            service._validate_image(invalid_path)

    def test_validate_image_invalid_content(self, service, temp_dir: Path):
        """Test validation fails for invalid image content."""
        fake_image = temp_dir / "fake.png"
        fake_image.write_bytes(b"not image data")

        with pytest.raises(FileProcessingError, match="Invalid image"):
            service._validate_image(fake_image)

    @pytest.mark.asyncio
    async def test_convert_single_jpg(self, service, create_image, temp_dir: Path):
        """Test converting a single JPG image."""
        img_path = create_image("test.jpg")
        output_path = temp_dir / "output.pdf"

        result = await service.convert_single(
            img_path,
            output_path,
            PageSize.A4,
        )

        assert result.page_count == 1
        assert result.output_path.exists()
        assert result.output_size > 0

    @pytest.mark.asyncio
    async def test_convert_single_png(self, service, create_image, temp_dir: Path):
        """Test converting a single PNG image."""
        img_path = create_image("test.png")
        output_path = temp_dir / "output.pdf"

        result = await service.convert_single(
            img_path,
            output_path,
            PageSize.LETTER,
        )

        assert result.page_count == 1
        assert result.output_path.exists()

    @pytest.mark.asyncio
    async def test_convert_single_webp(self, service, create_image, temp_dir: Path):
        """Test converting a WebP image (requires format conversion)."""
        img_path = create_image("test.webp")
        output_path = temp_dir / "output.pdf"

        result = await service.convert_single(
            img_path,
            output_path,
            PageSize.A4,
        )

        assert result.page_count == 1
        assert result.output_path.exists()

    @pytest.mark.asyncio
    async def test_convert_multiple(self, service, create_image, temp_dir: Path):
        """Test converting multiple images to a single PDF."""
        images = [
            create_image("img1.jpg"),
            create_image("img2.png"),
            create_image("img3.jpg"),
        ]
        output_path = temp_dir / "output.pdf"

        result = await service.convert_multiple(
            images,
            output_path,
            PageSize.A4,
        )

        assert result.page_count == 3
        assert result.output_path.exists()

    @pytest.mark.asyncio
    async def test_convert_multiple_empty_list(self, service, temp_dir: Path):
        """Test converting empty list fails."""
        output_path = temp_dir / "output.pdf"

        with pytest.raises(FileProcessingError, match="No images"):
            await service.convert_multiple([], output_path)

    @pytest.mark.asyncio
    async def test_convert_original_size(self, service, create_image, temp_dir: Path):
        """Test converting with original image dimensions."""
        img_path = create_image("test.jpg", size=(800, 600))
        output_path = temp_dir / "output.pdf"

        result = await service.convert_single(
            img_path,
            output_path,
            PageSize.ORIGINAL,
        )

        assert result.page_count == 1
        assert result.output_path.exists()

    def test_get_image_dimensions(self, service, create_image):
        """Test getting image dimensions."""
        img_path = create_image("test.png", size=(640, 480))

        width, height = service.get_image_dimensions(img_path)

        assert width == 640
        assert height == 480

    @pytest.mark.asyncio
    async def test_convert_rgba_png(self, service, temp_dir: Path):
        """Test converting RGBA PNG (with alpha channel)."""
        img_path = temp_dir / "rgba.png"
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        img.save(img_path, "PNG")

        output_path = temp_dir / "output.pdf"

        result = await service.convert_single(
            img_path,
            output_path,
            PageSize.A4,
        )

        assert result.page_count == 1
        assert result.output_path.exists()

    @pytest.mark.asyncio
    async def test_cleanup_temp_files(self, service, create_image, temp_dir: Path):
        """Test that temporary conversion files are cleaned up."""
        # WebP requires conversion to JPEG
        img_path = create_image("test.webp")
        output_path = temp_dir / "output.pdf"

        await service.convert_single(img_path, output_path, PageSize.A4)

        # Check no .jpg temp files left behind
        temp_files = list(temp_dir.glob("*.jpg"))
        # Original should still be there, but not conversion temps
        assert len([f for f in temp_files if "test" not in f.name]) == 0
