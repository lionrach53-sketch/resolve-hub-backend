# ingest.ps1 - VERSION MULTILINGUE 🇧🇫 - CORRIGÉ
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   INGESTION IA SOUVERAINE BURKINA" -ForegroundColor Green
Write-Host "   Version Multilingue (FR/MO/DI)" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Charger config.env
if (Test-Path "config.env") {
    Get-Content "config.env" | ForEach-Object {
        if ($_ -match "^(.*?)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
}
else {
    Write-Host "⚠️  Fichier config.env non trouvé" -ForegroundColor Yellow
    $API_URL = Read-Host "Entrez l'URL de l'API"
    $API_KEY = Read-Host "Entrez la clé API"
}

$API_URL = [Environment]::GetEnvironmentVariable("API_URL")
$API_KEY = [Environment]::GetEnvironmentVariable("API_KEY")

Write-Host "🌐 Connexion à : $API_URL" -ForegroundColor Blue
Write-Host ""

# Choisir le fichier source (priorité au format enrichi)
$sourceFile = $null
$enrichedFiles = Get-ChildItem -Filter "connaissances_enrichies*.json" -ErrorAction SilentlyContinue
if ($enrichedFiles -and $enrichedFiles.Count -gt 0) {
    $sourceFile = $enrichedFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
}
elseif (Test-Path "connaissances.json") {
    $sourceFile = Get-Item "connaissances.json"
}

if (-not $sourceFile) {
    Write-Host "❌ ERREUR : Aucun fichier de connaissances trouvé" -ForegroundColor Red
    Write-Host "   Attendu :" -ForegroundColor Yellow
    Write-Host "   - connaissances_enrichies*.json (prioritaire)" -ForegroundColor Yellow
    Write-Host "   - ou connaissances.json (format simple)" -ForegroundColor Yellow
    Pause
    exit
}

Write-Host "📁 Fichier utilisé : $($sourceFile.Name)" -ForegroundColor Cyan

# Compter les connaissances
$connaissances = Get-Content $sourceFile.FullName -Raw | ConvertFrom-Json

# Normaliser en tableau au cas où ConvertFrom-Json renvoie un seul objet
if ($connaissances -isnot [System.Collections.IEnumerable] -or $connaissances -is [string]) {
    $connaissances = @($connaissances)
}

$total = if ($null -ne $connaissances) { $connaissances.Count } else { 0 }
Write-Host "📊 $total connaissances chargées" -ForegroundColor Cyan

# Afficher un échantillon (sans emoji/accents pour éviter les bugs PowerShell)
if ($total -gt 0) {
    Write-Host ""
    Write-Host "ECHANTILLON (1ere connaissance) :" -ForegroundColor Magenta
    Write-Host "   Fichier : $($sourceFile.Name)" -ForegroundColor DarkGray
    Write-Host "   Categorie: $($connaissances[0].categorie)" -ForegroundColor Gray

    # Certaines langues peuvent être absentes ou vides, on sécurise l'accès
    $frQuestion = $connaissances[0].langues.fr.question
    $moQuestion = $connaissances[0].langues.mo.question
    $diQuestion = $connaissances[0].langues.di.question

    Write-Host "   Francais: $frQuestion" -ForegroundColor White
    Write-Host "   Moore: $moQuestion" -ForegroundColor Yellow
    Write-Host "   Dioula: $diQuestion" -ForegroundColor Green
    Write-Host ""
}

# Demander confirmation
$confirmation = Read-Host "✅ Lancer l'ingestion ? (O/N)"
if ($confirmation -notmatch "^[OoYy]") {
    Write-Host "❌ Ingestion annulée" -ForegroundColor Red
    Pause
    exit
}

# Headers
$headers = @{
    "Authorization" = "Bearer $API_KEY"
    "Content-Type"  = "application/json"
}

# Barre de progression
Write-Host ""
Write-Host "🚀 Envoi des données..." -ForegroundColor Green
Write-Host ""

    # Préparer le fichier pour l'upload multipart
    $filePath = Resolve-Path $sourceFile.FullName
    $fileName = $sourceFile.Name

    # Créer boundary pour multipart/form-data
    $boundary = [System.Guid]::NewGuid().ToString()

    # Lire le contenu du fichier en UTF-8
    $fileBytes = [System.IO.File]::ReadAllBytes($filePath)

    # Construire le body multipart en bytes UTF-8
    $LF = "`r`n"
    $encoding = [System.Text.Encoding]::UTF8

    # Header multipart
    $headerText = "--$boundary$LF" +
                  "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"$LF" +
                  "Content-Type: application/json$LF$LF"

    # Footer multipart
    $footerText = "$LF--$boundary--$LF"

    # Convertir en bytes
    $headerBytes = $encoding.GetBytes($headerText)
    $footerBytes = $encoding.GetBytes($footerText)

    # Créer un MemoryStream pour combiner les bytes
    $ms = New-Object System.IO.MemoryStream
    $ms.Write($headerBytes, 0, $headerBytes.Length)
    $ms.Write($fileBytes, 0, $fileBytes.Length)
    $ms.Write($footerBytes, 0, $footerBytes.Length)
    $bodyBytes = $ms.ToArray()
    $ms.Close()

    # Envoyer la requête avec le body en bytes
    $response = Invoke-RestMethod -Uri $API_URL -Method POST -Headers @{
        "Authorization" = "Bearer $API_KEY"
        "Content-Type"  = "multipart/form-data; boundary=$boundary"
    } -Body $bodyBytes -ErrorAction Stop

    Write-Host ""
    Write-Host "✅ SUCCÈS !" -ForegroundColor Green
    Write-Host "   $($response.ingested_count) connaissances ingérées sur $($response.total_items) items" -ForegroundColor White
    Write-Host "   Langues: Français, Mooré, Dioula" -ForegroundColor Cyan

    # Afficher les erreurs si présentes
    if ($response.errors_count -gt 0) {
        Write-Host ""
        Write-Host "⚠️  $($response.errors_count) erreurs détectées" -ForegroundColor Yellow
        if ($response.errors) {
            Write-Host "   Premières erreurs:" -ForegroundColor Gray
            $response.errors | ForEach-Object {
                Write-Host "   - Index $($_.index): $($_.error)" -ForegroundColor Gray
            }
        }
    }

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   INGESTION TERMINÉE" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Pause