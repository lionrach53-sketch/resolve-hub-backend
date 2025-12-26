import requests
import json

print("🧪 TEST DES VRAIES CATEGORIES DU RAG\n")
print("=" * 60)

tests = [
    {
        "name": "Plantes Medicinales",
        "message": "Quelle plante utilise-t-on pour soigner les maux d'estomac ?",
        "category": "Plantes Medicinales"
    },
    {
        "name": "Transformation PFNL", 
        "message": "Comment transformer la noix de karité en beurre ?",
        "category": "Transformation PFNL"
    },
    {
        "name": "Civisme",
        "message": "Quels sont mes devoirs de citoyen ?",
        "category": "Civisme"
    }
]

for test in tests:
    print(f"\n📌 Test: {test['name']}")
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
            print(f"✅ Réponse (langue: {data.get('language', 'N/A')}):")
            print(f"{data.get('response', 'Pas de réponse')}\n")
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

print("\n" + "=" * 60)
print("✅ Tests terminés!")
