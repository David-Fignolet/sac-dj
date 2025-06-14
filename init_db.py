# init_db.py
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path Python
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from sqlalchemy import text
from app.database import engine, Base, SessionLocal
from app.models import database_models
from app.config import settings
from app.api.auth import get_password_hash
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Crée toutes les tables de la base de données"""
    logger.info("🗄️ Création des tables de la base de données...")
    
    try:
        # Créer toutes les tables définies dans les modèles
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables créées avec succès")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création des tables: {e}")
        return False

def create_admin_user():
    """Crée l'utilisateur administrateur par défaut"""
    logger.info("👤 Création de l'utilisateur administrateur...")
    
    db = SessionLocal()
    try:
        # Vérifier si l'admin existe déjà
        existing_admin = db.query(database_models.User).filter(
            database_models.User.email == settings.FIRST_ADMIN_EMAIL
        ).first()
        
        if existing_admin:
            logger.info(f"ℹ️ L'utilisateur admin existe déjà: {settings.FIRST_ADMIN_EMAIL}")
            return True
        
        # Créer l'utilisateur admin
        hashed_password = get_password_hash(settings.FIRST_ADMIN_PASSWORD)
        admin_user = database_models.User(
            email=settings.FIRST_ADMIN_EMAIL,
            full_name="Administrateur Système",
            hashed_password=hashed_password,
            role=database_models.UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        logger.info(f"✅ Utilisateur admin créé: {settings.FIRST_ADMIN_EMAIL}")
        logger.info(f"🔑 Mot de passe: {settings.FIRST_ADMIN_PASSWORD}")
        logger.info("⚠️ IMPORTANT: Changez ce mot de passe en production !")
        
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur lors de la création de l'admin: {e}")
        return False
    finally:
        db.close()

def create_sample_data():
    """Crée des données d'exemple pour le développement"""
    if not settings.DEBUG:
        logger.info("ℹ️ Données d'exemple ignorées (pas en mode debug)")
        return
    
    logger.info("📊 Création de données d'exemple...")
    
    db = SessionLocal()
    try:
        # Vérifier si des documents existent déjà
        existing_docs = db.query(database_models.Document).count()
        if existing_docs > 0:
            logger.info("ℹ️ Des documents existent déjà, pas de données d'exemple créées")
            return
        
        # Créer quelques documents d'exemple
        sample_documents = [
            {
                "filename": "recours_exemple_1.txt",
                "content": "Monsieur le Président, Je soussigné, Jean DUPONT, demeurant 123 Rue de la Paix, 75001 Paris, ai l'honneur de former un recours contre la décision de raccordement CSPE du 15 mars 2024...",
                "status": database_models.DocumentStatus.COMPLETED
            },
            {
                "filename": "recours_exemple_2.txt", 
                "content": "Madame, Monsieur, La société SARL EXEMPLE, représentée par son gérant Monsieur Martin MARTIN, conteste par la présente la décision de refus de raccordement du 20 février 2024...",
                "status": database_models.DocumentStatus.NEEDS_REVIEW
            }
        ]
        
        for i, doc_data in enumerate(sample_documents):
            # Créer le document
            import hashlib
            content_hash = hashlib.sha256(doc_data["content"].encode()).hexdigest()[:16]
            
            document = database_models.Document(
                filename=doc_data["filename"],
                content_hash=content_hash,
                file_size=len(doc_data["content"]),
                content_type="text/plain",
                file_path=f"samples/{doc_data['filename']}",
                status=doc_data["status"],
                uploaded_by_id="admin-sample"  # ID fictif pour les exemples
            )
            
            db.add(document)
            db.flush()  # Pour obtenir l'ID
            
            # Créer une classification d'exemple
            if i == 0:  # Premier document : RECEVABLE
                classification = database_models.Classification(
                    document_id=document.id,
                    result=database_models.ClassificationResult.RECEVABLE,
                    justification="Tous les critères sont respectés : délai conforme (recours formé 45 jours après notification), demandeur qualifié (personne directement concernée), objet clairement défini (contestation décision de raccordement), pièces justificatives complètes.",
                    confidence_score=0.94,
                    analysis_steps={
                        "deadline_analysis": {"is_compliant": True, "confidence": 0.95},
                        "quality_analysis": {"is_compliant": True, "confidence": 0.92}, 
                        "object_analysis": {"is_compliant": True, "confidence": 0.96},
                        "documents_analysis": {"is_compliant": True, "confidence": 0.93}
                    },
                    processing_time_ms=3247,
                    model_version="mistral:7b-instruct"
                )
            else:  # Deuxième document : Besoin de révision
                classification = database_models.Classification(
                    document_id=document.id,
                    result=database_models.ClassificationResult.REQUIRES_REVIEW,
                    justification="Analyse incertaine : délai limite (exactement 60 jours), qualité du demandeur à vérifier (société vs décision individuelle), pièces justificatives incomplètes.",
                    confidence_score=0.67,
                    analysis_steps={
                        "deadline_analysis": {"is_compliant": True, "confidence": 0.71},
                        "quality_analysis": {"is_compliant": False, "confidence": 0.58},
                        "object_analysis": {"is_compliant": True, "confidence": 0.84},
                        "documents_analysis": {"is_compliant": False, "confidence": 0.55}
                    },
                    processing_time_ms=4156,
                    model_version="mistral:7b-instruct"
                )
            
            db.add(classification)
        
        db.commit()
        logger.info("✅ Données d'exemple créées")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur lors de la création des données d'exemple: {e}")
    finally:
        db.close()

def verify_database():
    """Vérifie que la base de données fonctionne correctement"""
    logger.info("🔍 Vérification de la base de données...")
    
    db = SessionLocal()
    try:
        # Test de connexion simple
        result = db.execute(text("SELECT 1")).scalar()
        if result != 1:
            raise Exception("Test de connexion échoué")
        
        # Compter les tables
        if settings.is_sqlite:
            tables_count = db.execute(text(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )).scalar()
        else:
            tables_count = db.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
            )).scalar()
        
        logger.info(f"✅ Base de données opérationnelle - {tables_count} tables")
        
        # Compter les utilisateurs
        users_count = db.query(database_models.User).count()
        documents_count = db.query(database_models.Document).count()
        classifications_count = db.query(database_models.Classification).count()
        
        logger.info(f"📊 Données actuelles:")
        logger.info(f"   👤 Utilisateurs: {users_count}")
        logger.info(f"   📄 Documents: {documents_count}")
        logger.info(f"   🏷️ Classifications: {classifications_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification: {e}")
        return False
    finally:
        db.close()

