from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import models
import security

# CRUD pour API Keys
def create_api_key(db: Session, name: str, raw_key: str, permissions: list, expires_at=None):
    hashed_key = security.hash_api_key(raw_key)
    
    db_api_key = models.APIKey(
        name=name,
        hashed_key=hashed_key,
        permissions=permissions,
        expires_at=expires_at
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

def get_api_key_by_key(db: Session, raw_key: str):
    hashed_key = security.hash_api_key(raw_key)
    return db.query(models.APIKey).filter(
        models.APIKey.hashed_key == hashed_key
    ).first()

def get_all_api_keys(db: Session):
    return db.query(models.APIKey).order_by(desc(models.APIKey.created_at)).all()

def revoke_api_key(db: Session, key_id: int):
    api_key = db.query(models.APIKey).filter(models.APIKey.id == key_id).first()
    if not api_key:
        return False
    
    api_key.is_active = False
    db.commit()
    return True

# CRUD pour Conversations
def create_conversation(db: Session, user_message: str, ai_response: str, 
                       category: str, api_key_id: int = None, confidence: float = 0.0):
    conversation = models.Conversation(
        user_message=user_message,
        ai_response=ai_response,
        category=category,
        api_key_id=api_key_id,
        confidence=confidence
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def get_conversations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Conversation)\
             .order_by(desc(models.Conversation.created_at))\
             .offset(skip).limit(limit).all()

# CRUD pour Knowledge
def create_knowledge(db: Session, question: str, answer: str, 
                    category: str, source: str = None, contributor: str = None):
    knowledge = models.Knowledge(
        question=question,
        answer=answer,
        category=category,
        source=source,
        contributor=contributor
    )
    
    db.add(knowledge)
    db.commit()
    db.refresh(knowledge)
    return knowledge

def get_knowledge(db: Session, category: str = None, limit: int = 50):
    query = db.query(models.Knowledge)
    if category:
        query = query.filter(models.Knowledge.category == category)
    
    return query.order_by(desc(models.Knowledge.created_at)).limit(limit).all()

# Statistiques
def get_system_stats(db: Session):
    today = datetime.now().date()
    
    total_conversations = db.query(func.count(models.Conversation.id)).scalar() or 0
    total_knowledge = db.query(func.count(models.Knowledge.id)).scalar() or 0
    
    conversations_today = db.query(func.count(models.Conversation.id)).filter(
        func.date(models.Conversation.created_at) == today
    ).scalar() or 0
    
    active_api_keys = db.query(func.count(models.APIKey.id)).filter(
        models.APIKey.is_active == True
    ).scalar() or 0
    
    return {
        "total_conversations": total_conversations,
        "total_knowledge": total_knowledge,
        "conversations_today": conversations_today,
        "active_api_keys": active_api_keys
    }