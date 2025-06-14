@echo off
echo ========================================
echo     DEMARRAGE API - SAC-DJ
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

REM V‚rifier que les d‚pendances sont install‚es
echo.
echo ?? V‚rification des d‚pendances...
python -c "import fastapi, uvicorn" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ? ERREUR: D‚pendances manquantes
    echo.
    echo ?? Lancez setup.bat pour installer les d‚pendances
    pause
    exit /b 1
)

echo ? D‚pendances OK

REM V‚rifier Ollama
echo.
echo ?? V‚rification d'Ollama...
curl -f http://localhost:11434/api/tags >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ?? ATTENTION: Ollama ne semble pas fonctionner
    echo.
    echo ?? Assurez-vous que start_ollama.bat est lanc‚ dans un autre terminal
    echo ?? L'API va quand mˆme d‚marrer, mais les analyses IA ne fonctionneront pas
    echo.
    timeout /t 3 >nul
)

REM D‚marrer l'API
echo.
echo ?? D‚marrage de l'API FastAPI...
echo.
echo ?? L'API sera accessible sur: http://localhost:8000
echo ?? Documentation interactive: http://localhost:8000/docs
echo ?? Mode rechargement automatique activ‚
echo.
echo ?? Gardez cette fenˆtre ouverte pendant l'utilisation
echo ?? Appuyez sur Ctrl+C pour arrˆter l'API
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo ?? L'API s'est arrˆt‚e
pause
