# app/services/nlp_service.py
import spacy
from typing import List, Dict, Any

class NLPService:
    def __init__(self):
        self.nlp = spacy.load("fr_core_news_lg")
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extrait les entités nommées d'un texte."""
        doc = self.nlp(text)
        return [
            {"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char}
            for ent in doc.ents
        ]
    
    def analyze_legal_text(self, text: str) -> Dict[str, Any]:
        """Analyse un texte juridique et en extrait des informations clés."""
        doc = self.nlp(text)
        
        # Exemple d'analyse simple
        return {
            "entities": self.extract_entities(text),
            "sentences": [str(sent) for sent in doc.sents],
            "keywords": list({token.lemma_ for token in doc 
                            if not token.is_stop and token.is_alpha and len(token) > 2})
        }

# Instance unique du service
nlp_service = NLPService()