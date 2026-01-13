from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),  # .env.local takes precedence
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    cors_origins: list[str] = ["https://slimpdf.io", "https://dev.slimpdf.io", "http://localhost:3000"]

    # Database
    database_url: str = "postgresql://user:pass@localhost:5432/slimpdf"

    # Authentication
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    # Firebase Authentication
    firebase_credentials_json: str = ""  # JSON string of service account credentials

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_monthly: str = ""
    stripe_price_yearly: str = ""

    # Email (Resend)
    resend_api_key: str = ""

    # File Processing
    temp_file_dir: str = "/tmp/slimpdf"
    file_expiry_free_hours: int = 1
    file_expiry_pro_hours: int = 24
    max_file_size_free_mb: int = 20
    max_file_size_pro_mb: int = 100

    # Rate Limiting (daily limits for free tier)
    rate_limit_compress_free: int = 2
    rate_limit_merge_free: int = 3
    rate_limit_image_to_pdf_free: int = 3

    # Merge limits
    max_files_merge_free: int = 5
    max_files_merge_pro: int = 50

    # Image to PDF limits
    max_images_free: int = 10
    max_images_pro: int = 100


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
