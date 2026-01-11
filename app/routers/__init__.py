"""API routers for SlimPDF."""

from app.routers.compress import router as compress_router
from app.routers.merge import router as merge_router
from app.routers.image_to_pdf import router as image_to_pdf_router
from app.routers.jobs import router as jobs_router
from app.routers.auth import router as auth_router
from app.routers.billing import router as billing_router
from app.routers.api_keys import router as api_keys_router

__all__ = [
    "compress_router",
    "merge_router",
    "image_to_pdf_router",
    "jobs_router",
    "auth_router",
    "billing_router",
    "api_keys_router",
]
