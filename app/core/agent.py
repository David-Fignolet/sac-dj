from typing import Dict, Any, List, Optional, Callable, Awaitable, Union
import asyncio
import logging
from uuid import uuid4
from datetime import datetime

from .state import WorkflowState, ProcessingStatus, DocumentState, AnalysisState, UserContext
from .graph import WorkflowGraph, create_default_workflow
from .prompts import prompt_manager

logger = logging.getLogger(__name__)

class AgentMessage:
    """Classe de base pour les messages échangés avec l'agent"""
    
    def __init__(self, 
                 content: Any, 
                 message_type: str = "text", 
                 metadata: Optional[Dict[str, Any]] = None):
        self.id = str(uuid4())
        self.timestamp = datetime.utcnow()
        self.content = content
        self.message_type = message_type  # text, document, analysis, error, etc.
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le message en dictionnaire"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "message_type": self.message_type,
            "metadata": self.metadata
        }

class AgentResponse:
    """Réponse de l'agent après exécution d'une commande"""
    
    def __init__(self, 
                 success: bool = True, 
                 message: str = "", 
                 data: Optional[Dict[str, Any]] = None,
                 messages: Optional[List[Dict[str, Any]]] = None):
        self.success = success
        self.message = message
        self.data = data or {}
        self.messages = messages or []
    
    def add_message(self, message: Union[Dict[str, Any], AgentMessage]) -> None:
        """Ajoute un message à la réponse"""
        if isinstance(message, AgentMessage):
            self.messages.append(message.to_dict())
        else:
            self.messages.append(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la réponse en dictionnaire"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "messages": self.messages
        }

class Agent:
    """Agent principal pour l'analyse de documents juridiques"""
    
    def __init__(self, 
                 workflow: Optional[WorkflowGraph] = None,
                 config: Optional[Dict[str, Any]] = None):
        """Initialise l'agent avec un workflow et une configuration"""
        self.workflow = workflow or create_default_workflow()
        self.config = config or {}
        self.state: Optional[WorkflowState] = None
        self._callbacks: List[Callable[[Dict[str, Any]], Awaitable[None]]] = []
    
    async def initialize(self) -> None:
        """Initialise l'agent"""
        logger.info("Initialisation de l'agent...")
        # Ici, on pourrait charger des modèles, des ressources, etc.
        logger.info("Agent initialisé")
    
    async def analyze_document(
        self, 
        document_content: str,
        document_title: str = "Document sans titre",
        document_type: str = "document_juridique",
        user_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Analyse un document juridique en utilisant le workflow défini
        
        Args:
            document_content: Contenu du document à analyser
            document_title: Titre du document
            document_type: Type de document (jugement, loi, contrat, etc.)
            user_context: Contexte utilisateur (id, rôles, etc.)
            metadata: Métadonnées supplémentaires
            
        Returns:
            AgentResponse: Réponse contenant le résultat de l'analyse
        """
        response = AgentResponse(
            message=f"Début de l'analyse du document: {document_title}"
        )
        
        try:
            # Crée l'état initial du workflow
            self.state = WorkflowState(
                workflow_id=str(uuid4()),
                name="analyse_document_juridique",
                description=f"Analyse du document: {document_title}",
                metadata=metadata or {}
            )
            
            # Initialise le document
            self.state.document = DocumentState(
                document_id=str(uuid4()),
                title=document_title,
                content=document_content,
                document_type=document_type,
                metadata={"source": "api"}
            )
            
            # Initialise l'analyse
            self.state.analysis = AnalysisState(
                analysis_id=str(uuid4()),
                document_id=self.state.document.document_id
            )
            
            # Initialise le contexte utilisateur
            if user_context:
                self.state.user_context = UserContext(
                    user_id=user_context.get("user_id", "anonymous"),
                    username=user_context.get("username", "anonymous"),
                    email=user_context.get("email", ""),
                    roles=user_context.get("roles", []),
                    preferences=user_context.get("preferences", {})
                )
            
            # Exécute le workflow
            logger.info(f"Exécution du workflow pour le document: {document_title}")
            self.state = await self.workflow.execute(self.state)
            
            # Prépare la réponse
            if self.state.status == ProcessingStatus.COMPLETED:
                response.success = True
                response.message = "Analyse terminée avec succès"
                response.data = {
                    "analysis_id": self.state.analysis.analysis_id,
                    "document_id": self.state.document.document_id,
                    "status": "completed",
                    "result": self.state.analysis.result,
                    "metadata": self.state.metadata
                }
            else:
                response.success = False
                response.message = f"Échec de l'analyse: {self.state.metadata.get('error', 'Raison inconnue')}"
                response.data = {
                    "status": "failed",
                    "error": self.state.metadata.get("error"),
                    "execution_path": self.state.metadata.get("execution_path", [])
                }
            
            # Ajoute un message de journal
            response.add_message(AgentMessage(
                content=response.message,
                message_type="analysis_result",
                metadata={
                    "analysis_id": self.state.analysis.analysis_id,
                    "document_id": self.state.document.document_id,
                    "status": self.state.status.value
                }
            ))
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du document: {str(e)}", exc_info=True)
            response.success = False
            response.message = f"Erreur lors de l'analyse du document: {str(e)}"
            
            # Ajoute un message d'erreur
            response.add_message(AgentMessage(
                content=response.message,
                message_type="error",
                metadata={
                    "error": str(e),
                    "error_type": e.__class__.__name__
                }
            ))
        
        return response
    
    async def get_analysis_status(self, analysis_id: str) -> AgentResponse:
        """Récupère le statut d'une analyse"""
        if not self.state or self.state.analysis.analysis_id != analysis_id:
            return AgentResponse(
                success=False,
                message=f"Aucune analyse trouvée avec l'ID: {analysis_id}"
            )
        
        return AgentResponse(
            success=True,
            message="Statut de l'analyse récupéré avec succès",
            data={
                "analysis_id": self.state.analysis.analysis_id,
                "status": self.state.analysis.status,
                "document_id": self.state.document.document_id if self.state.document else None,
                "created_at": self.state.created_at.isoformat(),
                "updated_at": self.state.updated_at.isoformat(),
                "metadata": self.state.metadata
            }
        )
    
    async def cancel_analysis(self, analysis_id: str) -> AgentResponse:
        """Annule une analyse en cours"""
        if not self.state or self.state.analysis.analysis_id != analysis_id:
            return AgentResponse(
                success=False,
                message=f"Aucune analyse trouvée avec l'ID: {analysis_id}"
            )
        
        if self.state.analysis.status == ProcessingStatus.COMPLETED:
            return AgentResponse(
                success=False,
                message="Impossible d'annuler une analyse déjà terminée"
            )
        
        self.state.analysis.status = ProcessingStatus.CANCELLED
        return AgentResponse(
            success=True,
            message=f"Analyse {analysis_id} annulée avec succès"
        )
    
    def register_callback(self, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Enregistre une fonction de rappel pour les événements de l'agent"""
        self._callbacks.append(callback)
    
    async def _notify_callbacks(self, event: str, data: Dict[str, Any]) -> None:
        """Notifie tous les callbacks enregistrés"""
        if not self._callbacks:
            return
            
        event_data = {
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        # Exécute les callbacks en parallèle
        await asyncio.gather(
            *(callback(event_data) for callback in self._callbacks),
            return_exceptions=True
        )
    
    async def close(self) -> None:
        """Nettoie les ressources de l'agent"""
        logger.info("Nettoyage des ressources de l'agent...")
        self.state = None
        self._callbacks.clear()
        logger.info("Ressources de l'agent nettoyées")
