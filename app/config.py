from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str = "sqlite:///./sac_dj.db"
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    
    # Redis
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    
    # Sécurité
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 jours
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "SAC-DJ"
    VERSION: str = "0.1.0"
    
    # Email (optionnel)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "mistral:7b-instruct"
    LLM_TIMEOUT: int = 180
    
    # Admin
    FIRST_ADMIN_EMAIL: str = "admin@conseil-etat.fr"
    FIRST_ADMIN_PASSWORD: str = "changeme-in-production"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignorer les variables non définies
        case_sensitive = True

settings = Settings()