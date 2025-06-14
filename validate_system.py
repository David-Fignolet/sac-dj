# validate_system.py
import sys
import subprocess
import importlib
import requests
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import asyncio

class SystemValidator:
    """Validateur complet du système SAC-DJ"""
    
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []
        
        # URLs de test
        self.api_base = "http://localhost:8000"
        self.frontend_base = "http://localhost:8501"
        self.ollama_base = "http://localhost:11434"
    
    def log_result(self, test_name: str, status: str, message: str = "", details: str = ""):
        """Enregistre un résultat de test"""
        result = {
            "test": test_name,
            "status": status,  # "PASS", "FAIL", "WARN", "SKIP"
            "message": message,
            "details": details
        }
        self.results.append(result)
        
        # Affichage coloré
        icons = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "SKIP": "⏭️"}
        icon = icons.get(status, "❓")
        print(f"{icon} {test_name}: {message}")
        
        if details:
            print(f"   📝 {details}")
    
    def check_python_version(self):
        """Vérifie la version de Python"""
        version = sys.version_info
        
        if version >= (3, 11):
            self.log_result("Python Version", "PASS", f"Python {version.major}.{version.minor}.{version.micro}")
        elif version >= (3, 9):
            self.log_result("Python Version", "WARN", f"Python {version.major}.{version.minor} (3.11+ recommandé)")
        else:
            self.log_result("Python Version", "FAIL", f"Python {version.major}.{version.minor} (minimum 3.9 requis)")
    
    def check_required_packages(self):
        """Vérifie que les packages requis sont installés"""
        required_packages = [
            "fastapi", "uvicorn", "sqlalchemy", "pydantic", "streamlit",
            "langchain", "langgraph", "spacy", "httpx", "requests",
            "plotly", "pandas", "passlib", "python-jose"
        ]
        
        missing = []
        installed = []
        
        for package in required_packages:
            try:
                importlib.import_module(package)
                installed.append(package)
            except ImportError:
                missing.append(package)
        
        if not missing:
            self.log_result("Required Packages", "PASS", f"{len(installed)} packages installés")
        else:
            self.log_result("Required Packages", "FAIL", 
                          f"{len(missing)} packages manquants", 
                          f"Manquants: {', '.join(missing)}")
    
    def check_spacy_model(self):
        """Vérifie le modèle spaCy français"""
        try:
            import spacy
            nlp = spacy.load("fr_core_news_lg")
            
            # Test basique
            doc = nlp("Test de reconnaissance d'entités nommées.")
            
            self.log_result("spaCy French Model", "PASS", "Modèle fr_core_news_lg disponible")
            
        except OSError:
            self.log_result("spaCy French Model", "FAIL", 
                          "Modèle français non installé",
                          "Exécutez: python -m spacy download fr_core_news_lg")
        except Exception as e:
            self.log_result("spaCy French Model", "FAIL", f"Erreur: {str(e)}")
    
    def check_project_structure(self):
        """Vérifie la structure du projet"""
        project_root = Path(".")
        
        required_files = [
            "app/main.py", "app/config.py", "app/database.py",
            "app/services/ollama_service.py", "app/core/graph.py",
            "init_db.py", "requirements.txt", ".env.example"
        ]
        
        required_dirs = [
            "app/api", "app/core", "app/models", "app/services",
            "frontend", "tests"
        ]
        
        missing_files = []
        missing_dirs = []
        
        for file_path in required_files:
            if not (project_root / file_path).exists():
                missing_files.append(file_path)
        
        for dir_path in required_dirs:
            if not (project_root / dir_path).exists():
                missing_dirs.append(dir_path)
        
        if not missing_files and not missing_dirs:
            self.log_result("Project Structure", "PASS", "Structure complète")
        else:
            issues = []
            if missing_files:
                issues.append(f"Fichiers manquants: {', '.join(missing_files)}")
            if missing_dirs:
                issues.append(f"Dossiers manquants: {', '.join(missing_dirs)}")
            
            self.log_result("Project Structure", "FAIL", "Structure incomplète", "; ".join(issues))
    
    def check_environment_config(self):
        """Vérifie la configuration d'environnement"""
        env_example = Path(".env.example")
        env_file = Path(".env")
        
        if not env_example.exists():
            self.log_result("Environment Config", "FAIL", "Fichier .env.example manquant")
            return
        
        if not env_file.exists():
            self.log_result("Environment Config", "WARN", 
                          "Fichier .env manquant",
                          "Copiez .env.example vers .env")
            return
        
        # Vérifier les variables essentielles dans .env
        env_content = env_file.read_text()
        required_vars = [
            "SECRET_KEY", "OLLAMA_BASE_URL", "LLM_MODEL", 
            "DATABASE_URL", "FIRST_ADMIN_EMAIL"
        ]
        
        missing_vars = [var for var in required_vars if var not in env_content]
        
        if not missing_vars:
            self.log_result("Environment Config", "PASS", "Configuration complète")
        else:
            self.log_result("Environment Config", "FAIL",
                          f"Variables manquantes dans .env",
                          f"Manquantes: {', '.join(missing_vars)}")
    
    def check_database_connection(self):
        """Vérifie la connexion à la base de données"""
        try:
            sys.path.append(".")
            from app.database import SessionLocal
            from app.config import settings
            
            # Test de connexion
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            
            db_type = "SQLite" if settings.is_sqlite else "PostgreSQL"
            self.log_result("Database Connection", "PASS", f"Connexion {db_type} OK")
            
        except Exception as e:
            self.log_result("Database Connection", "FAIL", f"Erreur de connexion: {str(e)}")
    
    def check_ollama_service(self):
        """Vérifie le service Ollama"""
        try:
            # Test de connexion
            response = requests.get(f"{self.ollama_base}/api/tags", timeout=5)
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                
                # Vérifier si Mistral est disponible
                mistral_available = any("mistral" in name for name in model_names)
                
                if mistral_available:
                    self.log_result("Ollama Service", "PASS", 
                                  "Ollama actif avec Mistral",
                                  f"Modèles: {', '.join(model_names)}")
                else:
                    self.log_result("Ollama Service", "WARN",
                                  "Ollama actif mais Mistral manquant",
                                  "Exécutez: ollama pull mistral:7b-instruct")
            else:
                self.log_result("Ollama Service", "FAIL", f"Ollama répond avec status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.log_result("Ollama Service", "FAIL", 
                          "Ollama non accessible",
                          "Démarrez Ollama avec start_ollama.bat")
        except Exception as e:
            self.log_result("Ollama Service", "FAIL", f"Erreur Ollama: {str(e)}")
    
    def check_api_service(self):
        """Vérifie l'API FastAPI"""
        try:
            # Test health check
            response = requests.get(f"{self.api_base}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Analyser les services
                services = health_data.get("services", {})
                all_healthy = all(
                    service.get("status") == "healthy" 
                    for service in services.values()
                )
                
                if all_healthy:
                    self.log_result("API Service", "PASS", "API entièrement fonctionnelle")
                else:
                    self.log_result("API Service", "WARN", 
                                  "API active mais certains services dégradés",
                                  f"Services: {list(services.keys())}")
            else:
                self.log_result("API Service", "FAIL", f"API répond avec status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.log_result("API Service", "FAIL",
                          "API non accessible",
                          "Démarrez l'API avec start_api.bat")
        except Exception as e:
            self.log_result("API Service", "FAIL", f"Erreur API: {str(e)}")
    
    def check_frontend_service(self):
        """Vérifie l'interface Streamlit"""
        try:
            response = requests.get(self.frontend_base, timeout=5)
            
            if response.status_code == 200:
                self.log_result("Frontend Service", "PASS", "Interface Streamlit accessible")
            else:
                self.log_result("Frontend Service", "FAIL", f"Frontend répond avec status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.log_result("Frontend Service", "FAIL",
                          "Interface non accessible",
                          "Démarrez l'interface avec start_frontend.bat")
        except Exception as e:
            self.log_result("Frontend Service", "FAIL", f"Erreur Frontend: {str(e)}")
    
    async def test_complete_workflow(self):
        """Test du workflow complet d'analyse"""
        try:
            sys.path.append(".")
            from app.core.graph import execute_cspe_analysis
            
            # Document de test
            test_content = """
            Monsieur le Président,
            Je soussigné, Jean DUPONT, demeurant 123 Rue de la Paix, 75001 Paris,
            ai l'honneur de former un recours contre la décision de raccordement CSPE
            du 15 mars 2024, qui m'a été notifiée le 20 mars 2024.
            """
            
            # Exécuter l'analyse (timeout 60s)
            result = await asyncio.wait_for(
                execute_cspe_analysis("test-doc-123", test_content),
                timeout=60.0
            )
            
            if result and result.get("final_classification"):
                self.log_result("Complete Workflow", "PASS",
                              f"Analyse réussie: {result['final_classification']}",
                              f"Confiance: {result.get('final_confidence', 0):.1%}")
            else:
                self.log_result("Complete Workflow", "FAIL", "Analyse incomplète")
                
        except asyncio.TimeoutError:
            self.log_result("Complete Workflow", "FAIL", "Timeout de l'analyse (>60s)")
        except Exception as e:
            self.log_result("Complete Workflow", "FAIL", f"Erreur workflow: {str(e)}")
    
    def check_scripts_availability(self):
        """Vérifie que les scripts de démarrage sont disponibles"""
        scripts = [
            "setup.bat", "start_all.bat", "start_ollama.bat",
            "start_api.bat", "start_frontend.bat", "install_model.bat",
            "check_status.bat"
        ]
        
        missing_scripts = []
        for script in scripts:
            if not Path(script).exists():
                missing_scripts.append(script)
        
        if not missing_scripts:
            self.log_result("Startup Scripts", "PASS", "Tous les scripts disponibles")
        else:
            self.log_result("Startup Scripts", "WARN",
                          f"{len(missing_scripts)} scripts manquants",
                          f"Manquants: {', '.join(missing_scripts)}")
    
    async def run_all_tests(self):
        """Exécute tous les tests de validation"""
        print("🔍 === VALIDATION COMPLÈTE DU SYSTÈME SAC-DJ ===")
        print()
        
        # Tests de base (rapides)
        print("📋 Phase 1: Tests de Configuration")
        self.check_python_version()
        self.check_required_packages()
        self.check_spacy_model()
        self.check_project_structure()
        self.check_environment_config()
        self.check_scripts_availability()
        
        print("\n🔗 Phase 2: Tests de Connectivité")
        self.check_database_connection()
        self.check_ollama_service()
        self.check_api_service()
        self.check_frontend_service()
        
        print("\n🧪 Phase 3: Test Fonctionnel")
        await self.test_complete_workflow()
        
        # Résumé
        print("\n" + "="*50)
        self.print_summary()
    
    def print_summary(self):
        """Affiche un résumé des résultats"""
        pass_count = len([r for r in self.results if r["status"] == "PASS"])
        fail_count = len([r for r in self.results if r["status"] == "FAIL"])
        warn_count = len([r for r in self.results if r["status"] == "WARN"])
        total_count = len(self.results)
        
        print(f"📊 RÉSUMÉ: {pass_count} réussis, {fail_count} échecs, {warn_count} avertissements")
        print(f"📈 Score global: {pass_count}/{total_count} ({pass_count/total_count*100:.1f}%)")
        
        if fail_count == 0:
            if warn_count == 0:
                print("🎉 SYSTÈME PARFAITEMENT FONCTIONNEL !")
            else:
                print("✅ SYSTÈME FONCTIONNEL avec quelques avertissements")
        else:
            print("❌ SYSTÈME PARTIELLEMENT FONCTIONNEL - Corrections nécessaires")
        
        # Afficher les échecs et avertissements
        if fail_count > 0:
            print("\n🔥 ÉCHECS À CORRIGER:")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"   ❌ {result['test']}: {result['message']}")
                    if result["details"]:
                        print(f"      💡 {result['details']}")
        
        if warn_count > 0:
            print("\n⚠️ AVERTISSEMENTS:")
            for result in self.results:
                if result["status"] == "WARN":
                    print(f"   ⚠️ {result['test']}: {result['message']}")
                    if result["details"]:
                        print(f"      💡 {result['details']}")
        
        # Recommandations
        print("\n🚀 PROCHAINES ÉTAPES:")
        if fail_count > 0:
            print("1. Corrigez les échecs listés ci-dessus")
            print("2. Relancez la validation: python validate_system.py")
        else:
            print("1. Démarrez tous les services: start_all.bat")
            print("2. Accédez à l'interface: http://localhost:8501")
            print("3. Connectez-vous avec admin@test.com / admin123")

async def main():
    """Point d'entrée principal"""
    validator = SystemValidator()
    await validator.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())