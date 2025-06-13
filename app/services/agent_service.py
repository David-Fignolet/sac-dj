from typing import Dict, Any
from app.core.agent.graph import agent_workflow

class AgentService:
    def __init__(self):
        self.workflow = agent_workflow

    async def process_document(self, document_id: str, content: str) -> Dict[str, Any]:
        """Traite un document à travers le workflow de l'agent"""
        try:
            # État initial
            initial_state = {
                "document_id": document_id,
                "document_content": content,
                "is_review_required": False
            }
            
            # Exécution du workflow
            result = await self.workflow.ainvoke(initial_state)
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Erreur lors du traitement du document: {str(e)}"
            }

# Instance unique du service
agent_service = AgentService()