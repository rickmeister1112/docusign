"""
Application configuration management.
Loads settings from environment variables.
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache
from pydantic import field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Application
    APP_NAME: str = "Feedback CRUD API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security - MUST be set via environment variable
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///./feedback.db"
    
    # CORS (comma-separated string)
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    
    # Pagination limits
    MAX_PAGE_SIZE: int = 100
    DEFAULT_PAGE_SIZE: int = 20
    
    # Password Policy
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_DIGIT: bool = True
    REQUIRE_SPECIAL: bool = False
    
    def get_cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Don't try to parse complex types as JSON from env
        env_parse_enums = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()


# Global settings instance
settings = get_settings()

