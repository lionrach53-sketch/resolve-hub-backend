# 🌍 INGESTION JSON MULTILINGUE - IA SOUVERAINE BURKINA

## 📋 Vue d'ensemble

Ce système permet d'ingérer des connaissances multilingues dans l'IA via :
1. **Interface Web Admin** (recommandé) - Upload via le panel admin
2. **Script Batch** - Ingestion automatique depuis la ligne de commande

---

## 🎯 Option 1 : Interface Web Admin (Recommandé)

### Étapes :
1. Ouvrez le **Panel Admin** : http://localhost:5175
2. Connectez-vous avec votre clé admin
3. Allez dans l'onglet **"✅ Validation Expert"**
4. Cliquez sur **"🌍 JSON Multi-langue"**
5. Sélectionnez votre fichier `connaissances.json`
6. Attendez la confirmation d'upload

### Avantages :
- ✅ Interface visuelle intuitive
- ✅ Retour immédiat sur le succès/erreurs
- ✅ Statistiques en temps réel
- ✅ Pas besoin de ligne de commande

---

## ⚙️ Option 2 : Script Batch Automatique

### Prérequis :
- PowerShell 5.1 ou supérieur
- Backend API en cours d'exécution (port 8000)
- Clé admin valide configurée dans `config.env`

### Configuration :

Éditez le fichier `config.env` :
```env
API_URL=http://localhost:8000/api/admin/ingest-json
API_KEY=admin-burkina-2024
```

### Utilisation :

#### Windows :
```cmd
# Double-cliquez sur ingest.bat
# OU exécutez dans le terminal :
.\ingest.bat
```

#### PowerShell direct :
```powershell
.\ingest.ps1
```

### Flux de travail :
1. Le script charge `connaissances.json`
2. Affiche un échantillon des données
3. Demande confirmation
4. Envoie le fichier à l'API
5. Affiche les résultats (succès + erreurs)

---

## 📄 Format JSON Multilingue

### Structure requise :

```json
[
  {
    "categorie": "Histoire",
    "langues": {
      "fr": {
        "question": "Que signifie Burkina Faso ?",
        "reponse": "Burkina Faso signifie 'pays des hommes intègres'..."
      },
      "mo": {
        "question": "Burkina Faso yɩlɩg yaa ?",
        "reponse": "Burkina Faso yɩlɩg yaa 'n taaba yamb ye'..."
      },
      "di": {
        "question": "Burkina Faso kɔrɔ ye mun ye ?",
        "reponse": "Burkina Faso kɔrɔ ye 'denw kɛnyɛ' ye..."
      }
    }
  },
  {
    "categorie": "Agriculture",
    "langues": {
      "fr": {
        "question": "Quelle est la période de semis du mil ?",
        "reponse": "Le mil se sème de juin à juillet..."
      },
      "mo": {
        "question": "Mil wʋsg n bɩ yɩ ne ?",
        "reponse": "Mil bɩ wʋs ne zu-bɩɩs fʋɭʋ wã..."
      },
      "di": {
        "question": "Mil bɛ fɔ san jumen na ?",
        "reponse": "Mil bɛ fɔ zuye ni zuluye..."
      }
    }
  }
]
```

### Champs :

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `categorie` | string | ✅ Oui | Catégorie de la connaissance |
| `langues` | object | ✅ Oui | Objet contenant les traductions |
| `langues.fr` | object | ⚠️ Recommandé | Version française |
| `langues.mo` | object | ❌ Optionnel | Version mooré |
| `langues.di` | object | ❌ Optionnel | Version dioula |
| `question` | string | ✅ Oui | La question |
| `reponse` | string | ✅ Oui | La réponse complète |

### Extension recommandée (structure enrichie)

Pour obtenir un comportement plus "pédagogique" côté IA (réponse courte, détaillée, conseil, avertissement),
vous pouvez, par langue, remplacer/compléter `question` + `reponse` par des champs plus structurés :

```json
{
  "categorie": "Plantes Medicinales",
  "sous_categorie": "Energie et fatigue",
  "niveau": "grand_public",
  "langues": {
    "fr": {
      "intention": "traitement_fatigue",
      "question_type": "utilisation",
      "reponse_courte": "Le moringa aide à réduire la fatigue grâce à sa richesse en fer et en vitamines.",
      "reponse_detaillee": "Pour lutter contre la fatigue, consomme une cuillère à soupe de poudre de feuilles séchées de moringa par jour. Tu peux la mélanger dans la bouillie, la sauce ou de l’eau tiède. Cette pratique est courante au Burkina Faso pour renforcer l’énergie et prévenir l’anémie.",
      "conseil": "Il est préférable de consommer le moringa le matin.",
      "avertissement": "En cas de maladie grave ou de fatigue persistante, consulte un agent de santé."
    }
  }
}
```

