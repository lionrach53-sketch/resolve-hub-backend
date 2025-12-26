"""Test compatibilité avec ai_chat.py"""
from ai.service.ai_brain import ai_brain

print("=" * 60)
print("TEST COMPATIBILITÉ AI_CHAT.PY")
print("=" * 60)

# Simuler un appel comme dans ai_chat.py ligne 662
print("\n🧪 Test appel comme dans ai_chat.py...")

rag_results = [
    {"question": "Test", "reponse": "Réponse test"}
]

response = ai_brain.generate_intelligent_response(
    question="Test question",
    rag_results=rag_results,
    category="test_category",
    language="fr"
)

# Vérifier les clés utilisées dans ai_chat.py ligne 690-698
required_in_ai_chat = [
    "reponse",
    "categorie",
    "sources_utilisees",
    "mode",
    "timestamp"
]

print("\n✅ Vérification clés utilisées dans ai_chat.py:")
all_ok = True
for key in required_in_ai_chat:
    exists = key in response
    status = "✅" if exists else "❌"
    print(f"  {key}: {status}")
    if not exists:
        all_ok = False

if not all_ok:
    print("\n❌ INCOMPATIBLE: certaines clés manquantes")
    exit(1)

# Vérifier l'historique fonctionne
print("\n🧪 Test méthodes historique:")
try:
    ai_brain.add_to_history("user", "test")
    print("  add_to_history: ✅")
    
    ai_brain.add_to_history("assistant", "test response")
    print("  add_to_history (2nd): ✅")
    
    ai_brain.clear_history()
    print("  clear_history: ✅")
except Exception as e:
    print(f"  ❌ Erreur historique: {e}")
    exit(1)

print("\n" + "=" * 60)
print("✅ 100% COMPATIBLE avec ai_chat.py")
print("=" * 60)
