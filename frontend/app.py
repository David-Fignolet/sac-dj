import streamlit as st
import requests
import os

# Configuration de la page
st.set_page_config(
    page_title="SAC-DJ | Agent d'Analyse",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration de l'API
API_BASE_URL = "http://localhost:8000"  # Mettez votre URL d'API ici

# Fonction de connexion simplifiée
def login(email, password):
    """Fonction de connexion avec des identifiants de test"""
    if email == "admin@example.com" and password == "admin123":
        st.session_state.token = "demo_token"
        st.session_state.user = {
            "email": email,
            "full_name": "Administrateur Test",
            "role": "admin"
        }
        return True
    return False

# Interface principale
st.title("🏛️ SAC-DJ : Système d'Analyse Cognitive")

# Gestion de la connexion
if 'token' not in st.session_state:
    # Formulaire de connexion
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")
        if submitted:
            if login(email, password):
                st.success("Connexion réussie !")
                st.rerun()  # Utilisation de rerun() au lieu de experimental_rerun()
            else:
                st.error("Identifiants incorrects")
else:
    # Menu de navigation
    with st.sidebar:
        st.header(f"Bienvenue, {st.session_state.user['full_name']}")
        st.write(f"Rôle : **{st.session_state.user['role'].upper()}**")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📄 Classifier un Document", "✅ Validation Humaine"]
        )
        
        st.markdown("---")
        if st.button("Se déconnecter"):
            del st.session_state.token
            st.rerun()  # Utilisation de rerun() au lieu de experimental_rerun()
    
    # Affichage de la page sélectionnée
    if page == "📊 Dashboard":
        st.header("Tableau de bord")
        st.info("Cette fonctionnalité est en cours de développement.")
        
    elif page == "📄 Classifier un Document":
        st.header("Classer un document")
        uploaded_file = st.file_uploader(
            "Téléversez un document (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt']
        )
        
        if uploaded_file is not None:
            if st.button("Analyser le document"):
                with st.spinner("Analyse en cours..."):
                    # Ici, vous appellerez votre API pour l'analyse
                    st.success("Analyse terminée !")
                    st.json({
                        "resultat": "RECEVABLE",
                        "confiance": 0.95,
                        "details": "Analyse détaillée ici..."
                    })
    
    elif page == "✅ Validation Humaine":
        st.header("Validation humaine")
        st.info("Cette fonctionnalité est en cours de développement.")