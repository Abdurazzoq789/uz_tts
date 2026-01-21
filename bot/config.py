"""
Configuration management for the Uzbek TTS Telegram Bot.
Uses Pydantic for type-safe configuration validation.
"""

import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Config(BaseSettings):
    """Bot configuration loaded from environment variables."""
    
    # Required settings
    bot_token: str = Field(..., description="Telegram bot token from BotFather")
    
    # Optional settings with defaults
    trigger_hashtag: str = Field(
        default="#audio",
        description="Hashtag to trigger TTS conversion"
    )
    max_text_length: int = Field(
        default=4500,
        description="Maximum characters per TTS chunk"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://internation:internation@localhost:5432/uz_tts",
        description="PostgreSQL database URL"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Max database connections overflow")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", description="Redis URL for queue and cache")
    
    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0", description="Celery broker URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/1", description="Celery result backend")
    
    # Payments
    telegram_payment_enabled: bool = Field(default=True, description="Enable Telegram Stars payments")
    manual_payment_enabled: bool = Field(default=True, description="Enable manual card payments")
    manual_payment_card_number: str = Field(default="", description="Card number for manual payments")
    manual_payment_card_holder: str = Field(default="", description="Card holder name")
    
    # Billing
    free_tier_tts_limit: int = Field(default=3, description="Free TTS limit per month (DM)")
    paid_monthly_price: float = Field(default=10.0, description="Monthly subscription price in USD")
    
    # Admin (comma-separated user IDs, e.g., "123456789,987654321")
    admin_user_ids: str = Field(default="", description="Comma-separated admin user IDs")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def get_admin_ids(self) -> list[int]:
        """Parse admin user IDs from comma-separated string."""
        if not self.admin_user_ids:
            return []
        return [int(uid.strip()) for uid in self.admin_user_ids.split(',') if uid.strip()]
    
    @field_validator("trigger_hashtag")
    @classmethod
    def validate_hashtag(cls, v: str) -> str:
        """Ensure hashtag starts with #."""
        if not v.startswith("#"):
            return f"#{v}"
        return v
    
    @field_validator("max_text_length")
    @classmethod
    def validate_max_length(cls, v: int) -> int:
        """Ensure max length is reasonable."""
        if v < 1 or v > 5000:
            raise ValueError("max_text_length must be between 1 and 5000")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper


# Global configuration instance
config: Config | None = None


def get_config() -> Config:
    """Get or create the global configuration instance."""
    global config
    if config is None:
        config = Config()
    return config
