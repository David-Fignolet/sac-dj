@echo off
echo ========================================
echo     VERIFICATION STATUT - SAC-DJ
echo ========================================
echo.

echo ?? VÇrification des composants...
echo.

REM VÇrifier Python
echo [Python]
python --version 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ? Python installÇ
) else (
    echo ? Python non trouvÇ
)

REM VÇrifier l'environnement virtuel  
echo.
echo [Environnement virtuel]
if exist venv (
    echo ? Environnement virtuel prÇsent
) else (
    echo ? Environnement virtuel manquant
)

REM VÇrifier Ollama
echo.
echo [Ollama]
where ollama >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ? Ollama installÇ
    
    REM VÇrifier si Ollama fonctionne
    curl -f http://localhost:11434/api/tags >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo ? Ollama fonctionne
        
        REM VÇrifier le modäle Mistral
        curl -s http://localhost:11434/api/tags | findstr "mistral" >nul
        if %ERRORLEVEL% EQU 0 (
            echo ? Modäle Mistral installÇ
        ) else (
            echo ? Modäle Mistral manquant
        )
    ) else (
        echo ? Ollama ne fonctionne pas
    )
) else (
    echo ? Ollama non installÇ
)

REM VÇrifier l'API
echo.
echo [API FastAPI]
curl -f http://localhost:8000 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ? API fonctionne sur http://localhost:8000
) else (
    echo ? API non accessible
)

REM VÇrifier l'interface
echo.
echo [Interface Streamlit]
curl -f http://localhost:8501 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ? Interface fonctionne sur http://localhost:8501
) else (
    echo ? Interface non accessible
)

REM VÇrifier les fichiers
echo.
echo [Fichiers de configuration]
if exist .env (
    echo ? Fichier .env prÇsent
) else (
    echo ? Fichier .env manquant
)

if exist uploads (
    echo ? Dossier uploads prÇsent
) else (
    echo ? Dossier uploads manquant
)

echo.
echo ========================================
echo      VERIFICATION TERMINêE
echo ========================================
pause
