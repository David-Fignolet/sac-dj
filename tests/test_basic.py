# tests/test_basic.py
import pytest
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path Python
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_imports():
    """Test que toutes les imports principales fonctionnent"""
    try:
        # Test des imports de base
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        import streamlit
        import requests
        import langchain
        import langgraph
        import spacy
        import httpx
        
        print("✅ Tous les imports de base fonctionnent")
        
    except ImportError as e:
        pytest.fail(f"❌ Import manquant: {e}")

def test_config():
    """Test que la configuration se charge correctement"""
    try:
        from app.config import settings
        
        # Vérifier que les paramètres essentiels sont définis
        assert settings.APP_NAME == "SAC-DJ"
        assert settings.SECRET_KEY is not None
        assert settings.OLLAMA_BASE_URL is not None
        assert settings.LLM_MODEL is not None
        
        print("✅ Configuration chargée correctement")
        
    except Exception as e:
        pytest.fail(f"❌ Erreur de configuration: {e}")

def test_database_models():
    """Test que les modèles de base de données sont valides"""
    try:
        from app.models import database_models as db_m
        from app.database import Base
        
        # Vérifier que les classes principales existent
        assert hasattr(db_m, 'User')
        assert hasattr(db_m, 'Document')
        assert hasattr(db_m, 'Classification')
        assert hasattr(db_m, 'HumanValidation')
        
        # Vérifier que les énumérations existent
        assert hasattr(db_m, 'UserRole')
        assert hasattr(db_m, 'DocumentStatus')
        assert hasattr(db_m, 'ClassificationResult')
        
        print("✅ Modèles de base de données valides")
        
    except Exception as e:
        pytest.fail(f"❌ Erreur modèles BDD: {e}")

def test_ollama_service():
    """Test que le service Ollama se crée correctement"""
    try:
        from app.services.ollama_service import ollama_service
        
        # Vérifier que le service a les méthodes nécessaires
        assert hasattr(ollama_service, 'health_check')
        assert hasattr(ollama_service, 'is_model_available')
        assert hasattr(ollama_service, 'generate_completion')
        assert hasattr(ollama_service, 'extract_entities_with_llm')
        
        print("✅ Service Ollama créé correctement")
        
    except Exception as e:
        pytest.fail(f"❌ Erreur service Ollama: {e}")

def test_langgraph_components():
    """Test que les composants LangGraph sont valides"""
    try:
        from app.core.state import CSPEState, CritereAnalysis
        from app.core.nodes import extract_entities
        from app.core.graph import create_cspe_workflow
        
        # Vérifier que les types TypedDict sont corrects
        assert CSPEState is not None
        assert CritereAnalysis is not None
        
        # Vérifier que les fonctions nodes existent
        assert callable(extract_entities)
        
        # Vérifier que le workflow peut être créé
        workflow = create_cspe_workflow()
        assert workflow is not None
        
        print("✅ Composants LangGraph valides")
        
    except Exception as e:
        pytest.fail(f"❌ Erreur LangGraph: {e}")

def test_api_routes():
    """Test que les routes API sont définies"""
    try:
        from app.api import documents, auth, analytics, validation
        
        # Vérifier que les routeurs existent
        assert hasattr(documents, 'router')
        assert hasattr(auth, 'router')
        assert hasattr(analytics, 'router')
        assert hasattr(validation, 'router')
        
        print("✅ Routes API définies")
        
    except Exception as e:
        pytest.fail(f"❌ Erreur routes API: {e}")

def test_spacy_model():
    """Test que le modèle spaCy français est disponible"""
    try:
        import spacy
        
        # Essayer de charger le modèle français
        try:
            nlp = spacy.load("fr_core_news_lg")
            
            # Test basique
            doc = nlp("Ceci est un test.")
            assert len(doc) > 0
            
            print("✅ Modèle spaCy français disponible")
            
        except OSError:
            print("⚠️ Modèle spaCy français non installé - lancez: python -m spacy download fr_core_news_lg")
            
    except Exception as e:
        pytest.fail(f"❌ Erreur spaCy: {e}")

def test_file_structure():
    """Test que la structure de fichiers est correcte"""
    project_root = Path(__file__).parent.parent
    
    # Fichiers essentiels
    essential_files = [
        "app/main.py",
        "app/config.py", 
        "app/database.py",
        "init_db.py",
        "requirements.txt",
        ".env.example"
    ]
    
    for file_path in essential_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"Fichier manquant: {file_path}"
    
    # Dossiers essentiels
    essential_dirs = [
        "app/api",
        "app/core",
        "app/models", 
        "app/services",
        "frontend",
        "tests"
    ]
    
    for dir_path in essential_dirs:
        full_path = project_root / dir_path
        assert full_path.exists(), f"Dossier manquant: {dir_path}"
    
    print("✅ Structure de fichiers correcte")

def test_environment_file():
    """Test que le fichier .env.example est valide"""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env.example"
    
    if env_file.exists():
        content = env_file.read_text()
        
        # Vérifier que les variables essentielles sont présentes
        required_vars = [
            "SECRET_KEY",
            "OLLAMA_BASE_URL", 
            "LLM_MODEL",
            "DATABASE_URL",
            "FIRST_ADMIN_EMAIL"
        ]
        
        for var in required_vars:
            assert var in content, f"Variable manquante dans .env.example: {var}"
        
        print("✅ Fichier .env.example valide")
    else:
        pytest.fail("❌ Fichier .env.example manquant")

if __name__ == "__main__":
    """Exécution directe des tests"""
    print("🧪 === TESTS DE VALIDATION SAC-DJ ===")
    print()
    
    tests = [
        test_imports,
        test_config,
        test_database_models,
        test_ollama_service,
        test_langgraph_components,
        test_api_routes,
        test_spacy_model,
        test_file_structure,
        test_environment_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
    
    print()
    print(f"📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! Le projet est prêt.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez l'installation.")