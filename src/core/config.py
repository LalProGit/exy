from __future__ import annotations
import logging
import os
from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError
import json

logger = logging.getLogger(__name__)

class Settings(BaseModel):
    app_name: str = Field(default="EXY bot")
    version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    owner_ids_discord: list[str] = Field(..., min_length=1)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    config_path = Path("config.json")

    if not config_path.exists():
        raise FileNotFoundError("CRITICAL: config.json file not found!")
    
    with open(config_path, "r") as file:
        config_data = json.load(file)

    env_data = dict(
        app_name=os.getenv("APP_NAME", "EXY bot"),
        version=os.getenv("APP_VERSION", "1.0.0"),
        environment=os.getenv("ENVIRONMENT", "development"),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
    )

    merged_data = {**env_data, **config_data}

    try:
        return Settings(**merged_data)
    
    except ValidationError as e:
        logger.critical(f"CRITICAL: Application configuration is invalid or missing required field{e}")
        exit(1)
    


    
