@echo off
echo ========================================
echo   DEMARRAGE INTERFACE - SAC-DJ
echo ========================================
echo.

REM V‚rifier que l'environnement virtuel existe
if not exist venv (
    echo ? ERREUR: Environnement virtuel non trouv‚
    echo.
    echo ?? Lancez d'abord setup.bat pour installer le projet
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
echo ?? Activation de l'environnement virtuel...
call venv\Scripts\activate

REM V‚rifier que Streamlit est install‚
echo.
echo ?? V‚rification de Streamlit...
python -c "import streamlit" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ? ERREUR: Streamlit non install‚
    echo.
    echo ?? Lancez setup.bat pour installer les d‚pendances
    pause
    exit /b 1
)

echo ? Streamlit OK

REM V‚rifier que l'API fonctionne
echo.
echo ?? V‚rification de l'API...
curl -f http://localhost:8000 >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ?? ATTENTION: L'API ne semble pas fonctionner
    echo.
    echo ?? Assurez-vous que start_api.bat est lanc‚ dans un autre terminal
    echo ?? L'interface va quand mˆme d‚marrer, mais ne pourra pas communiquer avec l'API
    echo.
    timeout /t 3 >nul
)

REM Aller dans le dossier frontend
echo.
echo ?? Navigation vers le dossier frontend...
cd frontend

REM D‚marrer Streamlit
echo.
echo ?? D‚marrage de l'interface Streamlit...
echo.
echo ?? L'interface sera accessible sur: http://localhost:8501
echo ?? Rechargement automatique activ‚
echo.
echo ?? Gardez cette fenˆtre ouverte pendant l'utilisation
echo ?? Appuyez sur Ctrl+C pour arrˆter l'interface
echo.

streamlit run app.py --server.port 8501

echo.
echo ?? L'interface s'est arrˆt‚e
pause