L’endpoint `/api/admin/ingest-json` accepte désormais :
- l’ancien format **plat** (`question` + `reponse`),
- et ce format **enrichi** (les champs `reponse_courte`, `reponse_detaillee`, `conseil`, `avertissement` sont
  utilisés pour construire un texte d’ingestion optimisé pour le RAG et le cerveau conversationnel.

### Codes langues supportés :
- `fr` : Français
- `mo` : Mooré
- `di` : Dioula
- `ff` : Fulfuldé (à ajouter)
- `gu` : Gulmancema (à ajouter)

---

## 🔍 Exemples par catégorie

### Histoire :
```json
{
  "categorie": "Histoire",
  "langues": {
    "fr": {
      "question": "Qui a renommé la Haute-Volta en Burkina Faso ?",
      "reponse": "Thomas Sankara a renommé la Haute-Volta en Burkina Faso le 4 août 1984."
    }
  }
}
```

### Agriculture :
```json
{
  "categorie": "Agriculture",
  "langues": {
    "fr": {
      "question": "Comment lutter contre les oiseaux qui mangent le mil ?",
      "reponse": "Utiliser des épouvantails, des filets ou des répulsifs naturels comme les feuilles de neem."
    },
    "mo": {
      "question": "Yaa woto n rat n yiɣ zĩis n wẽ mil ?",
      "reponse": "Tʋm saglgã, taab ne tɩɩm soaba pʋgẽ."
    }
  }
}
```

### Santé :
```json
{
  "categorie": "Santé",
  "langues": {
    "fr": {
      "question": "Quels sont les symptômes du paludisme ?",
      "reponse": "Fièvre, maux de tête, frissons, fatigue intense, parfois vomissements."
    },
    "mo": {
      "question": "Paludisme pils tɩɩsa ?",
      "reponse": "Pu-biig, zuk tɩɩse, gĩisg, vɩɩm yell, sãnda nao tʋmdẽ."
    },
    "di": {
      "question": "Paludisme ka juguw ye mun ye ?",
      "reponse": "Kunan, kunkolodimi, nɛnɛ, fami, wa a bɛ sɔgɔ."
    }
  }
}
```

---

## ✅ Validation et Traitement

### Validation automatique :
- ✅ Vérifie la présence de `categorie`
- ✅ Vérifie la présence de `langues`
- ✅ Vérifie `question` et `reponse` pour chaque langue
- ✅ Ignore les champs vides (nan, null)
- ⚠️ Continue même en cas d'erreur sur une ligne

### Traitement :
1. **Parsing JSON** : Lecture et validation du fichier
2. **Itération** : Traitement de chaque item
3. **Extraction** : Pour chaque langue (fr, mo, di, etc.)
4. **Embedding** : Création du vecteur sémantique (RAG)
5. **Stockage** : Sauvegarde dans MongoDB
6. **Indexation** : Ajout à l'index FAISS

### Métadonnées ajoutées :
- `language` : Code langue (fr, mo, di)
- `category` : Catégorie
- `source` : "json_multilingual"
- `uploaded_by` : "admin"
- `uploaded_at` : Timestamp
- `status` : "processed"

---

## 🐛 Dépannage

### Erreur : "API_URL non trouvé"
**Solution** : Vérifiez que `config.env` existe et contient `API_URL=...`

### Erreur : "API non disponible"
**Solution** : Démarrez le backend :
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Erreur : "JSON invalide"
**Solution** : Validez votre JSON sur https://jsonlint.com/

### Erreur : "Colonnes manquantes"
**Solution** : Vérifiez que chaque item a `categorie` et `langues`

### Erreur : "Erreur d'authentification"
**Solution** : Vérifiez que `API_KEY` dans `config.env` correspond à votre clé admin

---

## 📊 Statistiques d'import

Après l'import, vous verrez :
```
✅ Import JSON réussi!
95 connaissances ingérées (10 items)
⚠️ 5 erreurs détectées

Détails :
- Index 3 : Structure invalide
- Index 7 (mo) : Question vide
```

**Calcul** : 10 items × 3 langues = 30 possibles, 25 réussies, 5 échouées

---

## 🚀 Bonnes pratiques

### ✅ À faire :
- Utilisez UTF-8 pour les caractères spéciaux
- Testez avec 2-3 items avant d'uploader 100+
- Gardez une sauvegarde de vos JSON
- Utilisez des catégories cohérentes
- Vérifiez les traductions avant l'upload

### ❌ À éviter :
- Ne pas mélanger plusieurs formats dans un JSON
- Éviter les réponses trop courtes (< 20 caractères)
- Ne pas mettre de HTML dans les réponses
- Éviter les doublons (même question)

---

## 📞 Support

En cas de problème :
1. Vérifiez les logs backend : Onglet **Logs** du panel admin
2. Consultez la console PowerShell pour les détails d'erreur
3. Validez votre JSON sur https://jsonlint.com/
4. Testez d'abord avec le fichier `connaissances.json` fourni

---

## 📝 Template de départ

Le fichier `connaissances.json` contient 10 exemples prêts à l'emploi.

**Pour télécharger le template depuis l'admin** :
- Panel Admin → Validation Expert → "📄 Template JSON"

---

**🇧🇫 IA Souveraine Burkina - Version Multilingue**
