@echo off
echo Demarrage du backend YINGRE AI...

REM Se placer dans le dossier backend (là où se trouve ce script)
cd /d "%~dp0"

REM Utiliser le venv local du backend
venv\Scripts\python.exe -m uvicorn main:app --port 8000 --host 0.0.0.0

pause
