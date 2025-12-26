@echo off
chcp 65001

REM Se placer dans le dossier du script (backend)
cd /d "%~dp0"

echo ========================================
echo   IA SOUVERAINE BURKINA - BACKEND ADMIN
echo ========================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou n'est pas dans le PATH
    pause
    exit /b 1
)

REM Vérifier si venv existe
if not exist "venv" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
)

echo 🔄 Activation de l'environnement...
call venv\Scripts\activate

echo 📚 Installation des dépendances...
python -m pip install -r requirements.txt

echo.
echo 🚀 Démarrage du serveur backend...
echo 📍 API: http://localhost:8000
echo 📍 Docs: http://localhost:8000/docs
echo 📍 Health: http://localhost:8000/health
echo.
echo ⚠️  Clé d'administration: admin-souverain-burkina-2024
echo ========================================
echo.

python main.py

pause