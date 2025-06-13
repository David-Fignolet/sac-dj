import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def generate_sample_data():
    """Génère des données de démonstration pour le dashboard"""
    dates = [datetime.now() - timedelta(days=i) for i in range(30, -1, -1)]
    return pd.DataFrame({
        "Date": dates,
        "Dossiers traités": [max(10, min(30, 20 + (i-15)**2//10)) for i in range(31)],
        "Temps moyen (min)": [max(1, 5 - i/10) for i in range(31)],
        "Taux de réussite": [max(0.8, 0.9 + (i-15)*0.003) for i in range(31)],
        "Type de décision": ["Recevable" if x > 0.6 else "Irrecevable" for x in [0.7, 0.8, 0.9, 0.6, 0.5] * 6 + [0.7]]
    })

def render():
    st.title("📊 Tableau de bord CSPE")
    st.write("Vue d'ensemble des analyses et statistiques")
    
    # KPI Cards
    st.subheader("Indicateurs clés")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Dossiers traités", "742", "+12% vs mois dernier")
    
    with col2:
        st.metric("Temps moyen", "3.2 min", "-1.1 min")
    
    with col3:
        st.metric("Taux de précision", "94.5%", "+2.3%")
    
    # Graphiques
    st.subheader("Activité récente")
    df = generate_sample_data()
    
    # Graphique d'activité
    fig1 = px.line(
        df, x="Date", y="Dossiers traités",
        title="Volume de dossiers traités",
        labels={"Dossiers traités": "Nombre de dossiers"}
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Graphique de répartition
    col1, col2 = st.columns(2)
    
    with col1:
        fig2 = px.pie(
            df, names="Type de décision",
            title="Répartition des décisions"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        fig3 = px.bar(
            df, x="Date", y="Temps moyen (min)",
            title="Temps de traitement moyen"
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # Dernières activités
    st.subheader("Dernières activités")
    st.dataframe(
        df[["Date", "Dossiers traités", "Taux de réussite"]].tail(5),
        hide_index=True
    )