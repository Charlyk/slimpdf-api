"""Tests for the merge service."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.services.merge import (
    MergeService,
    MergeInput,
    MergeResult,
    PageRange,
)
from app.exceptions import FileProcessingError


class TestPageRange:
    """Tests for PageRange class."""

    def test_to_fitz_range_basic(self):
        """Test basic page range conversion."""
        pr = PageRange(start=1, end=5)
        start, end = pr.to_fitz_range(total_pages=10)
        assert start == 0  # 0-indexed
        assert end == 4

    def test_to_fitz_range_no_end(self):
        """Test page range with no end (to last page)."""
        pr = PageRange(start=3, end=None)
        start, end = pr.to_fitz_range(total_pages=10)
        assert start == 2
        assert end == 9

    def test_to_fitz_range_exceeds_total(self):
        """Test page range that exceeds total pages."""
        pr = PageRange(start=1, end=20)
        start, end = pr.to_fitz_range(total_pages=10)
        assert start == 0
        assert end == 9  # Clamped to max

    def test_to_fitz_range_start_clamped(self):
        """Test page range with invalid start."""
        pr = PageRange(start=0, end=5)  # 0 is invalid (1-indexed)
        start, end = pr.to_fitz_range(total_pages=10)
        assert start == 0  # max(0, -1) = 0


class TestMergeInput:
    """Tests for MergeInput class."""

    def test_merge_input_basic(self, temp_dir: Path):
        """Test basic MergeInput creation."""
        path = temp_dir / "test.pdf"
        mi = MergeInput(path=path)
        assert mi.path == path
        assert mi.page_range is None

    def test_merge_input_with_range(self, temp_dir: Path):
        """Test MergeInput with page range."""
        path = temp_dir / "test.pdf"
        pr = PageRange(start=1, end=5)
        mi = MergeInput(path=path, page_range=pr)
        assert mi.page_range == pr


class TestMergeResult:
    """Tests for MergeResult class."""

    def test_merge_result(self, temp_dir: Path):
        """Test MergeResult creation."""
        result = MergeResult(
            output_path=temp_dir / "merged.pdf",
            total_pages=15,
            input_files=3,
            output_size=1024,
        )
        assert result.total_pages == 15
        assert result.input_files == 3
        assert result.output_size == 1024


class TestMergeService:
    """Tests for MergeService."""

    @pytest.fixture
    def service(self):
        """Create merge service."""
        return MergeService()

    @pytest.mark.asyncio
    async def test_merge_empty_input(self, service):
        """Test merge fails with empty input list."""
        with pytest.raises(FileProcessingError, match="No input files"):
            await service.merge([], Path("/tmp/output.pdf"))

    @pytest.mark.asyncio
    async def test_merge_file_not_found(self, service, temp_dir: Path):
        """Test merge fails with nonexistent file."""
        nonexistent = temp_dir / "nonexistent.pdf"
        output = temp_dir / "output.pdf"

        with pytest.raises(FileProcessingError, match="not found"):
            await service.merge([nonexistent], output)

    @pytest.mark.asyncio
    async def test_merge_success(self, service, temp_dir: Path):
        """Test successful PDF merge using PyMuPDF."""
        import fitz

        # Create two simple PDFs
        pdf1_path = temp_dir / "pdf1.pdf"
        pdf2_path = temp_dir / "pdf2.pdf"
        output_path = temp_dir / "merged.pdf"

        # Create PDF 1 with 2 pages
        doc1 = fitz.open()
        doc1.new_page()
        doc1.new_page()
        doc1.save(pdf1_path)
        doc1.close()

        # Create PDF 2 with 3 pages
        doc2 = fitz.open()
        doc2.new_page()
        doc2.new_page()
        doc2.new_page()
        doc2.save(pdf2_path)
        doc2.close()

        # Merge
        result = await service.merge(
            [pdf1_path, pdf2_path],
            output_path,
        )

        assert result.total_pages == 5
        assert result.input_files == 2
        assert output_path.exists()

        # Verify merged PDF
        merged = fitz.open(output_path)
        assert len(merged) == 5
        merged.close()

    @pytest.mark.asyncio
    async def test_merge_with_ranges(self, service, temp_dir: Path):
        """Test merge with page ranges."""
        import fitz

        # Create PDF with 5 pages
        pdf_path = temp_dir / "source.pdf"
        output_path = temp_dir / "merged.pdf"

        doc = fitz.open()
        for i in range(5):
            doc.new_page()
        doc.save(pdf_path)
        doc.close()

        # Merge pages 2-4 only
        inputs = [
            MergeInput(
                path=pdf_path,
                page_range=PageRange(start=2, end=4),
            )
        ]

        result = await service.merge_with_ranges(inputs, output_path)

        assert result.total_pages == 3
        assert output_path.exists()

        # Verify
        merged = fitz.open(output_path)
        assert len(merged) == 3
        merged.close()

    def test_get_page_count(self, service, temp_dir: Path):
        """Test getting page count from PDF."""
        import fitz

        pdf_path = temp_dir / "test.pdf"
        doc = fitz.open()
        doc.new_page()
        doc.new_page()
        doc.new_page()
        doc.save(pdf_path)
        doc.close()

        count = service.get_page_count(pdf_path)
        assert count == 3

    def test_validate_pdf_valid(self, service, temp_dir: Path):
        """Test PDF validation with valid file."""
        import fitz

        pdf_path = temp_dir / "valid.pdf"
        doc = fitz.open()
        doc.new_page()
        doc.save(pdf_path)
        doc.close()

        assert service.validate_pdf(pdf_path) is True

    def test_validate_pdf_invalid(self, service, temp_dir: Path):
        """Test PDF validation with invalid file."""
        invalid_path = temp_dir / "invalid.pdf"
        invalid_path.write_text("not a pdf")

        assert service.validate_pdf(invalid_path) is False

    @pytest.mark.asyncio
    async def test_merge_preserves_bookmarks(self, service, temp_dir: Path):
        """Test that bookmarks are preserved during merge."""
        import fitz

        # Create PDF with bookmarks
        pdf_path = temp_dir / "with_bookmarks.pdf"
        output_path = temp_dir / "merged.pdf"

        doc = fitz.open()
        doc.new_page()
        doc.new_page()
        doc.set_toc([[1, "Chapter 1", 1], [1, "Chapter 2", 2]])
        doc.save(pdf_path)
        doc.close()

        # Merge
        result = await service.merge(
            [pdf_path],
            output_path,
            preserve_bookmarks=True,
        )

        # Check bookmarks preserved
        merged = fitz.open(output_path)
        toc = merged.get_toc()
        assert len(toc) == 2
        merged.close()
