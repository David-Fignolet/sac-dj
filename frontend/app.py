# frontend/app.py
import streamlit as st
import requests
import json
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Configuration de la page
st.set_page_config(
    page_title="SAC-DJ | Système d'Analyse Cognitive",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== CONFIGURATION =====

# URL de l'API (détection automatique Docker vs local)
if os.getenv('IS_IN_DOCKER'):
    API_BASE_URL = "http://api:8000"
else:
    API_BASE_URL = "http://localhost:8000"

# Constantes
UPLOAD_MAX_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'docx', 'doc']

# ===== STYLE CSS PERSONNALISÉ =====

st.markdown("""
<style>
/* Style Nord Theme */
.main {
    background-color: #2E3440;
}

.stAlert > div {
    background-color: #3B4252;
    border: 1px solid #4C566A;
}

.success-box {
    background-color: #A3BE8C;
    color: #2E3440;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}

.warning-box {
    background-color: #EBCB8B;
    color: #2E3440;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}

.error-box {
    background-color: #BF616A;
    color: #ECEFF4;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}

.metric-card {
    background-color: #3B4252;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #88C0D0;
}

.classification-result {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
}

.recevable {
    background-color: #A3BE8C;
    color: #2E3440;
}

.irrecevable {
    background-color: #BF616A;
    color: #ECEFF4;
}

.review-required {
    background-color: #EBCB8B;
    color: #2E3440;
}
</style>
""", unsafe_allow_html=True)

# ===== FONCTIONS UTILITAIRES =====

@st.cache_data(ttl=60)
def test_api_connection() -> bool:
    """Test la connexion à l'API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def make_api_request(method: str, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
    """Fait une requête à l'API avec gestion d'erreurs"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        # Ajouter le token d'auth si disponible
        headers = kwargs.get('headers', {})
        if 'token' in st.session_state:
            headers['Authorization'] = f"Bearer {st.session_state.token}"
            kwargs['headers'] = headers
        
        response = requests.request(method, url, timeout=30, **kwargs)
        
        if response.status_code == 401:
            st.error("🔐 Session expirée, veuillez vous reconnecter")
            if 'token' in st.session_state:
                del st.session_state.token
            st.rerun()
            return None
        
        if response.status_code >= 400:
            st.error(f"❌ Erreur API ({response.status_code}): {response.text}")
            return None
        
        return response.json()
        
    except requests.exceptions.Timeout:
        st.error("⏱️ Timeout: L'API met trop de temps à répondre")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Impossible de se connecter à l'API. Vérifiez que l'API est démarrée.")
        return None
    except Exception as e:
        st.error(f"❌ Erreur inattendue: {str(e)}")
        return None

def login_user(email: str, password: str) -> bool:
    """Connecte un utilisateur"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/token",
            data={"username": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data["access_token"]
            
            # Récupérer les infos utilisateur
            user_info = make_api_request("GET", "/api/v1/auth/me")
            if user_info:
                st.session_state.user = user_info
                logger.info(f"Connexion réussie pour {email}")
                return True
        else:
            st.error("❌ Email ou mot de passe incorrect")
            return False
            
    except Exception as e:
        st.error(f"❌ Erreur de connexion: {str(e)}")
        return False

def logout_user():
    """Déconnecte l'utilisateur"""
    if 'token' in st.session_state:
        del st.session_state.token
    if 'user' in st.session_state:
        del st.session_state.user
    st.success("✅ Déconnexion réussie")
    st.rerun()

