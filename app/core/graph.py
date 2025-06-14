# app/core/graph.py
from langgraph.graph import StateGraph, END
from .state import CSPEState
from .nodes import (
    extract_entities,
    analyze_deadline_criterion,
    analyze_quality_criterion,
    analyze_object_criterion,
    analyze_documents_criterion,
    make_final_decision,
    analyze_all_criteria_parallel
)
import logging

logger = logging.getLogger(__name__)

def should_continue_after_extraction(state: CSPEState) -> str:
    """Détermine si on peut continuer après l'extraction d'entités"""
    if state.get("error_message"):
        logger.error(f"Erreur détectée: {state['error_message']}")
        return "error"
    
    # Vérifier qu'on a au moins quelques entités extraites
    extracted_applicant = state.get("extracted_applicant")
    extracted_dates = state.get("extracted_dates", {})
    
    if not extracted_applicant and not any(extracted_dates.values()):
        logger.warning("Extraction d'entités insuffisante")
        return "insufficient_data"
    
    return "continue"

def should_continue_after_analysis(state: CSPEState) -> str:
    """Détermine si on peut faire la décision finale après les analyses"""
    if state.get("error_message"):
        return "error"
    
    # Vérifier qu'on a au moins 3 analyses sur 4
    analyses = [
        state.get("deadline_analysis"),
        state.get("quality_analysis"),
        state.get("object_analysis"),
        state.get("documents_analysis")
    ]
    
    valid_analyses = sum(1 for analysis in analyses if analysis and not analysis.get("error"))
    
    if valid_analyses < 3:
        logger.warning(f"Seulement {valid_analyses}/4 analyses valides")
        return "insufficient_analysis"
    
    return "continue"

def create_cspe_workflow() -> StateGraph:
    """Crée le workflow LangGraph pour l'analyse CSPE"""
    
    # Créer le graphe avec l'état CSPE
    workflow = StateGraph(CSPEState)
    
    # ===== AJOUT DES NŒUDS =====
    
    # Nœud d'extraction d'entités
    workflow.add_node("extract_entities", extract_entities)
    
    # Nœuds d'analyse des critères (peuvent être exécutés en parallèle)
    workflow.add_node("analyze_deadline", analyze_deadline_criterion)
    workflow.add_node("analyze_quality", analyze_quality_criterion)
    workflow.add_node("analyze_object", analyze_object_criterion)
    workflow.add_node("analyze_documents", analyze_documents_criterion)
    
    # Alternative: analyse parallèle des 4 critères
    workflow.add_node("analyze_all_parallel", analyze_all_criteria_parallel)
    
    # Nœud de décision finale
    workflow.add_node("make_decision", make_final_decision)
    
    # Nœuds de gestion d'erreurs
    workflow.add_node("handle_extraction_error", handle_extraction_error)
    workflow.add_node("handle_analysis_error", handle_analysis_error)
    
    # ===== CONFIGURATION DU FLUX =====
    
    # Point d'entrée: extraction d'entités
    workflow.set_entry_point("extract_entities")
    
    # Après extraction: vérifier si on peut continuer
    workflow.add_conditional_edges(
        "extract_entities",
        should_continue_after_extraction,
        {
            "continue": "analyze_all_parallel",  # Utilise l'analyse parallèle pour plus d'efficacité
            "insufficient_data": "handle_extraction_error",
            "error": "handle_extraction_error"
        }
    )
    
    # Alternative: flux séquentiel (plus lent mais plus robuste)
    # workflow.add_edge("extract_entities", "analyze_deadline")
    # workflow.add_edge("analyze_deadline", "analyze_quality")  
    # workflow.add_edge("analyze_quality", "analyze_object")
    # workflow.add_edge("analyze_object", "analyze_documents")
    # workflow.add_edge("analyze_documents", "make_decision")
    
    # Après analyse parallèle: décision finale
    workflow.add_conditional_edges(
        "analyze_all_parallel",
        should_continue_after_analysis,
        {
            "continue": "make_decision",
            "insufficient_analysis": "handle_analysis_error",
            "error": "handle_analysis_error"
        }
    )
    
    # Fin du workflow après décision
    workflow.add_edge("make_decision", END)
    
    # Gestion d'erreurs mène à la fin
    workflow.add_edge("handle_extraction_error", END)
    workflow.add_edge("handle_analysis_error", END)
    
    return workflow

# ===== NŒUDS DE GESTION D'ERREURS =====

