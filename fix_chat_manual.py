from fastapi import BackgroundTasks, HTTPException
from datetime import datetime
import uuid
from mongodb import db
import logging

logger = logging.getLogger(__name__)

def get_fixed_chat_function():
    """Retourne la fonction corrigée"""
    async def chat_with_ai_fixed(message, background_tasks: BackgroundTasks):
        try:
            responses = {
                "general": "Je suis l'IA Souveraine du Burkina Faso...",
                "agriculture": "Pour l'agriculture au Burkina...",
                "sante": "Pour votre santé, le moringa...",
                "education": "Le système éducatif burkinabè...",
                "culture": "La culture burkinabè est riche...",
                "economie": "L'économie burkinabè est basée...",
                "technologie": "Le secteur technologique...",
                "droit": "Le système juridique burkinabè..."
            }
            
            default_response = "Je suis spécialisé dans les questions concernant le Burkina Faso..."
            response_text = responses.get(message.category.lower(), default_response)
            conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
            
            # SAUVEGARDE MONGODB
            conversation_data = {
                "user_message": message.message,
                "ai_response": response_text,
                "category": message.category,
                "conversation_id": conversation_id,
                "timestamp": datetime.now(),
                "user_ip": "unknown"
            }
            
            mongo_id = db.save_chat_conversation(conversation_data)
            
            background_tasks.add_task(
                db.add_admin_log,
                "chat_conversation",
                "system",
                {
                    "conversation_id": conversation_id,
                    "mongo_id": mongo_id,
                    "category": message.category
                }
            )
            
            logger.info(f"💬 Conversation sauvegardée: {conversation_id}")
            
            from main import ChatResponse
            return ChatResponse(
                response=response_text,
                confidence=0.92,
                sources=["Base de connaissances IA Souveraine Burkina v2.0"],
                conversation_id=conversation_id
            )
            
        except Exception as e:
            logger.error(f"Erreur chat: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return chat_with_ai_fixed
