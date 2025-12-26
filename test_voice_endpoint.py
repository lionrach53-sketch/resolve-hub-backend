"""
Script de test rapide pour l'endpoint vocal
Crée un audio de test et l'envoie à l'API
"""
import requests
import io
import wave
import struct
import math

def generate_test_audio(duration=2, frequency=440):
    """Génère un son de test (bip) en WAV"""
    sample_rate = 16000
    num_samples = int(sample_rate * duration)
    
    # Créer un buffer WAV en mémoire
    buffer = io.BytesIO()
    
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Générer un ton simple
        for i in range(num_samples):
            value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)
    
    buffer.seek(0)
    return buffer.getvalue()

def test_voice_endpoint():
    """Teste l'endpoint /ai/chat/voice"""
    print("🧪 TEST ENDPOINT VOCAL")
    print("=" * 60)
    
    # Générer audio de test
    print("🔊 Génération audio test...")
    audio_data = generate_test_audio(duration=2, frequency=440)
    print(f"✅ Audio généré: {len(audio_data)} bytes")
    
    # Envoyer à l'API
    url = "http://localhost:8000/ai/chat/voice"
    files = {
        'audio': ('test.wav', audio_data, 'audio/wav')
    }
    data = {
        'session_id': 'test_123',
        'category': 'general'
    }
    
    print(f"\n📤 Envoi vers: {url}")
    print(f"📊 Taille: {len(audio_data)} bytes")
    print(f"🎯 Format: WAV 16kHz mono")
    
    try:
        response = requests.post(url, files=files, data=data, timeout=60)
        
        print(f"\n📥 Réponse HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCÈS !")
            print(f"📝 Transcription: {result.get('transcription', 'N/A')}")
            print(f"🌍 Langue: {result.get('language', 'N/A')}")
            print(f"📊 Confiance: {result.get('transcription_confidence', 0):.2%}")
            print(f"💬 Réponse IA: {result.get('response', 'N/A')[:100]}...")
        else:
            print(f"\n❌ ERREUR {response.status_code}")
            try:
                error = response.json()
                print(f"📄 Détail: {error.get('detail', 'N/A')}")
            except:
                print(f"📄 Texte: {response.text[:200]}")
        
        print("\n" + "=" * 60)
        
    except requests.exceptions.Timeout:
        print("\n⏱️ TIMEOUT - Le serveur met trop de temps à répondre")
    except requests.exceptions.ConnectionError:
        print("\n🔌 ERREUR - Impossible de se connecter au serveur")
        print("   Vérifiez que le backend tourne sur http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")

if __name__ == "__main__":
    test_voice_endpoint()
