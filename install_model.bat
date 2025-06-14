@echo off
echo ========================================
echo   INSTALLATION MODELE MISTRAL - SAC-DJ
echo ========================================
echo.

REM VÇrifier si Ollama fonctionne
echo ?? VÇrification d'Ollama...
curl -f http://localhost:11434/api/tags >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ? ERREUR: Ollama ne fonctionne pas
    echo.
    echo ?? Lancez d'abord start_ollama.bat dans un autre terminal
    pause
    exit /b 1
)

echo ? Ollama fonctionne!
echo.

echo ?? TÇlÇchargement du modäle Mistral 7B (cela peut prendre 5-10 minutes)...
echo ?? Taille: ~4.1 GB
echo.

REM TÇlÇcharger Mistral
ollama pull mistral:7b-instruct

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ? Modäle Mistral installÇ avec succäs!
    echo.
    echo ?? Test du modäle...
    echo.
    
    REM Test du modäle
    echo {"model":"mistral:7b-instruct","prompt":"Bonjour, peux-tu rÇpondre 'OK' pour confirmer que tu fonctionnes?","stream":false} | curl -X POST -H "Content-Type: application/json" -d @- http://localhost:11434/api/generate
    
    echo.
    echo.
    echo ?? Installation terminÇe! Vous pouvez maintenant utiliser SAC-DJ.
) else (
    echo.
    echo ? Erreur lors de l'installation du modäle
)

echo.
pause
