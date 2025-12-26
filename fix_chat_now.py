# fix_chat_now.py - Corrige IMMÉDIATEMENT la route /api/chat
import re
from datetime import datetime
import uuid

with open('main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Cherche la fonction chat_with_ai actuelle
chat_pattern = r'@app\.post\("/api/chat", response_model=ChatResponse, tags=\["Chat"\]\)\s*async def chat_with_ai\(message: ChatMessage\):'

if chat_pattern in content:
    print("✅ Fonction chat_with_ai trouvée")
    
    # Nouvelle version avec MongoDB
    new_chat_function = '''@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_with_ai(message: ChatMessage, background_tasks: BackgroundTasks):
    """Endpoint pour discuter avec l'IA (chat user) - VERSION MONGODB"""
    try:
        # Réponses simulées
        responses = {
            "general": "Je suis l'IA Souveraine du Burkina Faso. Je peux vous aider avec des questions sur l'agriculture, la santé, l'éducation et bien d'autres sujets concernant notre pays.",
            "agriculture": "Pour l'agriculture au Burkina, je recommande les techniques de zaï et de cordons pierreux pour lutter contre la désertification.",
            "sante": "Pour votre santé, le moringa est une plante locale très riche en nutriments. Consultez toujours un professionnel de santé.",
            "education": "Le système éducatif burkinabè comprend l'éducation de base, secondaire et supérieure. L'éducation est gratuite jusqu'à 16 ans.",
            "culture": "La culture burkinabè est riche et diversifiée, avec le FESPACO comme festival de cinéma le plus important d'Afrique.",
            "economie": "L'économie burkinabè est basée sur l'agriculture et l'extraction minière, notamment l'or.",
            "technologie": "Le secteur technologique au Burkina se développe rapidement avec des innovations dans le mobile money et l'agritech.",
            "droit": "Le système juridique burkinabè s'inspire du droit français avec des adaptations locales."
        }
        
        default_response = "Je suis spécialisé dans les questions concernant le Burkina Faso. Pourriez-vous préciser votre question ?"
        
        response_text = responses.get(message.category.lower(), default_response)
        conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        
        # ============ SAUVEGARDE MONGODB ============
        conversation_data = {
            "user_message": message.message,
            "ai_response": response_text,
            "category": message.category,
            "conversation_id": conversation_id,
            "timestamp": datetime.now(),
            "user_ip": "unknown"
        }
        
        # SAUVEGARDE DANS MONGODB
        from mongodb import db
        mongo_id = db.save_chat_conversation(conversation_data)
        
        # Log admin
        background_tasks.add_task(
            db.add_admin_log,
            "chat_conversation",
            "system",
            {
                "conversation_id": conversation_id,
                "mongo_id": mongo_id,
                "category": message.category,
                "message_length": len(message.message)
            }
        )
        
        logger.info(f"💬 Conversation sauvegardée MongoDB ID: {mongo_id}")
        # ============ FIN SAUVEGARDE ============
        
        return ChatResponse(
            response=response_text,
            confidence=0.92,
            sources=["Base de connaissances IA Souveraine Burkina v2.0"],
            conversation_id=conversation_id
        )
        
    except Exception as e:
        logger.error(f"Erreur chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))'''
    
    # Remplace la fonction
    old_function_match = re.search(r'@app\.post\("/api/chat".*?async def chat_with_ai.*?\n    except Exception as e.*?\n        raise HTTPException.*?\n        \}', content, re.DOTALL)
    
    if old_function_match:
        old_function = old_function_match.group(0)
        content = content.replace(old_function, new_chat_function)
        
        with open('main_fixed.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Route /api/chat corrigée avec MongoDB !")
        print("📁 Fichier: main_fixed.py")
    else:
        print("❌ Impossible de trouver toute la fonction")
else:
    print("❌ Pattern non trouvé")

print("\n🔧 Pour appliquer:")
print("1. Copiez le contenu de main_fixed.py vers main.py")
print("2. Ou exécutez: copy main_fixed.py main.py /Y")
print("3. Redémarrez: python main.py")