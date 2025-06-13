from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Configuration de l'application
    APP_NAME: str = "SAC-DJ"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Configuration de sécurité
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 jours
    
    # Base de données
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sac_dj.db")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    class Config:
        case_sensitive = True

# Instance des paramètres
settings = Settings()