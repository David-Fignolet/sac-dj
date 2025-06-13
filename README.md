# SAC-DJ - Système d'Analyse Cognitive - Dossiers Juridiques

Assistant d'analyse augmentée pour dossiers juridiques utilisant LangGraph et Mistral.

## 🚀 Fonctionnalités

- Analyse de documents juridiques complexes
- Détection automatique des éléments clés
- Génération de recommandations argumentées
- Interface utilisateur intuitive

## 🛠️ Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/TON_NOM_UTILISATEUR/sac-dj.git
   cd sac-dj
   ```

2. Copier le fichier d'environnement :
   ```bash
   cp .env.example .env
   ```

3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Lancer l'application :
   ```bash
   docker-compose up --build
   ```

## 📁 Structure du Projet

```
sac-dj/
├── .github/           # Configurations CI/CD
├── app/               # Code source principal
│   ├── api/          # Points d'API FastAPI
│   ├── core/         # Logique métier
│   ├── models/       # Modèles de données
│   └── services/     # Services métier
├── frontend/         # Interface utilisateur Streamlit
└── tests/            # Tests automatisés
```

## 📜 Licence

Ce projet est sous licence MIT.
