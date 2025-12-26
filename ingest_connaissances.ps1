# =========================
# CONFIGURATION
# =========================
$ApiUrl = "http://localhost:8000/admin/ingest"
$ApiKey = "expert-burkina-2024"

$Headers = @{
    "Content-Type"  = "application/json"
    "Authorization" = "Bearer $ApiKey"
}

# =========================
# DONNÉES À INGÉRER
# =========================
$Connaissances = @(
    @{
        "Categorie" = "Culture générale"
        "Question/Titre" = "Pourquoi le pays s'appelle Burkina Faso ?"
        "Réponse/Contenu" = "Le Burkina Faso signifie « le pays des hommes intègres ». Ce nom a été adopté en 1984 sous Thomas Sankara."
    },
    @{
        "Categorie" = "Culture générale"
        "Question/Titre" = "Quel est le rôle de la chefferie traditionnelle ?"
        "Réponse/Contenu" = "La chefferie traditionnelle assure la médiation sociale, la gestion des coutumes et la cohésion communautaire."
    },
    @{
        "Categorie" = "Agriculture"
        "Question/Titre" = "Qu'est-ce que la striure du maïs ?"
        "Réponse/Contenu" = "La striure du maïs est une maladie virale qui jaunit les feuilles et réduit fortement les rendements."
    },
    @{
        "Categorie" = "Agriculture"
        "Question/Titre" = "Qu'est-ce que la chenille légionnaire ?"
        "Réponse/Contenu" = "La chenille légionnaire est un ravageur du maïs très destructeur pour les cultures."
    },
    @{
        "Categorie" = "Santé"
        "Question/Titre" = "Qu'est-ce que le paludisme ?"
        "Réponse/Contenu" = "Le paludisme est une maladie parasitaire transmise par les moustiques, très répandue au Burkina Faso."
    },
    @{
        "Categorie" = "Santé"
        "Question/Titre" = "À quoi sert le neem ?"
        "Réponse/Contenu" = "Le neem est utilisé en médecine traditionnelle pour traiter la fièvre et repousser les moustiques."
    },
    @{
        "Categorie" = "Technologie"
        "Question/Titre" = "Qu'est-ce que le mobile money ?"
        "Réponse/Contenu" = "Le mobile money permet d’envoyer, recevoir et payer de l’argent via le téléphone portable."
    },
    @{
        "Categorie" = "Technologie"
        "Question/Titre" = "Comment les drones sont-ils utilisés en agriculture ?"
        "Réponse/Contenu" = "Les drones agricoles permettent de surveiller les cultures et détecter les maladies plus tôt."
    }
)

# =========================
# ENVOI VERS L'API
# =========================
foreach ($item in $Connaissances) {
    try {
        $JsonBody = $item | ConvertTo-Json -Depth 3 -Compress

        Invoke-RestMethod `
            -Uri $ApiUrl `
            -Method POST `
            -Headers $Headers `
            -Body $JsonBody

        Write-Host "✅ Ingestion OK :" $item."Question/Titre" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Erreur sur :" $item."Question/Titre" -ForegroundColor Red
        Write-Host $_
    }
}

Write-Host "🎉 Ingestion terminée" -ForegroundColor Cyan
