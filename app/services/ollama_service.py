# app/services/ollama_service.py
import httpx
import json
import asyncio
from typing import Dict, Any, Optional, List
from app.config import settings
import logging
import time

logger = logging.getLogger(__name__)

class OllamaService:
    """Service pour interagir avec Ollama et le modèle Mistral"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT
        self._client = None
        
    async def _get_client(self):
        """Obtient un client HTTP réutilisable"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
        
    async def close(self):
        """Ferme le client HTTP"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def health_check(self) -> bool:
        """Vérifie que Ollama fonctionne"""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def is_model_available(self) -> bool:
        """Vérifie si le modèle Mistral est disponible"""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                logger.info(f"Modèles disponibles: {available_models}")
                return any(self.model in model for model in available_models)
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du modèle: {e}")
            return False
    
    async def pull_model_if_needed(self) -> bool:
        """Télécharge le modèle s'il n'est pas disponible"""
        if await self.is_model_available():
            return True
            
        logger.info(f"Téléchargement du modèle {self.model}...")
        try:
            client = await self._get_client()
            response = await client.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model},
                timeout=600  # 10 minutes pour le téléchargement
            )
            
            if response.status_code == 200:
                logger.info(f"Modèle {self.model} téléchargé avec succès")
                return True
            else:
                logger.error(f"Erreur lors du téléchargement: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement du modèle: {e}")
            return False
    
    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """Génère une completion avec Mistral via Ollama"""
        
        # Vérifier et télécharger le modèle si nécessaire
        if not await self.pull_model_if_needed():
            raise RuntimeError(f"Le modèle {self.model} n'est pas disponible et n'a pas pu être téléchargé")
        
        # Préparer le prompt complet
        if system_prompt:
            full_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>\n"
        else:
            full_prompt = prompt
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": max_tokens,
                "stop": ["</s>", "<|end|>"]
            }
        }
        
        start_time = time.time()
        try:
            client = await self._get_client()
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Erreur Ollama: {response.status_code} - {response.text}")
            
            result = response.json()
            processing_time = time.time() - start_time
            
            logger.info(f"Génération terminée en {processing_time:.2f}s")
            
            return {
                "response": result.get("response", "").strip(),
                "model": result.get("model", ""),
                "created_at": result.get("created_at", ""),
                "done": result.get("done", False),
                "total_duration": result.get("total_duration", 0),
                "load_duration": result.get("load_duration", 0),
                "prompt_eval_count": result.get("prompt_eval_count", 0),
                "eval_count": result.get("eval_count", 0),
                "processing_time": processing_time
            }
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération: {e}")
            raise RuntimeError(f"Impossible de générer la réponse: {str(e)}")
    
    def _extract_json_from_response(self, response_text: str) -> dict:
        """Extrait et parse le JSON d'une réponse LLM"""
        try:
            # Nettoyer la réponse
            cleaned = response_text.strip()
            
            # Tenter de parser directement
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass
            
            # Chercher un JSON dans le texte
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, cleaned, re.DOTALL)
            
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
            
            # Chercher entre des délimiteurs markdown
            code_blocks = re.findall(r'```(?:json)?\n?(.*?)\n?```', cleaned, re.DOTALL)
            for block in code_blocks:
                try:
                    return json.loads(block.strip())
                except json.JSONDecodeError:
                    continue
            
            raise ValueError("Aucun JSON valide trouvé dans la réponse")
            
        except Exception as e:
            logger.warning(f"Impossible de parser JSON: {e}")
            raise
    
    async def extract_entities_with_llm(self, document_content: str) -> Dict[str, Any]:
        """Extrait les entités du document avec Mistral"""
        
        system_prompt = """Tu es un expert en analyse de documents juridiques français. 
        Tu dois extraire les informations clés des recours CSPE avec une précision maximale.
        Réponds UNIQUEMENT avec un JSON valide, sans texte supplémentaire."""
        
        prompt = f"""
Analyse ce document juridique et extrais les informations suivantes :

DOCUMENT :
---
{document_content[:3000]}...  
---

Extrais ces informations (utilise null si introuvable) :

{{
  "date_decision": "date de la décision contestée (format DD/MM/YYYY)",
  "date_recours": "date du recours (format DD/MM/YYYY)", 
  "demandeur": "nom du demandeur",
  "objet_recours": "objet de la contestation",
  "montant_conteste": "montant contesté en euros",
  "autorite_competente": "autorité qui a pris la décision",
  "type_decision": "type de décision contestée"
}}

Réponds uniquement avec le JSON, sans explication.
"""
        
        try:
            result = await self.generate_completion(prompt, system_prompt, temperature=0.1)
            response_text = result["response"]
            
            return self._extract_json_from_response(response_text)
                    
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction d'entités: {e}")
            return {
                "date_decision": None,
                "date_recours": None,
                "demandeur": None,
                "objet_recours": None,
                "montant_conteste": None,
                "autorite_competente": None,
                "type_decision": None,
                "error": str(e)
            }
    
    async def analyze_criterion(
        self, 
        criterion_name: str,
        document_content: str, 
        extracted_entities: Dict[str, Any],
        criterion_description: str
    ) -> Dict[str, Any]:
        """Analyse un critère spécifique avec Mistral"""
        
        system_prompt = f"""Tu es un expert juridique spécialisé dans l'analyse des recours CSPE.
        Analyse le critère '{criterion_name}' avec rigueur et objectivité.
        Réponds UNIQUEMENT avec un JSON valide."""
        
        prompt = f"""
CRITÈRE À ANALYSER : {criterion_name}

RÈGLE JURIDIQUE :
{criterion_description}

ENTITÉS EXTRAITES :
{json.dumps(extracted_entities, indent=2, ensure_ascii=False)}

DOCUMENT (extrait) :
---
{document_content[:2000]}...
---

Analyse si ce critère est respecté selon les règles CSPE.

Réponds avec ce JSON exact :
{{
  "is_compliant": true/false,
  "reasoning": "Explication détaillée de ton analyse en 2-3 phrases",
  "confidence": 0.XX,
  "source_quote": "Citation exacte du document qui justifie ta décision ou null"
}}
"""
        
        try:
            result = await self.generate_completion(prompt, system_prompt, temperature=0.1)
            response_text = result["response"]
            
            return self._extract_json_from_response(response_text)
                    
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du critère {criterion_name}: {e}")
            return {
                "is_compliant": False,
                "reasoning": f"Erreur lors de l'analyse: {str(e)}",
                "confidence": 0.0,
                "source_quote": None
            }

    async def make_final_decision(self, analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Prend la décision finale basée sur l'analyse des 4 critères"""
        
        system_prompt = """Tu es un expert juridique du Conseil d'État. 
        Prends une décision finale de recevabilité basée sur l'analyse des 4 critères CSPE.
        Réponds UNIQUEMENT avec un JSON valide."""
        
        prompt = f"""
ANALYSES DES 4 CRITÈRES CSPE :
{json.dumps(analyses, indent=2, ensure_ascii=False)}

RÈGLE DE DÉCISION :
- RECEVABLE : TOUS les critères doivent être respectés
- IRRECEVABLE : AU MOINS UN critère non respecté

Analyse et décide :

{{
  "final_classification": "RECEVABLE" ou "IRRECEVABLE",
  "final_justification": "Justification détaillée de la décision en 3-4 phrases",
  "final_confidence": 0.XX,
  "is_review_required": true/false,
  "critical_issues": ["liste des problèmes majeurs ou vide si aucun"]
}}
"""
        
        try:
            result = await self.generate_completion(prompt, system_prompt, temperature=0.1)
            response_text = result["response"]
            
            return self._extract_json_from_response(response_text)
                    
        except Exception as e:
            logger.error(f"Erreur lors de la décision finale: {e}")
            return {
                "final_classification": "IRRECEVABLE",
                "final_justification": f"Erreur lors de l'analyse: {str(e)}",
                "final_confidence": 0.0,
                "is_review_required": True,
                "critical_issues": ["Erreur technique lors de l'analyse"]
            }

# Instance unique du service
ollama_service = OllamaService()