def format_file_size(size_bytes: int) -> str:
    """Formate la taille de fichier"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def display_classification_result(result: Dict[str, Any]):
    """Affiche le résultat d'une classification"""
    classification = result.get('final_classification', 'UNKNOWN')
    confidence = result.get('final_confidence', 0.0)
    justification = result.get('final_justification', 'Aucune justification disponible')
    
    # Affichage du résultat principal
    if classification == "RECEVABLE":
        st.markdown(f"""
        <div class="classification-result recevable">
            ✅ RECEVABLE
            <br><small>Confiance: {confidence:.1%}</small>
        </div>
        """, unsafe_allow_html=True)
    elif classification == "IRRECEVABLE":
        st.markdown(f"""
        <div class="classification-result irrecevable">
            ❌ IRRECEVABLE
            <br><small>Confiance: {confidence:.1%}</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="classification-result review-required">
            🔍 RÉVISION REQUISE
            <br><small>Confiance: {confidence:.1%}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Justification
    st.subheader("📋 Justification")
    st.write(justification)
    
    # Analyse détaillée si disponible
    if 'analysis_summary' in result:
        summary = result['analysis_summary']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Critères analysés", summary.get('total_criteria', 0))
        with col2:
            st.metric("Critères conformes", summary.get('compliant_criteria', 0))
        with col3:
            st.metric("Confiance moyenne", f"{summary.get('average_confidence', 0):.1%}")

# ===== COMPOSANTS DE L'INTERFACE =====

def render_login_page():
    """Page de connexion"""
    st.title("🏛️ SAC-DJ - Connexion")
    st.write("Système d'Analyse Cognitive pour Dossiers Juridiques")
    
    # Test de connexion API
    api_ok = test_api_connection()
    if not api_ok:
        st.error("🔌 Impossible de se connecter à l'API. Vérifiez que l'API est démarrée.")
        st.info("💡 Lancez `start_api.bat` pour démarrer l'API")
        st.stop()
    
    st.success("✅ API accessible")
    
    # Formulaire de connexion
    with st.form("login_form"):
        st.subheader("Connexion")
        email = st.text_input("📧 Email", value="admin@test.com")
        password = st.text_input("🔑 Mot de passe", type="password", value="admin123")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("🚀 Se connecter", type="primary", use_container_width=True):
                if email and password:
                    with st.spinner("Connexion en cours..."):
                        if login_user(email, password):
                            st.success("✅ Connexion réussie !")
                            st.rerun()
                else:
                    st.error("❌ Veuillez remplir tous les champs")
        
        with col2:
            if st.form_submit_button("ℹ️ Infos par défaut", use_container_width=True):
                st.info("📧 Email: admin@test.com")
                st.info("🔑 Mot de passe: admin123")

def render_sidebar():
    """Barre latérale avec navigation"""
    with st.sidebar:
        # Informations utilisateur
        user = st.session_state.get('user', {})
        st.header(f"👤 {user.get('full_name', user.get('email', 'Utilisateur'))}")
        st.write(f"**Rôle:** {user.get('role', 'N/A').upper()}")
        
        st.markdown("---")
        
        # Navigation
        pages = {
            "📊 Dashboard": "dashboard",
            "📄 Analyser Document": "analyze",
            "✅ Validation Humaine": "validation",
            "📈 Analytics": "analytics",
            "⚙️ Paramètres": "settings"
        }
        
        selected_page = st.radio("🧭 Navigation", list(pages.keys()))
        st.session_state.current_page = pages[selected_page]
        
        st.markdown("---")
        
        # Informations système
        st.subheader("🔧 Système")
        
        # Test API
        api_status = test_api_connection()
        if api_status:
            st.success("✅ API connectée")
        else:
            st.error("❌ API déconnectée")
        
        # Test Ollama
        try:
            health = make_api_request("GET", "/health")
            if health and health.get('services', {}).get('ollama', {}).get('status') == 'healthy':
                st.success("✅ Ollama connecté")
            else:
                st.warning("⚠️ Ollama déconnecté")
        except:
            st.error("❌ Statut inconnu")
        
        st.markdown("---")
        
        # Déconnexion
        if st.button("🚪 Se déconnecter", use_container_width=True):
            logout_user()

def render_dashboard():
    """Page tableau de bord"""
    st.title("📊 Tableau de Bord")
    
    # Récupérer les métriques
    metrics = make_api_request("GET", "/api/v1/analytics/dashboard")
    
    if not metrics:
        st.error("❌ Impossible de charger les métriques")
        return
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📄 Total Documents",
            metrics.get('total_documents', 0),
            delta=metrics.get('documents_this_period', 0)
        )
    
    with col2:
        st.metric(
            "🎯 Confiance Moyenne",
            f"{metrics.get('average_confidence', 0):.1%}"
        )
    
    with col3:
        st.metric(
            "⏱️ Temps Moyen",
            f"{metrics.get('average_processing_time_ms', 0)/1000:.1f}s"
        )
    
    with col4:
        st.metric(
            "🔍 À Réviser",
            metrics.get('needs_review_count', 0)
        )
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Répartition par Statut")
        status_data = metrics.get('status_distribution', [])
        if status_data:
            labels = [item['status'] for item in status_data]
            values = [item['count'] for item in status_data]
            
            import plotly.express as px
            fig = px.pie(values=values, names=labels, title="Documents par Statut")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏷️ Résultats de Classification")
        classification_data = metrics.get('classification_results', [])
        if classification_data:
            labels = [item['result'] for item in classification_data]
            values = [item['count'] for item in classification_data]
            
            fig = px.bar(x=labels, y=values, title="Classifications")
            st.plotly_chart(fig, use_container_width=True)

def render_analyze_page():
    """Page d'analyse de documents"""
    st.title("📄 Analyser un Document")
    
    # Upload de fichier
    uploaded_file = st.file_uploader(
        "📁 Téléversez un document",
        type=ALLOWED_EXTENSIONS,
        help=f"Types supportés: {', '.join(ALLOWED_EXTENSIONS)}. Taille max: {format_file_size(UPLOAD_MAX_SIZE)}"
    )
    
    if uploaded_file is not None:
        # Vérifications
        if uploaded_file.size > UPLOAD_MAX_SIZE:
            st.error(f"❌ Fichier trop volumineux. Maximum: {format_file_size(UPLOAD_MAX_SIZE)}")
            return
        
        # Informations du fichier
        st.subheader("📋 Informations du Fichier")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Nom:** {uploaded_file.name}")
        with col2:
            st.write(f"**Taille:** {format_file_size(uploaded_file.size)}")
        with col3:
            st.write(f"**Type:** {uploaded_file.type}")
        
        # Bouton d'analyse
        if st.button("🚀 Lancer l'Analyse", type="primary", use_container_width=True):
            with st.spinner("📡 Analyse en cours... Cela peut prendre 1-2 minutes"):
                # Préparer le fichier pour l'upload
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                
                # Faire la requête d'upload
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/documents/upload",
                        files=files,
                        headers={"Authorization": f"Bearer {st.session_state.token}"},
                        timeout=120
                    )
                    
                    if response.status_code == 202:
                        result = response.json()
                        document_id = result.get('document_id')
                        
                        st.success("✅ Document reçu ! Analyse en cours...")
                        
                        # Polling pour attendre le résultat
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i in range(60):  # 60 secondes max
                            time.sleep(2)
                            progress_bar.progress((i + 1) / 60)
                            status_text.text(f"Analyse en cours... {i*2}s")
                            
                            # Vérifier le statut
                            doc_info = make_api_request("GET", f"/api/v1/documents/{document_id}")
                            if doc_info and doc_info.get('status') in ['completed', 'needs_review']:
                                progress_bar.progress(1.0)
                                status_text.text("✅ Analyse terminée !")
                                
                                # Afficher les résultats
                                st.subheader("🎯 Résultats de l'Analyse")
                                if 'classification' in doc_info and doc_info['classification']:
                                    display_classification_result(doc_info['classification'])
                                else:
                                    st.warning("⚠️ Aucune classification disponible")
                                break
                        else:
                            st.warning("⏱️ Timeout: L'analyse prend plus de temps que prévu")
                    
                    else:
                        st.error(f"❌ Erreur lors de l'upload: {response.text}")
                        
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse: {str(e)}")

