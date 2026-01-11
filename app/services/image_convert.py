"""Image to PDF conversion service using Pillow and img2pdf."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import BinaryIO

import img2pdf
from PIL import Image

from app.exceptions import FileProcessingError, InvalidFileTypeError


class PageSize(str, Enum):
    """Page size options for image to PDF conversion."""

    A4 = "a4"
    LETTER = "letter"
    ORIGINAL = "original"  # Keep original image dimensions


# Page dimensions in points (72 points = 1 inch)
PAGE_DIMENSIONS = {
    PageSize.A4: (595.276, 841.890),  # 210mm x 297mm
    PageSize.LETTER: (612, 792),  # 8.5" x 11"
}

# Supported image formats
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp", ".gif"}


@dataclass
class ImageConvertResult:
    """Result of an image to PDF conversion."""

    output_path: Path
    page_count: int
    output_size: int


class ImageConvertService:
    """Service for converting images to PDF."""

    def _validate_image(self, file_path: Path) -> None:
        """
        Validate that a file is a supported image format.

        Args:
            file_path: Path to image file

        Raises:
            InvalidFileTypeError: If not a supported image
        """
        suffix = file_path.suffix.lower()
        if suffix not in SUPPORTED_FORMATS:
            raise InvalidFileTypeError(
                expected=", ".join(SUPPORTED_FORMATS),
                actual=suffix or "unknown",
            )

        # Verify it's a valid image
        try:
            with Image.open(file_path) as img:
                img.verify()
        except Exception as e:
            raise FileProcessingError(f"Invalid image file: {e}")

    def _prepare_image(self, file_path: Path) -> Path:
        """
        Prepare image for PDF conversion.

        Converts unsupported formats (like WebP) to JPEG.
        Handles RGBA images by converting to RGB.

        Args:
            file_path: Path to image file

        Returns:
            Path to prepared image (may be same as input)
        """
        suffix = file_path.suffix.lower()

        # img2pdf supports JPEG, PNG, and some others natively
        # For WebP and others, convert to JPEG
        if suffix in {".webp", ".bmp", ".gif"}:
            with Image.open(file_path) as img:
                # Convert RGBA to RGB (remove alpha channel)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Save as JPEG
                output_path = file_path.with_suffix(".jpg")
                img.save(output_path, "JPEG", quality=95)
                return output_path

        # Handle PNG with alpha channel
        if suffix == ".png":
            with Image.open(file_path) as img:
                if img.mode == "RGBA":
                    # Convert to RGB with white background
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    output_path = file_path.with_suffix(".converted.jpg")
                    background.save(output_path, "JPEG", quality=95)
                    return output_path

        return file_path

    def _get_layout_fun(self, page_size: PageSize):
        """
        Get img2pdf layout function for specified page size.

        Args:
            page_size: Desired page size

        Returns:
            Layout function for img2pdf
        """
        if page_size == PageSize.ORIGINAL:
            # Use image dimensions
            return img2pdf.get_layout_fun(None)

        width, height = PAGE_DIMENSIONS[page_size]

        # Fit image to page while maintaining aspect ratio
        return img2pdf.get_layout_fun(
            pagesize=(width, height),
            fit=img2pdf.FitMode.into,
        )

    async def convert_single(
        self,
        image_path: Path,
        output_path: Path,
        page_size: PageSize = PageSize.A4,
    ) -> ImageConvertResult:
        """
        Convert a single image to PDF.

        Args:
            image_path: Path to image file
            output_path: Path for PDF output
            page_size: Page size for the PDF

        Returns:
            ImageConvertResult with output path and statistics

        Raises:
            FileProcessingError: If conversion fails
        """
        self._validate_image(image_path)

        try:
            # Prepare image (convert format if needed)
            prepared_path = self._prepare_image(image_path)

            # Get layout function
            layout_fun = self._get_layout_fun(page_size)

            # Convert to PDF
            with open(prepared_path, "rb") as img_file:
                pdf_bytes = img2pdf.convert(img_file, layout_fun=layout_fun)

            # Write output
            with open(output_path, "wb") as pdf_file:
                pdf_file.write(pdf_bytes)

            # Clean up temp file if we created one
            if prepared_path != image_path:
                prepared_path.unlink()

            return ImageConvertResult(
                output_path=output_path,
                page_count=1,
                output_size=output_path.stat().st_size,
            )

        except img2pdf.ImageOpenError as e:
            raise FileProcessingError(f"Failed to open image: {e}")
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise FileProcessingError(f"Failed to convert image to PDF: {e}")

    async def convert_multiple(
        self,
        image_paths: list[Path],
        output_path: Path,
        page_size: PageSize = PageSize.A4,
    ) -> ImageConvertResult:
        """
        Convert multiple images to a single PDF.

        Args:
            image_paths: List of paths to image files (in order)
            output_path: Path for PDF output
            page_size: Page size for all pages

        Returns:
            ImageConvertResult with output path and statistics

        Raises:
            FileProcessingError: If conversion fails
        """
        if not image_paths:
            raise FileProcessingError("No images provided")

        # Validate all images
        for path in image_paths:
            self._validate_image(path)

        prepared_paths = []
        temp_files = []

        try:
            # Prepare all images
            for path in image_paths:
                prepared = self._prepare_image(path)
                prepared_paths.append(prepared)
                if prepared != path:
                    temp_files.append(prepared)

            # Get layout function
            layout_fun = self._get_layout_fun(page_size)

            # Open all image files
            image_files: list[BinaryIO] = []
            try:
                for path in prepared_paths:
                    image_files.append(open(path, "rb"))

                # Convert all to PDF
                pdf_bytes = img2pdf.convert(image_files, layout_fun=layout_fun)

            finally:
                # Close all files
                for f in image_files:
                    f.close()

            # Write output
            with open(output_path, "wb") as pdf_file:
                pdf_file.write(pdf_bytes)

            return ImageConvertResult(
                output_path=output_path,
                page_count=len(image_paths),
                output_size=output_path.stat().st_size,
            )

        except img2pdf.ImageOpenError as e:
            raise FileProcessingError(f"Failed to open image: {e}")
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise FileProcessingError(f"Failed to convert images to PDF: {e}")
        finally:
            # Clean up temp files
            for temp_path in temp_files:
                if temp_path.exists():
                    temp_path.unlink()

    def get_image_dimensions(self, image_path: Path) -> tuple[int, int]:
        """
        Get image dimensions.

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (width, height) in pixels
        """
        with Image.open(image_path) as img:
            return img.size

    def is_supported_format(self, filename: str) -> bool:
        """
        Check if a filename has a supported image format.

        Args:
            filename: Filename to check

        Returns:
            True if supported format
        """
        suffix = Path(filename).suffix.lower()
        return suffix in SUPPORTED_FORMATS


# Global instance
image_convert_service = ImageConvertService()


def get_image_convert_service() -> ImageConvertService:
    """Dependency for getting image convert service instance."""
    return image_convert_service
