import requests

tests = [
    ("Plantes Medicinales", "Quelle plante utiliser-t-on pour soigner les maux d'estomac ?"),
    ("Transformation PFNL", "Comment transformer la noix de karité en beurre ?"),
    ("Science Pratique - Saponification", "Comment fabriquer du savon artisanal ?"),
    ("Metiers Informels", "Quels sont les métiers du secteur informel ?"),
    ("Mathematiques Pratiques", "Comment calculer les surfaces agricoles ?"),
    ("Developpement Personnel", "Comment développer mes compétences personnelles ?"),
    ("general", "Que peux-tu m'apprendre ?"),
]

print("TEST COMPLET DES QUESTIONS DU FRONTEND\n")
print("=" * 70)

for cat, question in tests:
    response = requests.post(
        'http://localhost:8000/api/chat/guest',
        json={"message": question, "category": cat}
    )
    
    print(f"\nCat: {cat}")
    print(f"   Q: {question}")
    print(f"   R: {response.json().get('response', 'N/A')[:150]}...")

print("\n" + "=" * 70)
print("Tests termines!")
