# app/config/config.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # ... autres paramètres existants ...
    
    # Configuration des prompts
    DEFAULT_PROMPT: str = "cspe_expert_prompt"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Créer l'instance settings
settings = Settings()