def create_directories():
    """Crée les répertoires nécessaires"""
    logger.info("📁 Création des répertoires...")
    
    directories = [
        settings.UPLOAD_DIR,
        "logs",
        "backups",
        "samples"
    ]
    
    for directory in directories:
        path = Path(directory)
        try:
            path.mkdir(exist_ok=True)
            logger.info(f"✅ Répertoire créé/vérifié: {directory}")
        except Exception as e:
            logger.error(f"❌ Erreur création répertoire {directory}: {e}")

def init_db():
    """Fonction principale d'initialisation"""
    logger.info("🚀 === INITIALISATION DE LA BASE DE DONNÉES SAC-DJ ===")
    
    # Afficher la configuration
    logger.info(f"📋 Configuration:")
    logger.info(f"   🗄️ Base de données: {settings.DATABASE_URL}")
    logger.info(f"   🤖 Ollama: {settings.OLLAMA_BASE_URL}")
    logger.info(f"   🧠 Modèle: {settings.LLM_MODEL}")
    logger.info(f"   📁 Upload: {settings.UPLOAD_DIR}")
    logger.info(f"   🐛 Debug: {settings.DEBUG}")
    
    success_count = 0
    total_steps = 5
    
    # Étape 1: Créer les répertoires
    create_directories()
    success_count += 1
    
    # Étape 2: Créer les tables
    if create_tables():
        success_count += 1
    
    # Étape 3: Créer l'utilisateur admin
    if create_admin_user():
        success_count += 1
    
    # Étape 4: Vérifier la base de données
    if verify_database():
        success_count += 1
    
    # Étape 5: Créer des données d'exemple (seulement en debug)
    if settings.DEBUG:
        create_sample_data()
    success_count += 1
    
    # Résumé
    logger.info("=" * 50)
    if success_count == total_steps:
        logger.info("🎉 INITIALISATION TERMINÉE AVEC SUCCÈS !")
        logger.info(f"✅ {success_count}/{total_steps} étapes réussies")
        
        logger.info("\n🚀 Prochaines étapes:")
        logger.info("1. Démarrez Ollama: start_ollama.bat")
        logger.info("2. Installez Mistral: install_model.bat")
        logger.info("3. Démarrez l'API: start_api.bat")
        logger.info("4. Démarrez l'interface: start_frontend.bat")
        
        logger.info(f"\n🔐 Connexion admin:")
        logger.info(f"   Email: {settings.FIRST_ADMIN_EMAIL}")
        logger.info(f"   Mot de passe: {settings.FIRST_ADMIN_PASSWORD}")
        
    else:
        logger.error(f"❌ INITIALISATION INCOMPLÈTE: {success_count}/{total_steps} étapes réussies")
        logger.error("🔧 Vérifiez les erreurs ci-dessus et relancez le script")
    
    logger.info("=" * 50)

if __name__ == "__main__":
    init_db()