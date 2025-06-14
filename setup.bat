@echo off
echo ========================================
echo     INSTALLATION SAC-DJ - WINDOWS
echo ========================================
echo.

REM V�rifier Python
echo ?? V�rification de Python...
python --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ? ERREUR: Python n'est pas install� ou pas dans le PATH
    echo.
    echo ?? Installez Python 3.11+ depuis: https://python.org
    pause
    exit /b 1
)

echo ? Python trouv�

REM Cr�er l'environnement virtuel
echo.
echo ?? Cr�ation de l'environnement virtuel...
if exist venv (
    echo ?? L'environnement virtuel existe d�j�, suppression...
    rmdir /s /q venv
)

python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ? Erreur lors de la cr�ation de l'environnement virtuel
    pause
    exit /b 1
)

echo ? Environnement virtuel cr��

REM Activer l'environnement virtuel
echo.
echo ?? Activation de l'environnement virtuel...
call venv\Scripts\activate

REM Mettre � jour pip
echo.
echo ?? Mise � jour de pip...
python -m pip install --upgrade pip

REM Installer les d�pendances
echo.
echo ?? Installation des d�pendances (cela peut prendre quelques minutes)...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo ? Erreur lors de l'installation des d�pendances
    pause
    exit /b 1
)

echo ? D�pendances install�es

REM Installer le mod�le spaCy
echo.
echo ?? Installation du mod�le fran�ais spaCy...
python -m spacy download fr_core_news_lg

REM Copier le fichier .env
echo.
echo ?? Configuration de l'environnement...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo ? Fichier .env cr�� depuis .env.example
        echo ?? IMPORTANT: �ditez le fichier .env pour personnaliser la configuration
    ) else (
        echo ? Fichier .env.example non trouv�
    )
) else (
    echo ? Fichier .env existe d�j�
)

REM Cr�er le dossier uploads
echo.
echo ?? Cr�ation des dossiers n�cessaires...
if not exist uploads mkdir uploads
echo ? Dossier uploads cr��

REM Initialiser la base de donn�es
echo.
echo ??? Initialisation de la base de donn�es...
python init_db.py

if %ERRORLEVEL% EQU 0 (
    echo ? Base de donn�es initialis�e
) else (
    echo ?? Erreur lors de l'initialisation de la base de donn�es (non critique)
)

echo.
echo ========================================
echo        INSTALLATION TERMIN�E! 
echo ========================================
echo.
echo ?? Prochaines �tapes:
echo.
echo 1. Lancez start_ollama.bat (dans un terminal s�par�)
echo 2. Lancez install_model.bat (pour t�l�charger Mistral)
echo 3. Lancez start_api.bat (pour d�marrer l'API)
echo 4. Lancez start_frontend.bat (pour d�marrer l'interface)
echo.
echo ?? Consultez le README.md pour plus d'informations
echo.
pause
