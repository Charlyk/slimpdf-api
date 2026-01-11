"""SlimPDF API - FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db, close_db
from app.routers import (
    compress_router,
    merge_router,
    image_to_pdf_router,
    jobs_router,
    auth_router,
    billing_router,
    api_keys_router,
)
from app.services.file_manager import file_manager

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    # Ensure temp directories exist
    Path(settings.temp_file_dir).mkdir(parents=True, exist_ok=True)
    (Path(settings.temp_file_dir) / "uploads").mkdir(exist_ok=True)
    (Path(settings.temp_file_dir) / "processed").mkdir(exist_ok=True)

    # Initialize database (create tables if needed)
    # Note: In production, use Alembic migrations instead
    # await init_db()

    yield

    # Shutdown
    # Close database connections
    await close_db()

    # Optional: Clean up old files on shutdown
    # file_manager.cleanup_expired_files(max_age_hours=24)


# Create FastAPI application
app = FastAPI(
    title="SlimPDF API",
    description="Server-side PDF toolkit for compression, merging, and image-to-PDF conversion.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(compress_router)
app.include_router(merge_router)
app.include_router(image_to_pdf_router)
app.include_router(jobs_router)
app.include_router(auth_router)
app.include_router(billing_router)
app.include_router(api_keys_router)


@app.get("/", tags=["health"])
async def root():
    """Root endpoint - API information."""
    return {
        "name": "SlimPDF API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "slimpdf-api",
    }


# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
