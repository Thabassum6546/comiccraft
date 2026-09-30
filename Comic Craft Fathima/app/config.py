from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    environment: str = "development"
    debug: bool = True

    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-3.8-flash"
    gemini_pro_model: str = "gemini-3.1-pro-preview"

    hf_token: str = ""
    image_model: str = "runwayml/stable-diffusion-v1-5"
    image_provider: str = "huggingface"
    allow_image_fallback: bool = True

    panels_count: int = 5
    image_width: int = 768
    image_height: int = 512
    image_steps: int = 25
    image_guidance: float = 7.5

    model_timeout_seconds: int = 180

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
