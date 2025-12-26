import requests
import json

print("\n🧪 TEST AGRICULTURE\n")

data = {
    "message": "Quelles sont les techniques agricoles traditionnelles au Burkina Faso ?",
    "category": "agriculture"
}

try:
    response = requests.post(
        "http://localhost:8000/api/chat/guest",
        json=data,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ REPONSE:")
        print(result.get("response", "No response"))
    else:
        print(f"\n❌ ERREUR {response.status_code}:")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