async def handle_extraction_error(state: CSPEState) -> dict:
    """Gère les erreurs d'extraction d'entités"""
    logger.error("❌ Gestion d'erreur d'extraction")
    
    error_message = state.get("error_message", "Erreur inconnue lors de l'extraction")
    
    return {
        "final_classification": "IRRECEVABLE", 
        "final_justification": f"Impossible d'analyser le document: {error_message}",
        "final_confidence": 0.0,
        "is_review_required": True,
        "critical_issues": ["Erreur technique", "Document illisible ou malformé"],
        "analysis_summary": {
            "total_criteria": 4,
            "compliant_criteria": 0,
            "average_confidence": 0.0,
            "error": error_message
        }
    }

async def handle_analysis_error(state: CSPEState) -> dict:
    """Gère les erreurs d'analyse des critères"""
    logger.error("❌ Gestion d'erreur d'analyse")
    
    error_message = state.get("error_message", "Erreur lors de l'analyse des critères")
    
    # Compter les analyses réussies
    analyses = [
        state.get("deadline_analysis"),
        state.get("quality_analysis"),
        state.get("object_analysis"), 
        state.get("documents_analysis")
    ]
    
    successful_analyses = sum(1 for analysis in analyses if analysis and not analysis.get("error"))
    
    return {
        "final_classification": "IRRECEVABLE",
        "final_justification": f"Analyse incomplète ({successful_analyses}/4 critères analysés): {error_message}",
        "final_confidence": 0.0,
        "is_review_required": True,
        "critical_issues": ["Erreur technique", "Analyse incomplète"],
        "analysis_summary": {
            "total_criteria": 4,
            "compliant_criteria": 0,
            "average_confidence": 0.0,
            "successful_analyses": successful_analyses,
            "error": error_message
        }
    }

# ===== CRÉATION DU WORKFLOW COMPILÉ =====

def create_compiled_workflow():
    """Crée et compile le workflow pour utilisation"""
    try:
        workflow = create_cspe_workflow()
        compiled = workflow.compile()
        logger.info("✅ Workflow CSPE compilé avec succès")
        return compiled
    except Exception as e:
        logger.error(f"❌ Erreur lors de la compilation du workflow: {e}")
        raise

# Instance du workflow compilé (singleton)
compiled_workflow = None

def get_compiled_workflow():
    """Retourne l'instance compilée du workflow (singleton)"""
    global compiled_workflow
    if compiled_workflow is None:
        compiled_workflow = create_compiled_workflow()
    return compiled_workflow

# ===== FONCTIONS UTILITAIRES =====

async def execute_cspe_analysis(document_id: str, document_content: str) -> dict:
    """Fonction principale pour exécuter une analyse CSPE complète"""
    logger.info(f"🚀 Début de l'analyse CSPE pour le document {document_id}")
    
    # État initial
    initial_state = CSPEState(
        document_id=document_id,
        document_content=document_content,
        extracted_dates=None,
        extracted_applicant=None,
        deadline_analysis=None,
        quality_analysis=None,
        object_analysis=None,
        documents_analysis=None,
        final_classification=None,
        final_justification=None,
        final_confidence=None,
        is_review_required=True,
        error_message=None
    )
    
    try:
        # Obtenir le workflow compilé
        workflow = get_compiled_workflow()
        
        # Exécuter le workflow
        final_state = await workflow.ainvoke(initial_state)
        
        logger.info(f"✅ Analyse CSPE terminée pour le document {document_id}")
        logger.info(f"📊 Résultat: {final_state.get('final_classification', 'UNKNOWN')}")
        
        return final_state
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution de l'analyse: {e}", exc_info=True)
        return {
            **initial_state,
            "final_classification": "IRRECEVABLE",
            "final_justification": f"Erreur système lors de l'analyse: {str(e)}",
            "final_confidence": 0.0,
            "is_review_required": True,
            "error_message": str(e)
        }

def get_workflow_graph_visualization():
    """Retourne une représentation du graphe pour debugging/visualisation"""
    try:
        workflow = create_cspe_workflow()
        return {
            "nodes": [
                "extract_entities",
                "analyze_deadline", 
                "analyze_quality",
                "analyze_object", 
                "analyze_documents",
                "analyze_all_parallel",
                "make_decision",
                "handle_extraction_error",
                "handle_analysis_error"
            ],
            "edges": [
                ("extract_entities", "analyze_all_parallel"),
                ("analyze_all_parallel", "make_decision"),
                ("make_decision", "END")
            ],
            "conditional_edges": [
                ("extract_entities", ["continue", "insufficient_data", "error"]),
                ("analyze_all_parallel", ["continue", "insufficient_analysis", "error"])
            ]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la visualisation: {e}")
        return {"error": str(e)}