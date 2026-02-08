"""
GBP Audit Bot API - Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/gbp_check"
    
    # SERP API
    scale_serp_api_key: str = ""
    scale_serp_base_url: str = "https://api.scaleserp.com/search"
    
    # OpenAI (for AI analysis reports)
    openai_api_key: str = ""
    
    # Security
    secret_key: str = "development-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # Grid Settings
    max_grid_size: int = 7
    default_grid_size: int = 5
    max_radius_km: float = 50.0
    
    # Rate Limiting
    serp_batch_size: int = 5  # Process in batches to avoid API blocking
    serp_batch_delay_seconds: float = 0.5
    
    # WhatsApp Gateway (Evolution API / Z-API)
    whatsapp_api_url: str = ""
    whatsapp_api_key: str = ""
    whatsapp_instance_name: str = ""
    
    # Scheduler
    scheduler_timezone: str = "America/Sao_Paulo"
    weekly_report_day: str = "mon"  # monday
    weekly_report_hour: int = 9
    weekly_report_minute: int = 0
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
