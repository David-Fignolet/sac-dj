@echo off
echo ========================================
echo     INSTALLATION SAC-DJ - WINDOWS
echo ========================================
echo.

REM VÇrifier Python
echo ?? VÇrification de Python...
python --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ? ERREUR: Python n'est pas installÇ ou pas dans le PATH
    echo.
    echo ?? Installez Python 3.11+ depuis: https://python.org
    pause
    exit /b 1
)

echo ? Python trouvÇ

REM CrÇer l'environnement virtuel
echo.
echo ?? CrÇation de l'environnement virtuel...
if exist venv (
    echo ?? L'environnement virtuel existe dÇjÖ, suppression...
    rmdir /s /q venv
)

python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ? Erreur lors de la crÇation de l'environnement virtuel
    pause
    exit /b 1
)

echo ? Environnement virtuel crÇÇ

REM Activer l'environnement virtuel
echo.
echo ?? Activation de l'environnement virtuel...
call venv\Scripts\activate

REM Mettre Ö jour pip
echo.
echo ?? Mise Ö jour de pip...
python -m pip install --upgrade pip

REM Installer les dÇpendances
echo.
echo ?? Installation des dÇpendances (cela peut prendre quelques minutes)...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo ? Erreur lors de l'installation des dÇpendances
    pause
    exit /b 1
)

echo ? DÇpendances installÇes

REM Installer le modäle spaCy
echo.
echo ?? Installation du modäle franáais spaCy...
python -m spacy download fr_core_news_lg

REM Copier le fichier .env
echo.
echo ?? Configuration de l'environnement...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo ? Fichier .env crÇÇ depuis .env.example
        echo ?? IMPORTANT: êditez le fichier .env pour personnaliser la configuration
    ) else (
        echo ? Fichier .env.example non trouvÇ
    )
) else (
    echo ? Fichier .env existe dÇjÖ
)

REM CrÇer le dossier uploads
echo.
echo ?? CrÇation des dossiers nÇcessaires...
if not exist uploads mkdir uploads
echo ? Dossier uploads crÇÇ

REM Initialiser la base de donnÇes
echo.
echo ??? Initialisation de la base de donnÇes...
python init_db.py

if %ERRORLEVEL% EQU 0 (
    echo ? Base de donnÇes initialisÇe
) else (
    echo ?? Erreur lors de l'initialisation de la base de donnÇes (non critique)
)

echo.
echo ========================================
echo        INSTALLATION TERMINêE! 
echo ========================================
echo.
echo ?? Prochaines Çtapes:
echo.
echo 1. Lancez start_ollama.bat (dans un terminal sÇparÇ)
echo 2. Lancez install_model.bat (pour tÇlÇcharger Mistral)
echo 3. Lancez start_api.bat (pour dÇmarrer l'API)
echo 4. Lancez start_frontend.bat (pour dÇmarrer l'interface)
echo.
echo ?? Consultez le README.md pour plus d'informations
echo.
pause
