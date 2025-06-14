# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Configuration de l'application
    APP_NAME: str = "SAC-DJ"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Configuration de sécurité
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-very-important")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Base de données (SQLite par défaut pour développement Windows)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sac_dj.db")
    
    # Redis (optionnel pour développement)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    
    # Configuration Ollama
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "mistral:7b-instruct")
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "180"))
    
    # Configuration LLM avancée
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    LLM_TOP_P: float = float(os.getenv("LLM_TOP_P", "0.9"))
    LLM_TOP_K: int = int(os.getenv("LLM_TOP_K", "40"))
    
    # Modèles alternatifs
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", "mistral:7b-instruct")
    
    # Configuration de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "sac_dj.log")
    
    # Configuration des uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "txt", "docx", "doc"]
    
    # Configuration de l'utilisateur admin par défaut
    FIRST_ADMIN_EMAIL: str = os.getenv("FIRST_ADMIN_EMAIL", "admin@test.com")
    FIRST_ADMIN_PASSWORD: str = os.getenv("FIRST_ADMIN_PASSWORD", "admin123")
    
    # Configuration CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",  # Streamlit
        "http://localhost:3000",  # React dev
        "http://127.0.0.1:8501",
        "http://127.0.0.1:3000"
    ]
    
    # Configuration des critères CSPE
    CSPE_CRITERIA: dict = {
        "deadline": {
            "name": "Respect des délais",
            "description": "Le recours doit être formé dans un délai de 2 mois à compter de la notification de la décision contestée.",
            "weight": 1.0
        },
        "quality": {
            "name": "Qualité pour agir", 
            "description": "Le demandeur doit avoir qualité pour agir (intérêt direct et personnel).",
            "weight": 1.0
        },
        "object": {
            "name": "Objet du recours",
            "description": "L'objet du recours doit être clairement défini et porter sur une décision administrative susceptible de recours.",
            "weight": 1.0
        },
        "documents": {
            "name": "Pièces justificatives",
            "description": "Le recours doit être accompagné des pièces justificatives nécessaires.",
            "weight": 1.0
        }
    }
    
    # Configuration des seuils de confiance
    CONFIDENCE_THRESHOLDS: dict = {
        "high": 0.9,      # Décision automatique possible
        "medium": 0.7,    # Validation humaine recommandée
        "low": 0.5        # Révision humaine obligatoire
    }
    
    # Configuration du cache
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 heure
    
    # Configuration de développement
    ENABLE_MOCK_LLM: bool = os.getenv("ENABLE_MOCK_LLM", "false").lower() == "true"
    MOCK_RESPONSES: bool = os.getenv("MOCK_RESPONSES", "false").lower() == "true"
    
    @property
    def is_sqlite(self) -> bool:
        """Vérifie si on utilise SQLite"""
        return self.DATABASE_URL.startswith("sqlite")
    
    @property
    def is_development(self) -> bool:
        """Vérifie si on est en développement"""
        return self.DEBUG or "localhost" in self.OLLAMA_BASE_URL
    
    def get_database_args(self) -> dict:
        """Retourne les arguments de configuration pour SQLAlchemy"""
        if self.is_sqlite:
            return {"check_same_thread": False}
        return {}
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Instance des paramètres
settings = Settings()

# Configuration du logging
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        },
        'detailed': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s (%(filename)s:%(lineno)d): %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': settings.LOG_LEVEL,
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': settings.LOG_LEVEL,
            'formatter': 'detailed',
            'filename': settings.LOG_FILE,
            'mode': 'a',
        }
    },
    'loggers': {
        '': {  # root logger
            'level': settings.LOG_LEVEL,
            'handlers': ['console', 'file'] if not settings.DEBUG else ['console']
        },
        'ollama_service': {
            'level': 'DEBUG' if settings.DEBUG else 'INFO',
            'handlers': ['console', 'file'] if not settings.DEBUG else ['console'],
            'propagate': False
        },
        'langgraph': {
            'level': 'INFO',
            'handlers': ['console', 'file'] if not settings.DEBUG else ['console'],
            'propagate': False
        }
    }
}

# Configuration automatique du logging
logging.config.dictConfig(LOGGING_CONFIG)