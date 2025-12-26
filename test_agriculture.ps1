Write-Host "`n🧪 TEST AGRICULTURE`n" -ForegroundColor Yellow

$body = @{
    message = 'Quelles sont les techniques agricoles traditionnelles au Burkina Faso ?'
    category = 'agriculture'
} | ConvertTo-Json -Compress

try {
    $resp = Invoke-RestMethod -Uri 'http://localhost:8000/api/chat/guest' -Method Post -Headers @{'Content-Type'='application/json'} -Body $body -ErrorAction Stop
    
    Write-Host "`n✅ REPONSE:"-ForegroundColor Green
    Write-Host $resp.response -ForegroundColor Cyan
    
} catch {
    Write-Host "`n❌ ERREUR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
