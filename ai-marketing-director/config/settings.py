"""Configuration settings for AI Marketing Director"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Core API Keys
    openai_api_key: str

    # Social Media APIs
    linkedin_access_token: Optional[str] = None
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_secret: Optional[str] = None

    # CRM Integration
    crm_api_key: Optional[str] = None
    crm_type: str = "hubspot"  # hubspot or salesforce

    # Analytics
    google_analytics_key: Optional[str] = None

    # Database
    database_url: str = "postgresql://localhost:5432/marketing_director"
    redis_url: str = "redis://localhost:6379"

    # Application Settings
    environment: str = "development"  # development, staging, production
    debug: bool = True

    # Agent Settings
    max_agent_retries: int = 3
    agent_timeout: int = 300  # seconds

    # LLM Settings
    default_model: str = "gpt-5"
    max_tokens: int = 8000
    temperature: float = 0.7

    # Brand Settings
    company_name: str = "AI Elevate"
    company_url: str = "https://ai-elevate.ai"
    brand_voice: str = "professional"  # professional, casual, technical

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
