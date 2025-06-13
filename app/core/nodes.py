import json
from datetime import datetime
from typing import Dict
from .state import CSPEState, CritereAnalysis
from .prompts import EXTRACT_ENTITIES_PROMPT

def extract_entities(state: CSPEState) -> Dict:
    print("--- Extraction des entités ---")
    try:
        # Simulation de l'appel au LLM
        # À remplacer par un vrai appel à votre modèle
        extracted_data = {
            "date_decision": "15 mars 2024",
            "date_recours": "10 mai 2024",
            "demandeur": "SARL du Pont"
        }
        
        return {
            "extracted_dates": {
                "date_decision": extracted_data["date_decision"],
                "date_recours": extracted_data["date_recours"]
            },
            "extracted_applicant": extracted_data["demandeur"]
        }
    except Exception as e:
        return {"error_message": f"Erreur lors de l'extraction des entités: {e}"}

# Ajoutez les autres fonctions de nœuds ici