# app/config/prompts.py
from pathlib import Path

# Chemin vers le dossier des prompts
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

# Noms des prompts disponibles
DEFAULT_PROMPT = "cspe_expert_prompt"

def get_prompt(prompt_name: str = None) -> str:
    """
    Récupère le contenu d'un prompt par son nom.
    Si aucun nom n'est fourni, retourne le prompt par défaut.
    
    Args:
        prompt_name: Nom du fichier de prompt (sans l'extension .md)
        
    Returns:
        str: Le contenu du prompt
    """
    if prompt_name is None:
        prompt_name = DEFAULT_PROMPT
    
    prompt_path = PROMPTS_DIR / f"{prompt_name}.md"
    
    try:
        return prompt_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        available = [f.stem for f in PROMPTS_DIR.glob("*.md")]
        raise ValueError(
            f"Prompt '{prompt_name}' non trouvé. "
            f"Prompts disponibles : {', '.join(available)}"
        )