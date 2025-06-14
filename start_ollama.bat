@echo off
echo ========================================
echo    DEMARRAGE OLLAMA - SAC-DJ
echo ========================================
echo.

REM V‚rifier si Ollama est install‚
where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ? ERREUR: Ollama n'est pas install‚ ou pas dans le PATH
    echo.
    echo ?? T‚l‚chargez Ollama depuis: https://ollama.ai
    echo    Puis relancez ce script
    pause
    exit /b 1
)

echo ? Ollama trouv‚, d‚marrage du serveur...
echo.
echo ?? Le serveur Ollama va d‚marrer sur http://localhost:11434
echo ?? Laissez cette fenˆtre ouverte pendant l'utilisation
echo.

REM D‚marrer Ollama
ollama serve

echo.
echo ?? Ollama s'est arrˆt‚
pause
