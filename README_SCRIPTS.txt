📋 GUIDE D'UTILISATION - SAC-DJ

1. INSTALLATION
   -------------
   - Installez Python 3.11+ depuis https://python.org
   - Téléchargez et installez Ollama depuis https://ollama.ai
   - Exécutez setup.bat pour configurer l'environnement

2. DÉMARRAGE RAPIDE
   ----------------
   - Lancez start_all.bat pour démarrer tous les composants
   - OU démarrez manuellement dans l'ordre :
     1. start_ollama.bat (dans un terminal séparé)
     2. install_model.bat (une seule fois)
     3. start_api.bat (dans un terminal séparé)
     4. start_frontend.bat (dans un terminal séparé)

3. VÉRIFICATION
   ------------
   - Utilisez check_status.bat pour vérifier l'état des composants
   - L'interface sera disponible sur http://localhost:8501
   - L'API sera disponible sur http://localhost:8000

4. DÉPANNAGE
   ---------
   - Si Ollama ne se lance pas : vérifiez l'installation
   - Si l'API ne démarre pas : vérifiez les dépendances avec setup.bat
   - Consultez les logs dans chaque fenêtre de terminal

5. ARRÊT
   -----
   - Fermez toutes les fenêtres de terminal pour arrêter les services

📝 NOTE : Assurez-vous que tous les services ont terminé leur démarrage avant d'utiliser l'application.
