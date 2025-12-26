"""Test pour vérifier le statut de Whisper"""
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("="*60)
print("TEST DE WHISPER")
print("="*60)

# Test 1: Import Whisper
print("\n1. Test import whisper...")
try:
    import whisper
    print("   OK - Whisper importe")
except ImportError as e:
    print(f"   ECHEC - Whisper non installe: {e}")
    sys.exit(1)

# Test 2: Charger le modèle
print("\n2. Test chargement modele base...")
try:
    model = whisper.load_model("base")
    print("   OK - Modele base charge")
except Exception as e:
    print(f"   ECHEC - Erreur chargement: {e}")
    sys.exit(1)

# Test 3: Vérifier le service STT
print("\n3. Test STT Service...")
try:
    from ai.service.stt_service import stt_service
    
    print(f"   - STT disponible: {stt_service.is_available()}")
    print(f"   - Whisper disponible: {stt_service.whisper_available}")
    print(f"   - Modele charge: {stt_service.model is not None}")
    print(f"   - Taille modele: {stt_service.model_size}")
    
    if not stt_service.is_available():
        print("   ECHEC - STT non disponible")
        sys.exit(1)
    
    print("   OK - STT Service operationnel")
except Exception as e:
    print(f"   ECHEC - Erreur STT Service: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("RESULTAT: Tous les tests passes!")
print("="*60)
