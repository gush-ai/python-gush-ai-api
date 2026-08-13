# File: app/config.py
from pydantic import BaseSettings, Field, validator
from typing import Literal

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    GITHUB_TOKEN: str = Field(..., env="GITHUB_TOKEN", description="GitHub personal access token")
    GITHUB_ORG: str = Field(..., env="GITHUB_ORG", description="GitHub organization or username")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        "INFO", env="LOG_LEVEL", description="Logging level"
    )
    GITHUB_API_URL: str = Field(
        "https://api.github.com", env="GITHUB_API_URL", description="Base URL for GitHub API"
    )

    @validator("GITHUB_TOKEN")
    def _non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("GITHUB_TOKEN cannot be empty")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Export a singleton for import elsewhere
settings = Settings()