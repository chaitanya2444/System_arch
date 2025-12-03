import os
from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Keys
    groq_api_key: str = ""
    huggingface_api_key: str = ""
    
    # Security
    allowed_origins: List[str] = ["http://localhost:3000"]
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Application
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()