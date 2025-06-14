# app/utils/prompt_utils.py
from typing import Optional
from app.config.prompts import get_prompt
from app.config.config import settings

def get_system_prompt(prompt_name: Optional[str] = None) -> str:
    """
    Récupère un prompt système.
    Si aucun nom n'est fourni, utilise le prompt par défaut de la configuration.
    
    Args:
        prompt_name: Nom du prompt (optionnel)
        
    Returns:
        str: Le contenu du prompt formaté pour une utilisation avec un LLM
    """
    if prompt_name is None:
        prompt_name = settings.DEFAULT_PROMPT
    
    prompt_content = get_prompt(prompt_name)
    return f"""Tu es un expert en analyse de dossiers CSPE. Voici les instructions à suivre :

{prompt_content}

Analyse maintenant le document fourni en respectant scrupuleusement ces instructions."""