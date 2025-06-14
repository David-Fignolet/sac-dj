# app/core/nodes.py
import json
import asyncio
from datetime import datetime
from typing import Dict, Any
from .state import CSPEState
from app.services.ollama_service import ollama_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)

async def extract_entities(state: CSPEState) -> Dict[str, Any]:
    """Extraction des entités avec Ollama/Mistral"""
    logger.info("🔍 --- Début extraction des entités ---")
    
    try:
        # Vérification des prérequis
        if not state.get("document_content"):
            logger.error("Contenu du document manquant")
            return {"error_message": "Contenu du document manquant"}
        
        # Extraction avec le service Ollama
        logger.info("📡 Appel à Mistral pour extraction d'entités...")
        extracted_data = await ollama_service.extract_entities_with_llm(
            state["document_content"]
        )
        
        # Vérification des erreurs
        if "error" in extracted_data:
            logger.error(f"Erreur LLM: {extracted_data['error']}")
            return {"error_message": f"Erreur lors de l'extraction: {extracted_data['error']}"}
        
        # Log du résultat
        logger.info(f"✅ Entités extraites: {json.dumps(extracted_data, indent=2, ensure_ascii=False)}")
        
        # Formatage du résultat
        result = {
            "extracted_dates": {
                "date_decision": extracted_data.get("date_decision"),
                "date_recours": extracted_data.get("date_recours")
            },
            "extracted_applicant": extracted_data.get("demandeur"),
            "extracted_object": extracted_data.get("objet_recours"),
            "extracted_amount": extracted_data.get("montant_conteste"),
            "extracted_authority": extracted_data.get("autorite_competente"),
            "extracted_decision_type": extracted_data.get("type_decision")
        }
        
        logger.info("✅ Extraction des entités terminée avec succès")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'extraction des entités: {e}", exc_info=True)
        return {"error_message": f"Erreur lors de l'extraction des entités: {e}"}

