import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def generate_validation_queue():
    """Génère une file d'attente de validation simulée"""
    return [
        {
            "id": f"DOC-{1000 + i}",
            "date": (datetime.now() - timedelta(hours=i)).strftime("%d/%m/%Y %H:%M"),
            "type": "CSPE Standard",
            "confiance": f"{90 - i*2}%",
            "statut": "En attente",
            "priorité": "Haute" if i < 3 else "Moyenne"
        }
        for i in range(10)
    ]

def render_document_card(doc):
    """Affiche une carte de document à valider"""
    with st.container(border=True):
        cols = st.columns([2, 1, 1, 1, 2])
        with cols[0]:
            st.write(f"**{doc['id']}**")
            st.caption(f"Type: {doc['type']}")
        
        with cols[1]:
            st.metric("Confiance", doc["confiance"])
        
        with cols[2]:
            st.metric("Priorité", doc["priorité"])
        
        with cols[3]:
            st.metric("Statut", doc["statut"])
        
        with cols[4]:
            if st.button("📝 Valider", key=f"btn_{doc['id']}"):
                st.session_state.current_doc = doc
                st.rerun()

def render_validation_form(doc):
    """Affiche le formulaire de validation"""
    st.title(f"Validation - {doc['id']}")
    
    with st.form(key="validation_form"):
        st.write(f"**Document:** {doc['id']}")
        st.write(f"**Date de réception:** {doc['date']}")
        st.write(f"**Niveau de confiance IA:** {doc['confiance']}")
        
        # Décision
        decision = st.radio(
            "Votre décision:",
            ["✅ Valider l'analyse", "❌ Rejeter l'analyse", "🔄 Demander un avis complémentaire"],
            index=0
        )
        
        # Commentaires
        commentaires = st.text_area(
            "Commentaires (optionnel):",
            placeholder="Ajoutez des précisions sur votre décision..."
        )
        
        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Enregistrer la décision", type="primary"):
                st.success("Décision enregistrée avec succès!")
                del st.session_state.current_doc
                st.rerun()
        
        with col2:
            if st.form_submit_button("🔙 Retour à la liste"):
                del st.session_state.current_doc
                st.rerun()

def render():
    st.title("✅ Validation Humaine")
    
    # Vérifier si un document est en cours de validation
    if "current_doc" in st.session_state:
        render_validation_form(st.session_state.current_doc)
        return
    
    # Sinon afficher la file d'attente
    st.write("Liste des documents en attente de validation")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        st.selectbox("Filtrer par type", ["Tous", "CSPE Standard", "Appel", "Réclamation"])
    with col2:
        st.selectbox("Filtrer par priorité", ["Toutes", "Haute", "Moyenne", "Basse"])
    with col3:
        st.selectbox("Trier par", ["Date (récent)", "Priorité", "Confiance IA"])
    
    # Liste des documents
    documents = generate_validation_queue()
    for doc in documents:
        render_document_card(doc)
    
    # Pagination
    st.write("Page 1 sur 3")
    col1, col2, col3 = st.columns([1, 1, 10])
    with col1:
        st.button("Précédent", disabled=True)
    with col2:
        st.button("Suivant")