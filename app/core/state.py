# app/core/state.py
from typing import List, Optional, Dict, Any, Union
from typing_extensions import TypedDict
from datetime import datetime
from enum import Enum

# ===== ÉNUMÉRATIONS =====

class ProcessingStatus(str, Enum):
    """Statuts de traitement possibles"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ClassificationResult(str, Enum):
    """Résultats de classification possibles"""
    RECEVABLE = "RECEVABLE"
    IRRECEVABLE = "IRRECEVABLE"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"

class ConfidenceLevel(str, Enum):
    """Niveaux de confiance"""
    HIGH = "high"      # > 0.9
    MEDIUM = "medium"  # 0.7 - 0.9  
    LOW = "low"        # < 0.7

# ===== STRUCTURES DE DONNÉES =====

class CritereAnalysis(TypedDict):
    """Résultat de l'analyse d'un critère spécifique"""
    is_compliant: bool                    # Le critère est-il respecté ?
    reasoning: str                        # Explication détaillée
    confidence: float                     # Score de confiance (0.0 à 1.0)
    source_quote: Optional[str]           # Citation du texte source
    criterion_name: Optional[str]         # Nom du critère analysé
    analyzed_at: Optional[str]            # Timestamp de l'analyse
    error: Optional[str]                  # Message d'erreur éventuel

class ExtractedDates(TypedDict):
    """Dates extraites du document"""
    date_decision: Optional[str]          # Date de la décision contestée
    date_recours: Optional[str]           # Date du recours
    date_notification: Optional[str]      # Date de notification (si mentionnée)

class ExtractedEntities(TypedDict):
    """Entités extraites du document juridique"""
    demandeur: Optional[str]              # Nom du demandeur
    objet_recours: Optional[str]          # Objet de la contestation
    montant_conteste: Optional[str]       # Montant financier en jeu
    autorite_competente: Optional[str]    # Autorité ayant pris la décision
    type_decision: Optional[str]          # Type de décision contestée
    numero_dossier: Optional[str]         # Numéro de dossier/référence

class AnalysisSummary(TypedDict):
    """Résumé de l'analyse complète"""
    total_criteria: int                   # Nombre total de critères analysés
    compliant_criteria: int               # Nombre de critères respectés
    average_confidence: float             # Confiance moyenne
    decision_timestamp: str               # Timestamp de la décision
    processing_time_ms: Optional[int]     # Temps de traitement en ms
    successful_analyses: Optional[int]    # Nombre d'analyses réussies
    error: Optional[str]                  # Erreur globale éventuelle

# ===== ÉTAT PRINCIPAL =====

class CSPEState(TypedDict):
    """État global du workflow d'analyse CSPE"""
    
    # ===== DONNÉES INITIALES =====
    document_id: str                      # Identifiant unique du document
    document_content: str                 # Contenu textuel complet du document
    document_metadata: Optional[Dict[str, Any]]  # Métadonnées du document
    
    # ===== ENTITÉS EXTRAITES =====
    extracted_dates: Optional[ExtractedDates]           # Dates importantes extraites
    extracted_applicant: Optional[str]                  # Demandeur principal
    extracted_object: Optional[str]                     # Objet du recours
    extracted_amount: Optional[str]                     # Montant contesté
    extracted_authority: Optional[str]                  # Autorité compétente
    extracted_decision_type: Optional[str]              # Type de décision
    extracted_entities: Optional[ExtractedEntities]     # Toutes les entités extraites
    
    # ===== ANALYSES DES CRITÈRES =====
    deadline_analysis: Optional[CritereAnalysis]        # Analyse du délai
    quality_analysis: Optional[CritereAnalysis]         # Analyse de la qualité pour agir
    object_analysis: Optional[CritereAnalysis]          # Analyse de l'objet du recours
    documents_analysis: Optional[CritereAnalysis]       # Analyse des pièces justificatives
    
    # ===== RÉSULTATS FINAUX =====
    final_classification: Optional[str]                 # Classification finale (RECEVABLE/IRRECEVABLE)
    final_justification: Optional[str]                  # Justification détaillée de la décision
    final_confidence: Optional[float]                   # Score de confiance global
    is_review_required: bool                            # Nécessite-t-il une révision humaine ?
    critical_issues: Optional[List[str]]                # Problèmes critiques identifiés
    
    # ===== MÉTADONNÉES D'ANALYSE =====
    analysis_summary: Optional[AnalysisSummary]         # Résumé de l'analyse
    processing_status: Optional[str]                    # Statut du traitement
    started_at: Optional[str]                           # Timestamp de début
    completed_at: Optional[str]                         # Timestamp de fin
    
    # ===== GESTION D'ERREURS =====
    error_message: Optional[str]                        # Message d'erreur principal
    warnings: Optional[List[str]]                       # Avertissements non bloquants
    debug_info: Optional[Dict[str, Any]]                # Informations de débogage