async def analyze_deadline_criterion(state: CSPEState) -> Dict[str, Any]:
    """Analyse du critère délai avec Mistral"""
    logger.info("⏰ --- Analyse du critère délai ---")
    
    try:
        criterion_config = settings.CSPE_CRITERIA["deadline"]
        
        # Préparer les entités extraites
        extracted_entities = {
            "dates": state.get("extracted_dates", {}),
            "demandeur": state.get("extracted_applicant"),
            "objet": state.get("extracted_object"),
            "autorite": state.get("extracted_authority")
        }
        
        logger.info(f"📊 Entités pour l'analyse: {json.dumps(extracted_entities, indent=2, ensure_ascii=False)}")
        
        # Analyse avec Ollama
        logger.info("📡 Appel à Mistral pour analyse du délai...")
        analysis_result = await ollama_service.analyze_criterion(
            criterion_name=criterion_config["name"],
            document_content=state["document_content"],
            extracted_entities=extracted_entities,
            criterion_description=criterion_config["description"]
        )
        
        logger.info(f"✅ Analyse délai terminée: {json.dumps(analysis_result, indent=2, ensure_ascii=False)}")
        
        return {
            "deadline_analysis": {
                "is_compliant": analysis_result.get("is_compliant", False),
                "reasoning": analysis_result.get("reasoning", "Analyse non disponible"),
                "confidence": float(analysis_result.get("confidence", 0.0)),
                "source_quote": analysis_result.get("source_quote"),
                "criterion_name": criterion_config["name"],
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse du délai: {e}", exc_info=True)
        return {
            "deadline_analysis": {
                "is_compliant": False,
                "reasoning": f"Erreur lors de l'analyse: {str(e)}",
                "confidence": 0.0,
                "source_quote": None,
                "criterion_name": "Respect des délais",
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }

async def analyze_quality_criterion(state: CSPEState) -> Dict[str, Any]:
    """Analyse du critère qualité pour agir avec Mistral"""
    logger.info("👤 --- Analyse du critère qualité ---")
    
    try:
        criterion_config = settings.CSPE_CRITERIA["quality"]
        
        extracted_entities = {
            "dates": state.get("extracted_dates", {}),
            "demandeur": state.get("extracted_applicant"),
            "objet": state.get("extracted_object"),
            "montant": state.get("extracted_amount"),
            "autorite": state.get("extracted_authority")
        }
        
        logger.info("📡 Appel à Mistral pour analyse de la qualité...")
        analysis_result = await ollama_service.analyze_criterion(
            criterion_name=criterion_config["name"],
            document_content=state["document_content"],
            extracted_entities=extracted_entities,
            criterion_description=criterion_config["description"]
        )
        
        logger.info(f"✅ Analyse qualité terminée: {json.dumps(analysis_result, indent=2, ensure_ascii=False)}")
        
        return {
            "quality_analysis": {
                "is_compliant": analysis_result.get("is_compliant", False),
                "reasoning": analysis_result.get("reasoning", "Analyse non disponible"),
                "confidence": float(analysis_result.get("confidence", 0.0)),
                "source_quote": analysis_result.get("source_quote"),
                "criterion_name": criterion_config["name"],
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse de la qualité: {e}", exc_info=True)
        return {
            "quality_analysis": {
                "is_compliant": False,
                "reasoning": f"Erreur lors de l'analyse: {str(e)}",
                "confidence": 0.0,
                "source_quote": None,
                "criterion_name": "Qualité pour agir",
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }

async def analyze_object_criterion(state: CSPEState) -> Dict[str, Any]:
    """Analyse du critère objet du recours avec Mistral"""
    logger.info("📋 --- Analyse du critère objet ---")
    
    try:
        criterion_config = settings.CSPE_CRITERIA["object"]
        
        extracted_entities = {
            "dates": state.get("extracted_dates", {}),
            "demandeur": state.get("extracted_applicant"),
            "objet": state.get("extracted_object"),
            "montant": state.get("extracted_amount"),
            "autorite": state.get("extracted_authority"),
            "type_decision": state.get("extracted_decision_type")
        }
        
        logger.info("📡 Appel à Mistral pour analyse de l'objet...")
        analysis_result = await ollama_service.analyze_criterion(
            criterion_name=criterion_config["name"],
            document_content=state["document_content"],
            extracted_entities=extracted_entities,
            criterion_description=criterion_config["description"]
        )
        
        logger.info(f"✅ Analyse objet terminée: {json.dumps(analysis_result, indent=2, ensure_ascii=False)}")
        
        return {
            "object_analysis": {
                "is_compliant": analysis_result.get("is_compliant", False),
                "reasoning": analysis_result.get("reasoning", "Analyse non disponible"),
                "confidence": float(analysis_result.get("confidence", 0.0)),
                "source_quote": analysis_result.get("source_quote"),
                "criterion_name": criterion_config["name"],
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse de l'objet: {e}", exc_info=True)
        return {
            "object_analysis": {
                "is_compliant": False,
                "reasoning": f"Erreur lors de l'analyse: {str(e)}",
                "confidence": 0.0,
                "source_quote": None,
                "criterion_name": "Objet du recours",
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }

async def analyze_documents_criterion(state: CSPEState) -> Dict[str, Any]:
    """Analyse du critère pièces justificatives avec Mistral"""
    logger.info("📎 --- Analyse du critère pièces justificatives ---")
    
    try:
        criterion_config = settings.CSPE_CRITERIA["documents"]
        
        extracted_entities = {
            "dates": state.get("extracted_dates", {}),
            "demandeur": state.get("extracted_applicant"),
            "objet": state.get("extracted_object"),
            "autorite": state.get("extracted_authority"),
            "type_decision": state.get("extracted_decision_type")
        }
        
        logger.info("📡 Appel à Mistral pour analyse des documents...")
        analysis_result = await ollama_service.analyze_criterion(
            criterion_name=criterion_config["name"],
            document_content=state["document_content"],
            extracted_entities=extracted_entities,
            criterion_description=criterion_config["description"]
        )
        
        logger.info(f"✅ Analyse documents terminée: {json.dumps(analysis_result, indent=2, ensure_ascii=False)}")
        
        return {
            "documents_analysis": {
                "is_compliant": analysis_result.get("is_compliant", False),
                "reasoning": analysis_result.get("reasoning", "Analyse non disponible"),
                "confidence": float(analysis_result.get("confidence", 0.0)),
                "source_quote": analysis_result.get("source_quote"),
                "criterion_name": criterion_config["name"],
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse des documents: {e}", exc_info=True)
        return {
            "documents_analysis": {
                "is_compliant": False,
                "reasoning": f"Erreur lors de l'analyse: {str(e)}",
                "confidence": 0.0,
                "source_quote": None,
                "criterion_name": "Pièces justificatives",
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }

async def make_final_decision(state: CSPEState) -> Dict[str, Any]:
    """Décision finale basée sur l'analyse des 4 critères avec Mistral"""
    logger.info("⚖️ --- Décision finale ---")
    
    try:
        # Compiler les analyses
        analyses = {
            "deadline": state.get("deadline_analysis"),
            "quality": state.get("quality_analysis"), 
            "object": state.get("object_analysis"),
            "documents": state.get("documents_analysis")
        }
        
        # Vérifier que toutes les analyses sont présentes
        missing_analyses = [key for key, value in analyses.items() if not value]
        if missing_analyses:
            logger.warning(f"Analyses manquantes: {missing_analyses}")
        
        logger.info(f"📊 Analyses compilées: {json.dumps(analyses, indent=2, ensure_ascii=False)}")
        
        # Décision finale avec Mistral
        logger.info("📡 Appel à Mistral pour décision finale...")
        decision_result = await ollama_service.make_final_decision(analyses)
        
        # Calcul du score de confiance global
        confidences = [
            analysis.get("confidence", 0.0) 
            for analysis in analyses.values() 
            if analysis
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Détermination de la nécessité de révision
        needs_review = (
            decision_result.get("final_confidence", 0.0) < settings.CONFIDENCE_THRESHOLDS["medium"] or
            decision_result.get("is_review_required", True) or
            avg_confidence < settings.CONFIDENCE_THRESHOLDS["medium"]
        )
        
        result = {
            "final_classification": decision_result.get("final_classification", "IRRECEVABLE"),
            "final_justification": decision_result.get("final_justification", "Décision par défaut"),
            "final_confidence": float(decision_result.get("final_confidence", avg_confidence)),
            "is_review_required": needs_review,
            "critical_issues": decision_result.get("critical_issues", []),
            "analysis_summary": {
                "total_criteria": len(analyses),
                "compliant_criteria": sum(1 for a in analyses.values() if a and a.get("is_compliant", False)),
                "average_confidence": avg_confidence,
                "decision_timestamp": datetime.utcnow().isoformat()
            }
        }
        
        logger.info(f"✅ Décision finale: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la décision finale: {e}", exc_info=True)
        return {
            "final_classification": "IRRECEVABLE",
            "final_justification": f"Erreur lors de l'analyse: {str(e)}",
            "final_confidence": 0.0,
            "is_review_required": True,
            "critical_issues": ["Erreur technique lors de l'analyse"],
            "analysis_summary": {
                "total_criteria": 4,
                "compliant_criteria": 0,
                "average_confidence": 0.0,
                "decision_timestamp": datetime.utcnow().isoformat()
            }
        }

# Fonction utilitaire pour exécuter les analyses en parallèle
async def analyze_all_criteria_parallel(state: CSPEState) -> Dict[str, Any]:
    """Exécute l'analyse des 4 critères en parallèle pour optimiser les performances"""
    logger.info("⚡ --- Analyse parallèle des 4 critères ---")
    
    try:
        # Lancer toutes les analyses en parallèle
        tasks = [
            analyze_deadline_criterion(state),
            analyze_quality_criterion(state),
            analyze_object_criterion(state),
            analyze_documents_criterion(state)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combiner les résultats
        combined_result = {}
        for result in results:
            if isinstance(result, dict):
                combined_result.update(result)
            else:
                logger.error(f"Erreur dans l'analyse parallèle: {result}")
        
        logger.info("✅ Analyse parallèle terminée")
        return combined_result
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'analyse parallèle: {e}", exc_info=True)
        return {
            "error_message": f"Erreur lors de l'analyse parallèle: {e}"
        }