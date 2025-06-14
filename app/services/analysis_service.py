# app/services/analysis_service.py
from app.utils.prompt_utils import get_system_prompt

class AnalysisService:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def analyze_document(self, document_content: str, prompt_name: str = None):
        # Récupérer le prompt système
        system_prompt = get_system_prompt(prompt_name)
        
        # Construire le message pour le LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": document_content}
        ]
        
        # Appeler le LLM
        response = await self.llm.chat_complete(messages)
        return response