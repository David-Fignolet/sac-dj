@echo off
echo ========================================
echo    MISE A JOUR SYSTEME - SAC-DJ
echo ========================================
echo.

REM Vérifier que nous sommes dans le bon répertoire
if not exist "app\main.py" (
    echo ❌ ERREUR: Vous devez être dans le répertoire racine du projet SAC-DJ
    echo.
    echo 📂 Assurez-vous d'être dans le dossier contenant app\main.py
    pause
    exit /b 1
)

echo 🔍 Vérification de l'état actuel du système...
echo.

REM Vérifier que Git est disponible
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERREUR: Git n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

REM Vérifier l'environnement virtuel
if not exist venv (
    echo ❌ ERREUR: Environnement virtuel non trouvé
    echo.
    echo 🔧 Exécutez d'abord setup.bat pour installer le projet
    pause
    exit /b 1
)

echo ✅ Environnement virtuel trouvé
echo.

REM Activer l'environnement virtuel
echo 🔧 Activation de l'environnement virtuel...
call venv\Scripts\activate

REM Afficher la version actuelle
echo 📊 État actuel:
python --version
pip --version

REM Vérifier les modifications Git
echo.
echo 🔍 Vérification des mises à jour Git...
git fetch

REM Comparer avec la branche distante
for /f "tokens=*" %%i in ('git rev-list HEAD...origin/main --count 2^>nul') do set COMMITS_BEHIND=%%i

if "%COMMITS_BEHIND%"=="0" (
    echo ✅ Le projet est à jour avec la branche principale
) else (
    echo ⚠️ %COMMITS_BEHIND% nouveaux commits disponibles
    echo.
    
    choice /c YN /m "Voulez-vous mettre à jour le code depuis Git (Y/N)?"
    if errorlevel 2 goto :skip_git_update
    if errorlevel 1 goto :git_update
)

goto :skip_git_update

:git_update
echo.
echo 📥 Mise à jour du code depuis Git...
git stash
git pull origin main
git stash pop

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors de la mise à jour Git
    echo 💡 Vous devrez peut-être résoudre des conflits manuellement
    pause
)

:skip_git_update

REM Mettre à jour les dépendances Python
echo.
echo 📦 Vérification des mises à jour des dépendances...

REM Sauvegarder les dépendances actuelles
pip freeze > requirements_current.txt

REM Mettre à jour pip
echo 🔄 Mise à jour de pip...
python -m pip install --upgrade pip

REM Mettre à jour les dépendances
echo 🔄 Mise à jour des dépendances Python...
pip install -r requirements.txt --upgrade

REM Vérifier les changements
echo.
echo 📊 Comparaison des dépendances:
fc requirements_current.txt <(pip freeze) >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Aucune mise à jour de dépendances
) else (
    echo ✅ Dépendances mises à jour
)

REM Nettoyer le fichier temporaire
del requirements_current.txt >nul 2>nul

REM Vérifier le modèle spaCy
echo.
echo 🧠 Vérification du modèle spaCy...
python -c "import spacy; spacy.load('fr_core_news_lg')" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ Modèle spaCy manquant, installation...
    python -m spacy download fr_core_news_lg
) else (
    echo ✅ Modèle spaCy français disponible
)

REM Vérifier Ollama et le modèle Mistral
echo.
echo 🤖 Vérification d'Ollama et Mistral...
curl -f http://localhost:11434/api/tags >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Ollama accessible
    
    REM Vérifier si Mistral est installé
    curl -s http://localhost:11434/api/tags | findstr "mistral" >nul
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Modèle Mistral disponible
        
        REM Proposer la mise à jour du modèle
        choice /c YN /m "Voulez-vous mettre à jour le modèle Mistral (Y/N)?"
        if errorlevel 1 (
            echo 📥 Mise à jour du modèle Mistral...
            ollama pull mistral:7b-instruct
        )
    ) else (
        echo ⚠️ Modèle Mistral manquant
        choice /c YN /m "Voulez-vous installer le modèle Mistral (Y/N)?"
        if errorlevel 1 (
            echo 📥 Installation du modèle Mistral...
            ollama pull mistral:7b-instruct
        )
    )
) else (
    echo ⚠️ Ollama non accessible
    echo 💡 Démarrez Ollama avec start_ollama.bat
)

REM Mettre à jour la base de données si nécessaire
echo.
echo 🗄️ Vérification de la base de données...
python -c "
try:
    from app.database import SessionLocal
    db = SessionLocal()
    db.execute('SELECT 1')
    db.close()
    print('✅ Base de données accessible')
except Exception as e:
    print('⚠️ Problème de base de données:', str(e))
    print('💡 Exécutez init_db.py si nécessaire')
"

REM Effectuer des tests de validation
echo.
choice /c YN /m "Voulez-vous exécuter les tests de validation (Y/N)?"
if errorlevel 1 (
    echo 🧪 Exécution des tests de validation...
    python validate_system.py
)

REM Résumé
echo.
echo ========================================
echo      MISE A JOUR TERMINÉE
echo ========================================
echo.
echo 🎉 Le système SAC-DJ a été mis à jour !
echo.
echo 🚀 Prochaines étapes:
echo 1. Redémarrez les services si ils étaient actifs
echo 2. Testez l'application sur http://localhost:8501
echo 3. Vérifiez les nouvelles fonctionnalités
echo.
echo 📋 Services à redémarrer:
echo    • start_ollama.bat
echo    • start_api.bat  
echo    • start_frontend.bat
echo.
echo    OU utilisez: start_all.bat
echo.

REM Proposer de redémarrer les services
choice /c YN /m "Voulez-vous redémarrer tous les services maintenant (Y/N)?"
if errorlevel 1 (
    echo.
    echo 🔄 Redémarrage des services...
    
    REM Arrêter les services existants (si ils tournent)
    taskkill /F /IM ollama.exe >nul 2>nul
    taskkill /F /IM python.exe >nul 2>nul
    timeout /t 2 >nul
    
    REM Redémarrer tout
    start "SAC-DJ - Tous Services" cmd /k start_all.bat
    
    echo ✅ Services redémarrés dans une nouvelle fenêtre
)

echo.
pause