def render_validation_page():
    """Page de validation humaine"""
    st.title("✅ Validation Humaine")
    
    # Récupérer les documents en attente
    pending = make_api_request("GET", "/api/v1/validation/pending")
    
    if not pending:
        st.error("❌ Impossible de charger les validations en attente")
        return
    
    documents = pending.get('pending_documents', [])
    
    if not documents:
        st.info("🎉 Aucun document en attente de validation !")
        return
    
    st.write(f"📋 **{len(documents)} document(s)** en attente de validation")
    
    # Liste des documents
    for i, doc in enumerate(documents):
        with st.expander(f"📄 {doc['filename']} - Priorité: {doc['priority'].upper()}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Uploadé le:** {doc['upload_date'][:10]}")
                st.write(f"**Classification IA:** {doc['classification']['result']}")
                st.write(f"**Confiance:** {doc['classification']['confidence_score']:.1%}")
                
                if doc['classification']['justification']:
                    st.write("**Justification:**")
                    st.write(doc['classification']['justification'])
            
            with col2:
                st.write(f"**Temps estimé:** {doc['estimated_review_time']}")
                
                # Formulaire de validation
                with st.form(f"validation_form_{doc['document_id']}"):
                    decision = st.radio(
                        "Votre décision:",
                        ["RECEVABLE", "IRRECEVABLE"],
                        key=f"decision_{doc['document_id']}"
                    )
                    
                    notes = st.text_area(
                        "Notes (optionnel):",
                        key=f"notes_{doc['document_id']}",
                        height=100
                    )
                    
                    if st.form_submit_button("✅ Valider", type="primary"):
                        validation_data = {
                            "validated_result": decision,
                            "notes": notes
                        }
                        
                        result = make_api_request(
                            "POST",
                            f"/api/v1/validation/validate/{doc['classification']['id']}",
                            json=validation_data
                        )
                        
                        if result:
                            st.success("✅ Validation enregistrée !")
                            st.rerun()

def render_analytics_page():
    """Page d'analytics avancées"""
    st.title("📈 Analytics Avancées")
    
    # Métriques de performance
    performance = make_api_request("GET", "/api/v1/analytics/performance")
    
    if performance:
        st.subheader("⚡ Performance du Système")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Taux de Succès", f"{performance.get('success_rate_percent', 0):.1f}%")
        with col2:
            percentiles = performance.get('processing_time_percentiles_ms', {})
            st.metric("Temps Médian", f"{percentiles.get('p50', 0)/1000:.1f}s")
        with col3:
            st.metric("P95", f"{percentiles.get('p95', 0)/1000:.1f}s")

def render_settings_page():
    """Page de paramètres"""
    st.title("⚙️ Paramètres")
    
    st.subheader("🔧 Configuration Système")
    
    # Informations système
    info = make_api_request("GET", "/info")
    if info:
        st.json(info)

# ===== FONCTION PRINCIPALE =====

def main():
    """Fonction principale de l'application"""
    # Vérifier l'authentification
    if 'token' not in st.session_state:
        render_login_page()
        return
    
    # Interface principale
    render_sidebar()
    
    # Routage des pages
    current_page = st.session_state.get('current_page', 'dashboard')
    
    if current_page == 'dashboard':
        render_dashboard()
    elif current_page == 'analyze':
        render_analyze_page()
    elif current_page == 'validation':
        render_validation_page()
    elif current_page == 'analytics':
        render_analytics_page()
    elif current_page == 'settings':
        render_settings_page()

if __name__ == "__main__":
    main()