# ===== ÉTATS ÉTENDUS POUR FONCTIONNALITÉS AVANCÉES =====

class DocumentState(TypedDict):
    """État d'un document dans le système"""
    document_id: str
    title: str
    content: str
    document_type: str
    file_path: Optional[str]
    upload_date: Optional[str]
    processed_date: Optional[str]
    status: str
    metadata: Optional[Dict[str, Any]]

class AnalysisState(TypedDict):
    """État d'une analyse en cours ou terminée"""
    analysis_id: str
    document_id: str
    status: str
    result: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
    assigned_to: Optional[str]
    priority: Optional[str]

class UserContext(TypedDict):
    """Contexte utilisateur pour l'analyse"""
    user_id: str
    username: str
    email: str
    roles: List[str]
    preferences: Dict[str, Any]
    session_id: Optional[str]

class WorkflowState(TypedDict):
    """État global du workflow (pour les cas complexes)"""
    workflow_id: str
    name: str
    description: str
    status: str
    created_at: str
    updated_at: str
    document: Optional[DocumentState]
    analysis: Optional[AnalysisState]
    user_context: Optional[UserContext]
    metadata: Dict[str, Any]

# ===== FONCTIONS UTILITAIRES =====

def create_initial_cspe_state(document_id: str, document_content: str, **kwargs) -> CSPEState:
    """Crée un état CSPE initial avec les valeurs par défaut"""
    return CSPEState(
        # Données obligatoires
        document_id=document_id,
        document_content=document_content,
        
        # Entités extraites (initialement vides)
        extracted_dates=None,
        extracted_applicant=None,
        extracted_object=None,
        extracted_amount=None,
        extracted_authority=None,
        extracted_decision_type=None,
        extracted_entities=None,
        
        # Analyses (initialement vides)
        deadline_analysis=None,
        quality_analysis=None,
        object_analysis=None,
        documents_analysis=None,
        
        # Résultats (initialement vides)
        final_classification=None,
        final_justification=None,
        final_confidence=None,
        is_review_required=True,  # Par défaut, révision requise
        critical_issues=None,
        
        # Métadonnées
        analysis_summary=None,
        processing_status=ProcessingStatus.PENDING.value,
        started_at=datetime.utcnow().isoformat(),
        completed_at=None,
        
        # Gestion d'erreurs
        error_message=None,
        warnings=None,
        debug_info=None,
        
        # Métadonnées optionnelles
        document_metadata=kwargs.get("document_metadata", None)
    )

def get_confidence_level(confidence: float) -> ConfidenceLevel:
    """Détermine le niveau de confiance basé sur le score"""
    if confidence >= 0.9:
        return ConfidenceLevel.HIGH
    elif confidence >= 0.7:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW

def calculate_overall_confidence(state: CSPEState) -> float:
    """Calcule la confiance globale basée sur les analyses individuelles"""
    analyses = [
        state.get("deadline_analysis"),
        state.get("quality_analysis"),
        state.get("object_analysis"),
        state.get("documents_analysis")
    ]
    
    valid_confidences = [
        analysis.get("confidence", 0.0)
        for analysis in analyses
        if analysis and isinstance(analysis.get("confidence"), (int, float))
    ]
    
    if not valid_confidences:
        return 0.0
    
    return sum(valid_confidences) / len(valid_confidences)

def is_analysis_complete(state: CSPEState) -> bool:
    """Vérifie si l'analyse est complète"""
    required_analyses = ["deadline_analysis", "quality_analysis", "object_analysis", "documents_analysis"]
    
    for analysis_key in required_analyses:
        analysis = state.get(analysis_key)
        if not analysis or analysis.get("error"):
            return False
    
    return bool(state.get("final_classification"))

def get_analysis_errors(state: CSPEState) -> List[str]:
    """Retourne la liste des erreurs d'analyse"""
    errors = []
    
    # Erreur globale
    if state.get("error_message"):
        errors.append(state["error_message"])
    
    # Erreurs d'analyses individuelles
    analyses = [
        ("deadline_analysis", "Analyse des délais"),
        ("quality_analysis", "Analyse de la qualité"),
        ("object_analysis", "Analyse de l'objet"),
        ("documents_analysis", "Analyse des documents")
    ]
    
    for key, name in analyses:
        analysis = state.get(key)
        if analysis and analysis.get("error"):
            errors.append(f"{name}: {analysis['error']}")
    
    return errors

def update_state_with_timing(state: CSPEState, status: str) -> CSPEState:
    """Met à jour l'état avec les informations de timing"""
    updated_state = state.copy()
    updated_state["processing_status"] = status
    
    if status == ProcessingStatus.COMPLETED.value:
        updated_state["completed_at"] = datetime.utcnow().isoformat()
    
    return updated_state