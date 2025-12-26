"""
Script pour créer un fichier Excel template pour l'ingestion de connaissances
"""
import pandas as pd
from datetime import datetime

# Données exemple
data = {
    'Question/Titre': [
        'Quelle est la capitale du Burkina Faso?',
        'Comment cultiver le mil?',
        'Quels sont les symptômes du paludisme?',
        'Comment obtenir un passeport au Burkina Faso?',
        'Quelle est la monnaie du Burkina Faso?'
    ],
    'Réponse/Contenu': [
        'La capitale du Burkina Faso est Ouagadougou. C\'est la plus grande ville du pays avec environ 2,5 millions d\'habitants.',
        'Le mil se cultive pendant la saison des pluies (juin-septembre). Il faut labourer le champ, semer les graines espacées de 40cm, désherber régulièrement et récolter après 3-4 mois.',
        'Les symptômes du paludisme incluent: fièvre élevée, frissons, maux de tête, douleurs musculaires, fatigue intense, nausées et vomissements. Consultez rapidement un centre de santé.',
        'Pour obtenir un passeport, rendez-vous au commissariat de police avec: acte de naissance, 2 photos, extrait de casier judiciaire, certificat de nationalité. Le coût est de 45 000 FCFA et le délai est de 2 semaines.',
        'La monnaie officielle est le Franc CFA (XOF). 1 EUR = environ 655 FCFA. Les billets vont de 500 à 10 000 FCFA.'
    ],
    'Catégorie': [
        'Général',
        'Agriculture',
        'Santé',
        'Administration',
        'Économie'
    ],
    'Tags': [
        'capitale, géographie, Ouagadougou',
        'agriculture, mil, culture, saison',
        'santé, paludisme, maladie, symptômes',
        'administration, passeport, documents',
        'économie, monnaie, FCFA, devise'
    ]
}

# Créer le DataFrame
df = pd.DataFrame(data)

# Sauvegarder dans Excel
output_file = '../template_connaissances.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"✅ Template Excel créé: {output_file}")
print(f"📊 {len(df)} exemples de connaissances inclus")
print("\n📝 Structure du fichier:")
print("  - Colonne A: Question/Titre (obligatoire)")
print("  - Colonne B: Réponse/Contenu (obligatoire)")
print("  - Colonne C: Catégorie (obligatoire)")
print("  - Colonne D: Tags (optionnel, séparés par des virgules)")
print("\n💡 Utilisez ce template pour ajouter vos propres connaissances!")
