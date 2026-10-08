from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_provider: Literal["ollama", "openai_compatible", "mock"] = "ollama"
    llm_model: str = "mistral"
    llm_base_url: str = "http://localhost:11434"
    llm_api_key: str = ""
    max_upload_bytes: int = Field(default=5 * 1024 * 1024, ge=1024, le=20 * 1024 * 1024)
    max_documents: int = Field(default=100, ge=1, le=1000)
    top_k: int = Field(default=4, ge=1, le=10)
    upload_dir: Path = Path("data/uploads")


@lru_cache
def get_settings() -> Settings:
    return Settings()

