# test_mongo.py
from mongodb import db

print("📊 Vérification MongoDB...")
print("=" * 50)

# 1. Comptez les conversations
count = db.chat_conversations.count_documents({})
print(f"Total conversations dans MongoDB: {count}")

if count > 0:
    print("\n📝 3 dernières conversations:")
    recent = list(db.chat_conversations.find().sort("timestamp", -1).limit(3))
    
    for i, conv in enumerate(recent):
        print(f"\n{i+1}. Message: {conv.get('user_message', 'N/A')}")
        print(f"   ID: {conv.get('conversation_id', 'N/A')}")
        print(f"   Date: {conv.get('timestamp')}")
        print(f"   Catégorie: {conv.get('category', 'N/A')}")
else:
    print("❌ Aucune conversation dans MongoDB")

# 2. Vérifiez les logs admin
print("\n" + "=" * 50)
print("📋 Logs admin de chat:")
logs = list(db.admin_logs.find({"action": "chat_conversation"}).sort("timestamp", -1).limit(3))
print(f"Nombre de logs: {len(logs)}")

for log in logs:
    print(f"  - {log.get('timestamp')}: {log.get('details', {})}")

print("=" * 50)