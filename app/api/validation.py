# app/api/validation.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import database_models as db_m
from app.models import pydantic_schemas as schemas
from app.api.auth import get_current_active_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/validation",
    tags=["Human Validation"],
)

# ===== FILE D'ATTENTE DE VALIDATION =====

@router.get("/pending")
async def get_pending_validations(
    limit: int = Query(20, description="Nombre maximum de documents à retourner"),
    priority: Optional[str] = Query(None, description="Filtrer par priorité"),
    db: Session = Depends(get_db),
    current_user: db_m.User = Depends(get_current_active_user)
):
    """Obtient la liste des documents en attente de validation"""
    logger.info(f"Récupération des validations en attente pour {current_user.email}")
    
    try:
        # Requête de base pour les documents nécessitant une validation
        query = db.query(db_m.Document).join(
            db_m.Classification, db_m.Document.id == db_m.Classification.document_id
        ).outerjoin(
            db_m.HumanValidation, db_m.Classification.id == db_m.HumanValidation.classification_id
        ).filter(
            db_m.Document.status == db_m.DocumentStatus.NEEDS_REVIEW,
            db_m.HumanValidation.id.is_(None)  # Pas encore validé
        )
        
        # Filtrage par priorité (basé sur la confiance)
        if priority == "high":
            query = query.filter(db_m.Classification.confidence_score < 0.5)
        elif priority == "medium":
            query = query.filter(
                and_(
                    db_m.Classification.confidence_score >= 0.5,
                    db_m.Classification.confidence_score < 0.8
                )
            )
        elif priority == "low":
            query = query.filter(db_m.Classification.confidence_score >= 0.8)
        
        # Ordonner par date de création (les plus anciens d'abord)
        documents = query.order_by(desc(db_m.Document.upload_date)).limit(limit).all()
        
        # Enrichir avec les données de classification
        result = []
        for doc in documents:
            classification = doc.classification
            if classification:
                result.append({
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "upload_date": doc.upload_date.isoformat(),
                    "classification": {
                        "id": classification.id,
                        "result": classification.result.value if classification.result else None,
                        "justification": classification.justification,
                        "confidence_score": float(classification.confidence_score) if classification.confidence_score else 0.0
                    },
                    "priority": _calculate_priority(classification.confidence_score),
                    "estimated_review_time": _estimate_review_time(classification.confidence_score)
                })
        
        logger.info(f"Retour de {len(result)} documents en attente de validation")
        return {
            "pending_documents": result,
            "total_count": len(result),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des validations en attente: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== VALIDATION D'UN DOCUMENT =====

@router.post("/validate/{classification_id}")
async def validate_classification(
    classification_id: str,
    validation_data: schemas.HumanValidationCreate,
    db: Session = Depends(get_db),
    current_user: db_m.User = Depends(get_current_active_user)
):
    """Valide une classification existante"""
    logger.info(f"Validation de la classification {classification_id} par {current_user.email}")
    
    try:
        # Vérifier que la classification existe
        classification = db.query(db_m.Classification).filter(
            db_m.Classification.id == classification_id
        ).first()
        
        if not classification:
            raise HTTPException(status_code=404, detail="Classification not found")
        
        # Vérifier qu'il n'y a pas déjà une validation
        existing_validation = db.query(db_m.HumanValidation).filter(
            db_m.HumanValidation.classification_id == classification_id
        ).first()
        
        if existing_validation:
            raise HTTPException(status_code=400, detail="Classification already validated")
        
        # Créer la validation humaine
        is_ia_correct = (classification.result == validation_data.validated_result)
        
        validation = db_m.HumanValidation(
            classification_id=classification_id,
            validator_id=current_user.id,
            validated_result=validation_data.validated_result,
            is_ia_correct=is_ia_correct,
            notes=validation_data.notes
        )
        
        db.add(validation)
        
        # Mettre à jour le statut du document
        document = classification.document
        if document:
            document.status = db_m.DocumentStatus.COMPLETED
        
        db.commit()
        db.refresh(validation)
        
        logger.info(f"Validation créée avec succès: {validation.id}")
        
        # Préparer la réponse
        return {
            "validation_id": validation.id,
            "classification_id": classification_id,
            "original_result": classification.result.value if classification.result else None,
            "validated_result": validation.validated_result.value,
            "is_ia_correct": is_ia_correct,
            "validator": current_user.full_name or current_user.email,
            "validated_at": validation.validation_date.isoformat(),
            "notes": validation.notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la validation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== HISTORIQUE DES VALIDATIONS =====

@router.get("/history")
async def get_validation_history(
    limit: int = Query(50, description="Nombre de validations à retourner"),
    validator_id: Optional[str] = Query(None, description="ID du validateur"),
    db: Session = Depends(get_db),
    current_user: db_m.User = Depends(get_current_active_user)
):
    """Obtient l'historique des validations"""
    logger.info(f"Récupération de l'historique des validations pour {current_user.email}")
    
    try:
        query = db.query(db_m.HumanValidation).join(
            db_m.Classification, db_m.HumanValidation.classification_id == db_m.Classification.id
        ).join(
            db_m.Document, db_m.Classification.document_id == db_m.Document.id
        )
        
        # Filtrer par validateur si spécifié
        if validator_id:
            query = query.filter(db_m.HumanValidation.validator_id == validator_id)
        
        validations = query.order_by(
            desc(db_m.HumanValidation.validation_date)
        ).limit(limit).all()
        
        result = []
        for validation in validations:
            classification = validation.classification
            document = classification.document if classification else None
            
            result.append({
                "validation_id": validation.id,
                "document": {
                    "id": document.id if document else None,
                    "filename": document.filename if document else None,
                    "upload_date": document.upload_date.isoformat() if document else None
                },
                "original_classification": {
                    "result": classification.result.value if classification and classification.result else None,
                    "confidence": float(classification.confidence_score) if classification and classification.confidence_score else 0.0
                },
                "validation": {
                    "result": validation.validated_result.value,
                    "is_ia_correct": validation.is_ia_correct,
                    "notes": validation.notes,
                    "validated_at": validation.validation_date.isoformat(),
                    "validator_id": validation.validator_id
                }
            })
        
        return {
            "validations": result,
            "total_count": len(result),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== STATISTIQUES DE VALIDATION =====

@router.get("/stats")
async def get_validation_stats(
    days: int = Query(30, description="Période en jours"),
    db: Session = Depends(get_db),
    current_user: db_m.User = Depends(get_current_active_user)
):
    """Obtient les statistiques de validation"""
    logger.info(f"Génération des statistiques de validation pour {current_user.email}")
    
    try:
        from sqlalchemy import func
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Nombre total de validations
        total_validations = db.query(func.count(db_m.HumanValidation.id)).filter(
            db_m.HumanValidation.validation_date >= start_date
        ).scalar()
        
        # Taux de précision de l'IA
        correct_predictions = db.query(func.count(db_m.HumanValidation.id)).filter(
            db_m.HumanValidation.validation_date >= start_date,
            db_m.HumanValidation.is_ia_correct == True
        ).scalar()
        
        accuracy_rate = (correct_predictions / total_validations * 100) if total_validations > 0 else 0
        
        # Répartition des résultats validés
        validation_results = db.query(
            db_m.HumanValidation.validated_result,
            func.count(db_m.HumanValidation.id).label('count')
        ).filter(
            db_m.HumanValidation.validation_date >= start_date
        ).group_by(db_m.HumanValidation.validated_result).all()
        
        # Top validateurs
        top_validators = db.query(
            db_m.HumanValidation.validator_id,
            func.count(db_m.HumanValidation.id).label('count')
        ).filter(
            db_m.HumanValidation.validation_date >= start_date
        ).group_by(db_m.HumanValidation.validator_id).order_by(desc('count')).limit(5).all()
        
        return {
            "period_days": days,
            "total_validations": total_validations,
            "ia_accuracy_percent": round(accuracy_rate, 2),
            "validation_results": [
                {"result": result.value, "count": count}
                for result, count in validation_results
            ],
            "top_validators": [
                {"validator_id": validator_id, "validations_count": count}
                for validator_id, count in top_validators
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération des statistiques: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== FONCTIONS UTILITAIRES =====

def _calculate_priority(confidence_score: Optional[float]) -> str:
    """Calcule la priorité basée sur le score de confiance"""
    if confidence_score is None:
        return "high"
    
    if confidence_score < 0.5:
        return "high"
    elif confidence_score < 0.8:
        return "medium"
    else:
        return "low"

def _estimate_review_time(confidence_score: Optional[float]) -> str:
    """Estime le temps de révision nécessaire"""
    if confidence_score is None:
        return "15-20 minutes"
    
    if confidence_score < 0.5:
        return "15-20 minutes"
    elif confidence_score < 0.8:
        return "10-15 minutes"
    else:
        return "5-10 minutes"