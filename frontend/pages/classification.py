import streamlit as st
import os
import requests
import json
from datetime import datetime
from pathlib import Path

# Configuration
UPLOAD_FOLDER = "uploads"
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

def save_uploaded_file(uploaded_file):
    """Sauvegarde le fichier uploadé et retourne le chemin"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uploaded_file.name}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def analyze_document(file_path):
    """
    Envoie le document à l'API d'analyse
    À remplacer par un appel réel à votre API
    """
    # Simulation de l'analyse
    return {
        "statut": "RECEVABLE",
        "confiance": 0.92,
        "critères": {
            "délai": {"statut": "Conforme", "détails": "Délai respecté (15 jours sur 60)"},
            "qualité": {"statut": "Conforme", "détails": "Demandeur directement concerné"},
            "objet": {"statut": "Conforme", "détails": "Objet de la contestation valide"},
            "pièces": {"statut": "Conforme", "détails": "Pièces justificatives complètes"}
        },
        "commentaires": "Le document respecte tous les critères de recevabilité."
    }

def display_analysis_result(result):
    """Affiche les résultats de l'analyse"""
    st.subheader("📋 Résultats de l'analyse")
    
    # Affichage du statut global
    if result["statut"] == "RECEVABLE":
        st.success("✅ Dossier RECEVABLE", icon="✅")
    else:
        st.error("❌ Dossier IRRECEVABLE", icon="❌")
    
    # Score de confiance
    st.metric("Niveau de confiance", f"{result['confiance']*100:.1f}%")
    
    # Détails par critère
    st.subheader("Analyse détaillée")
    for critere, details in result["critères"].items():
        with st.expander(f"🔍 {critere.capitalize()}: {details['statut']}"):
            st.write(details["détails"])
    
    # Commentaires
    st.subheader("Commentaires")
    st.info(result["commentaires"])

def render():
    st.title("📄 Classification CSPE")
    st.write("Téléchargez un document pour analyse automatique selon les critères CSPE")
    
    # Section d'upload
    uploaded_file = st.file_uploader(
        "Téléversez un document (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt']
    )
    
    if uploaded_file is not None:
        # Aperçu du fichier
        st.subheader("📎 Fichier sélectionné")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Nom du fichier:**", uploaded_file.name)
            st.write("**Taille:**", f"{uploaded_file.size / 1024:.1f} KB")
        
        # Bouton d'analyse
        if st.button("🚀 Lancer l'analyse", type="primary", use_container_width=True):
            with st.spinner("Analyse en cours..."):
                try:
                    # Sauvegarde du fichier
                    saved_path = save_uploaded_file(uploaded_file)
                    
                    # Simulation d'analyse
                    analysis_result = analyze_document(saved_path)
                    
                    # Affichage des résultats
                    display_analysis_result(analysis_result)
                    
                    # Bouton de téléchargement du rapport
                    st.download_button(
                        label="📥 Télécharger le rapport complet",
                        data=json.dumps(analysis_result, indent=2, ensure_ascii=False),
                        file_name=f"rapport_analyse_{uploaded_file.name}.json",
                        mime="application/json"
                    )
                    
                except Exception as e:
                    st.error(f"Erreur lors de l'analyse: {str(e)}")
                    st.exception(e)