"""
Application configuration settings
"""

from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Kudwa Financial AI System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 4000

    # Anthropic (Alternative)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"

    # Agno Framework Configuration
    AGNO_CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    AGNO_OPENAI_MODEL: str = "gpt-4o"
    AGNO_REASONING_ENABLED: bool = True
    AGNO_MULTI_MODAL: bool = True

    # Google Cloud (for LangExtract)
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # Database
    DATABASE_URL: Optional[str] = None
    TEST_DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["application/json", "text/csv", "application/pdf"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # n8n Integration
    N8N_WEBHOOK_BASE_URL: str = "http://localhost:5678/webhook"
    N8N_API_KEY: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"
    }


# Global settings instance
settings = Settings()
