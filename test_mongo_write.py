# test_mongo_write.py
import sys
sys.path.append('.')
from mongodb import db
from datetime import datetime

print("🧪 Test d'écriture MongoDB...")

# Test 1: Écrire une conversation
test_conv = {
    "user_message": "Test depuis script",
    "ai_response": "Réponse de test",
    "category": "test",
    "conversation_id": "test_123",
    "timestamp": datetime.now()
}

try:
    conv_id = db.save_chat_conversation(test_conv)
    print(f"✅ Conversation écrite: {conv_id}")
except Exception as e:
    print(f"❌ Erreur conversation: {e}")

# Test 2: Écrire une contribution
test_contrib = {
    "id": "test_" + str(datetime.now().timestamp())[-6:],
    "title": "Test contribution",
    "content": "Contenu de test",
    "category": "Test",
    "status": "pending",
    "expertId": "exp_001",
    "expertName": "Dr. Test",
    "createdAt": datetime.now()
}

try:
    contrib_id = db.add_contribution(test_contrib)
    print(f"✅ Contribution écrite: {contrib_id}")
except Exception as e:
    print(f"❌ Erreur contribution: {e}")

# Test 3: Vérifier les comptes
print("\n📊 VÉRIFICATION:")
print(f"  Conversations: {db.chat_conversations.count_documents({})}")
print(f"  Contributions: {db.contributions.count_documents({})}")
print(f"  File validation: {db.validation_queue.count_documents({})}")

# Afficher les 3 dernières conversations
print("\n💬 3 dernières conversations:")
convs = list(db.chat_conversations.find().sort("timestamp", -1).limit(3))
for conv in convs:
    print(f"  - {conv.get('user_message', 'N/A')}")