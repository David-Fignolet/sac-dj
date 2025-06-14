@echo off
echo ========================================
echo     VERIFICATION STATUT - SAC-DJ
echo ========================================
echo.

echo ?? V�rification des composants...
echo.

REM V�rifier Python
echo [Python]
python --version 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ? Python install�
) else (
    echo ? Python non trouv�
)

REM V�rifier l'environnement virtuel  
echo.
echo [Environnement virtuel]
if exist venv (
    echo ? Environnement virtuel pr�sent
) else (
    echo ? Environnement virtuel manquant
)

REM V�rifier Ollama
echo.
echo [Ollama]
where ollama >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ? Ollama install�
    
    REM V�rifier si Ollama fonctionne
    curl -f http://localhost:11434/api/tags >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo ? Ollama fonctionne
        
        REM V�rifier le mod�le Mistral
        curl -s http://localhost:11434/api/tags | findstr "mistral" >nul
        if %ERRORLEVEL% EQU 0 (
            echo ? Mod�le Mistral install�
        ) else (
            echo ? Mod�le Mistral manquant
        )
    ) else (
        echo ? Ollama ne fonctionne pas
    )
) else (
    echo ? Ollama non install�
)

REM V�rifier l'API
echo.
echo [API FastAPI]
curl -f http://localhost:8000 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ? API fonctionne sur http://localhost:8000
) else (
    echo ? API non accessible
)

REM V�rifier l'interface
echo.
echo [Interface Streamlit]
curl -f http://localhost:8501 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ? Interface fonctionne sur http://localhost:8501
) else (
    echo ? Interface non accessible
)

REM V�rifier les fichiers
echo.
echo [Fichiers de configuration]
if exist .env (
    echo ? Fichier .env pr�sent
) else (
    echo ? Fichier .env manquant
)

if exist uploads (
    echo ? Dossier uploads pr�sent
) else (
    echo ? Dossier uploads manquant
)

echo.
echo ========================================
echo      VERIFICATION TERMIN�E
echo ========================================
pause
