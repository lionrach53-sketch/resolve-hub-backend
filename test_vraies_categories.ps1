$ErrorActionPreference = 'Stop'

Write-Host "🧪 TEST DES VRAIES CATEGORIES DU RAG`n" -ForegroundColor Green

# Test 1: Plantes Medicinales
Write-Host "1️⃣  Test: Plantes Medicinales" -ForegroundColor Yellow
$body1 = @{
    message = "Quelle plante utilise-t-on pour soigner les maux d'estomac ?"
    category = "Plantes Medicinales"
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri 'http://localhost:8000/api/chat/guest' -Method Post -Headers @{'Content-Type'='application/json'} -Body $body1 -TimeoutSec 10
    Write-Host "✅ Réponse:" -ForegroundColor Green
    Write-Host $response1.response -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
}

# Test 2: Transformation PFNL
Write-Host "`n2️⃣  Test: Transformation PFNL" -ForegroundColor Yellow
$body2 = @{
    message = "Comment transformer la noix de karité en beurre ?"
    category = "Transformation PFNL"
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri 'http://localhost:8000/api/chat/guest' -Method Post -Headers @{'Content-Type'='application/json'} -Body $body2 -TimeoutSec 10
    Write-Host "✅ Réponse:" -ForegroundColor Green
    Write-Host $response2.response -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
}

# Test 3: Civisme
Write-Host "`n3️⃣  Test: Civisme" -ForegroundColor Yellow
$body3 = @{
    message = "Quels sont mes devoirs de citoyen ?"
    category = "Civisme"
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri 'http://localhost:8000/api/chat/guest' -Method Post -Headers @{'Content-Type'='application/json'} -Body $body3 -TimeoutSec 10
    Write-Host "✅ Réponse:" -ForegroundColor Green
    Write-Host $response3.response -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
}

Write-Host "`n✅ Tests terminés!" -ForegroundColor Green
