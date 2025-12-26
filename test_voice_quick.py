"""Test rapide de l'endpoint vocal"""
import requests
import io

# URL de l'API
url = "http://localhost:8000/ai/chat/voice"

# Créer un fichier audio factice (très court)
audio_data = b'\x00' * 1000  # 1KB de données

files = {
    'audio': ('test.webm', io.BytesIO(audio_data), 'audio/webm')
}

data = {
    'session_id': 'test-session',
    'category': 'general'
}

print("Test de l'endpoint vocal...")
print(f"URL: {url}")

try:
    response = requests.post(url, files=files, data=data, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
except requests.exceptions.ConnectionError:
    print("\nERREUR: Impossible de se connecter au backend")
    print("Le serveur backend n'est probablement pas en cours d'execution")
except Exception as e:
    print(f"\nERREUR: {e}")
