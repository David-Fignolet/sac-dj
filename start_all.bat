@echo off
echo ========================================
echo    DEMARRAGE COMPLET - SAC-DJ
echo ========================================
echo.

echo ?? Ce script va dÇmarrer tous les composants de SAC-DJ
echo.
echo ?? Composants qui seront lancÇs:
echo    1. Ollama (serveur IA)
echo    2. API FastAPI (backend)
echo    3. Interface Streamlit (frontend)
echo.
echo ?? 3 fenàtres de terminal vont s'ouvrir
echo ?? Gardez-les toutes ouvertes pendant l'utilisation
echo.

pause

echo.
echo ?? Lancement d'Ollama...
start "SAC-DJ - Ollama" cmd /k start_ollama.bat

echo ? Attente 5 secondes pour qu'Ollama dÇmarre...
timeout /t 5 >nul

echo.
echo ?? Lancement de l'API...
start "SAC-DJ - API" cmd /k start_api.bat

echo ? Attente 3 secondes pour que l'API dÇmarre...
timeout /t 3 >nul

echo.
echo ?? Lancement de l'interface...
start "SAC-DJ - Frontend" cmd /k start_frontend.bat

echo.
echo ========================================
echo     TOUS LES COMPOSANTS DêMARRêS!
echo ========================================
echo.
echo ?? Accäs Ö l'application:
echo     Interface: http://localhost:8501
echo     API: http://localhost:8000
echo     Documentation API: http://localhost:8000/docs
echo.
echo ?? Pour arràter: fermez toutes les fenàtres de terminal
echo.
pause
