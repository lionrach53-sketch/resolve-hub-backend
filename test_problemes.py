import requests
import json

print("🧪 TEST DES QUESTIONS PROBLÉMATIQUES\n")
print("=" * 60)

tests = [
    {
        "name": "Spiritualité (devrait parler de Tengsoba)",
        "message": "Parle-moi des traditions spirituelles burkinabè",
        "category": "Spiritualite et Traditions"
    },
    {
        "name": "Développement Personnel (devrait parler de SMART)",
        "message": "Comment développer mes compétences personnelles ?",
        "category": "Developpement Personnel"
    },
    {
        "name": "Métiers Informels (devrait parler de réparation)",
        "message": "Quels sont les métiers du secteur informel ?",
        "category": "Metiers Informels"
    }
]

for test in tests:
    print(f"\n📌 {test['name']}")
    print(f"   Question: {test['message']}")
    print(f"   Catégorie: {test['category']}")
    print("-" * 60)
    
    try:
        response = requests.post(
            'http://localhost:8000/api/chat/guest',
            json={"message": test['message'], "category": test['category']},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse:")
            print(f"{data.get('response', 'Pas de réponse')}\n")
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("✅ Tests terminés!")
