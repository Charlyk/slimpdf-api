"""PDF merge service using PyMuPDF."""

from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF

from app.exceptions import FileProcessingError


@dataclass
class PageRange:
    """Represents a range of pages to include from a PDF."""

    start: int  # 1-indexed
    end: int | None = None  # None means to the end

    def to_fitz_range(self, total_pages: int) -> tuple[int, int]:
        """Convert to 0-indexed range for PyMuPDF."""
        start = max(0, self.start - 1)
        end = (self.end or total_pages) - 1
        end = min(end, total_pages - 1)
        return start, end


@dataclass
class MergeInput:
    """Input file with optional page range."""

    path: Path
    page_range: PageRange | None = None


@dataclass
class MergeResult:
    """Result of a PDF merge operation."""

    output_path: Path
    total_pages: int
    input_files: int
    output_size: int


class MergeService:
    """Service for merging PDF files using PyMuPDF."""

    async def merge(
        self,
        input_paths: list[Path],
        output_path: Path,
        preserve_bookmarks: bool = True,
    ) -> MergeResult:
        """
        Merge multiple PDF files into one.

        Args:
            input_paths: List of paths to PDF files (in order)
            output_path: Path for merged output
            preserve_bookmarks: Whether to preserve bookmarks from source PDFs

        Returns:
            MergeResult with output path and statistics

        Raises:
            FileProcessingError: If merge fails
        """
        if not input_paths:
            raise FileProcessingError("No input files provided")

        # Validate all inputs exist
        for path in input_paths:
            if not path.exists():
                raise FileProcessingError(f"Input file not found: {path}")

        try:
            # Create output document
            output_doc = fitz.open()
            total_pages = 0
            toc_entries = []
            current_page = 0

            for i, input_path in enumerate(input_paths):
                # Open source document
                src_doc = fitz.open(input_path)

                # Add pages to output
                output_doc.insert_pdf(src_doc)

                # Collect bookmarks if preserving
                if preserve_bookmarks:
                    src_toc = src_doc.get_toc()
                    for level, title, page in src_toc:
                        # Adjust page numbers for merged document
                        toc_entries.append([level, title, page + current_page])

                current_page += len(src_doc)
                total_pages += len(src_doc)
                src_doc.close()

            # Set table of contents if we have entries
            if toc_entries:
                output_doc.set_toc(toc_entries)

            # Save output
            output_doc.save(output_path, garbage=4, deflate=True)
            output_doc.close()

            output_size = output_path.stat().st_size

            return MergeResult(
                output_path=output_path,
                total_pages=total_pages,
                input_files=len(input_paths),
                output_size=output_size,
            )

        except fitz.FileDataError as e:
            raise FileProcessingError(f"Invalid PDF file: {e}")
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise FileProcessingError(f"Failed to merge PDFs: {e}")

    async def merge_with_ranges(
        self,
        inputs: list[MergeInput],
        output_path: Path,
        preserve_bookmarks: bool = True,
    ) -> MergeResult:
        """
        Merge PDFs with specific page ranges.

        Args:
            inputs: List of MergeInput with paths and optional page ranges
            output_path: Path for merged output
            preserve_bookmarks: Whether to preserve bookmarks

        Returns:
            MergeResult with output path and statistics

        Raises:
            FileProcessingError: If merge fails
        """
        if not inputs:
            raise FileProcessingError("No input files provided")

        try:
            output_doc = fitz.open()
            total_pages = 0
            toc_entries = []
            current_page = 0

            for merge_input in inputs:
                if not merge_input.path.exists():
                    raise FileProcessingError(f"Input file not found: {merge_input.path}")

                src_doc = fitz.open(merge_input.path)
                src_pages = len(src_doc)

                # Determine page range
                if merge_input.page_range:
                    start, end = merge_input.page_range.to_fitz_range(src_pages)
                else:
                    start, end = 0, src_pages - 1

                # Insert specified pages
                output_doc.insert_pdf(src_doc, from_page=start, to_page=end)
                pages_added = end - start + 1

                # Collect bookmarks for included pages
                if preserve_bookmarks:
                    src_toc = src_doc.get_toc()
                    for level, title, page in src_toc:
                        # Only include bookmarks for pages in range
                        if start <= page - 1 <= end:
                            adjusted_page = page - start + current_page
                            toc_entries.append([level, title, adjusted_page])

                current_page += pages_added
                total_pages += pages_added
                src_doc.close()

            if toc_entries:
                output_doc.set_toc(toc_entries)

            output_doc.save(output_path, garbage=4, deflate=True)
            output_doc.close()

            output_size = output_path.stat().st_size

            return MergeResult(
                output_path=output_path,
                total_pages=total_pages,
                input_files=len(inputs),
                output_size=output_size,
            )

        except fitz.FileDataError as e:
            raise FileProcessingError(f"Invalid PDF file: {e}")
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise FileProcessingError(f"Failed to merge PDFs: {e}")

    def get_page_count(self, file_path: Path) -> int:
        """
        Get the number of pages in a PDF.

        Args:
            file_path: Path to PDF file

        Returns:
            Number of pages
        """
        try:
            doc = fitz.open(file_path)
            count = len(doc)
            doc.close()
            return count
        except Exception as e:
            raise FileProcessingError(f"Failed to read PDF: {e}")

    def validate_pdf(self, file_path: Path) -> bool:
        """
        Validate that a file is a valid PDF.

        Args:
            file_path: Path to file

        Returns:
            True if valid PDF
        """
        try:
            doc = fitz.open(file_path)
            doc.close()
            return True
        except Exception:
            return False


# Global instance
merge_service = MergeService()


def get_merge_service() -> MergeService:
    """Dependency for getting merge service instance."""
    return merge_service
