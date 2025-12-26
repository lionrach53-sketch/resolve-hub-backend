import requests

# Question EXACTE du RAG
response = requests.post(
    'http://localhost:8000/api/chat/guest',
    json={"message": "Quel est le rôle du Tengsoba dans la communauté Mossi ?", "category": "Spiritualite et Traditions"}
)

print("✅ Question exacte du RAG:")
print(response.json().get('response', 'N/A')[:200])
