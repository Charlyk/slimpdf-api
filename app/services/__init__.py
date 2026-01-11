"""Services for SlimPDF PDF processing."""

from app.services.compression import (
    CompressionService,
    CompressionQuality,
    CompressionResult,
    compression_service,
    get_compression_service,
)
from app.services.merge import (
    MergeService,
    MergeInput,
    MergeResult,
    PageRange,
    merge_service,
    get_merge_service,
)
from app.services.image_convert import (
    ImageConvertService,
    ImageConvertResult,
    PageSize,
    image_convert_service,
    get_image_convert_service,
)
from app.services.file_manager import (
    FileManager,
    file_manager,
    get_file_manager,
)

__all__ = [
    # Compression
    "CompressionService",
    "CompressionQuality",
    "CompressionResult",
    "compression_service",
    "get_compression_service",
    # Merge
    "MergeService",
    "MergeInput",
    "MergeResult",
    "PageRange",
    "merge_service",
    "get_merge_service",
    # Image Convert
    "ImageConvertService",
    "ImageConvertResult",
    "PageSize",
    "image_convert_service",
    "get_image_convert_service",
    # File Manager
    "FileManager",
    "file_manager",
    "get_file_manager",
]
