@echo off
chcp 65001 >nul
title 🇧🇫 INGESTION IA MULTILINGUE BURKINA

echo.
echo =========================================
echo    INGESTION IA SOUVERAINE BURKINA
echo    Version Multilingue (FR/MO/DI)
echo =========================================
echo.

rem Vérifier PowerShell
powershell -Command "Write-Host '✓ PowerShell OK' -ForegroundColor Green" >nul 2>&1
if errorlevel 1 (
    echo ❌ PowerShell n'est pas disponible
    echo Installez PowerShell 5.1 ou supérieur
    pause
    exit /b 1
)

rem Vérifier le fichier JSON
if not exist "connaissances.json" (
    echo ❌ Fichier connaissances.json introuvable
    echo.
    echo Créez un fichier connaissances.json avec la structure :
    echo [
    echo   {
    echo     "categorie": "Exemple",
    echo     "langues": {
    echo       "fr": { "question": "...", "reponse": "..." },
    echo       "mo": { "question": "...", "reponse": "..." },
    echo       "di": { "question": "...", "reponse": "..." }
    echo     }
    echo   }
    echo ]
    pause
    exit /b 1
)

rem Lancer PowerShell avec la bonne politique d'exécution
echo ✅ Tout est prêt
echo.
echo Lancement de l'ingestion...
echo.

powershell -ExecutionPolicy Bypass -NoProfile -File ingest.ps1

if errorlevel 1 (
    echo.
    echo ❌ L'ingestion a échoué
    pause
    exit /b 1
)

exit /b 0