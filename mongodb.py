# mongodb.py - NOUVELLE CLASSE DATABASE POUR MONGODB
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from bson.json_util import dumps, loads
import json
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class _InMemoryCursor:
    def __init__(self, docs: List[Dict[str, Any]]):
        self._docs = list(docs)

    def sort(self, key: str, direction: int = DESCENDING):
        reverse = direction == DESCENDING or direction == -1
        self._docs.sort(key=lambda d: d.get(key), reverse=reverse)
        return self

    def limit(self, n: int):
        self._docs = self._docs[: max(0, int(n))]
        return self

    def skip(self, n: int):
        self._docs = self._docs[max(0, int(n)) :]
        return self

    def __iter__(self):
        return iter(self._docs)


class _InMemoryInsertOneResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class _InMemoryUpdateResult:
    def __init__(self, matched_count: int, modified_count: int):
        self.matched_count = matched_count
        self.modified_count = modified_count


class _InMemoryDeleteResult:
    def __init__(self, deleted_count: int):
        self.deleted_count = deleted_count


class _InMemoryCollection:
    def __init__(self):
        self._docs: List[Dict[str, Any]] = []

    def create_index(self, *args, **kwargs):
        return None

    def insert_one(self, doc: Dict[str, Any]):
        if "_id" not in doc:
            doc = dict(doc)
            doc["_id"] = str(ObjectId())
        self._docs.append(doc)
        return _InMemoryInsertOneResult(doc["_id"])

    def insert_many(self, docs: List[Dict[str, Any]]):
        for d in docs:
            self.insert_one(d)
        return None

    def _matches(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        if not query:
            return True
        for key, expected in query.items():
            actual = doc.get(key)
            if isinstance(expected, dict):
                # support minimal operators used in this repo ($gte, $lte)
                gte = expected.get("$gte")
                lte = expected.get("$lte")
                if gte is not None and (actual is None or actual < gte):
                    return False
                if lte is not None and (actual is None or actual > lte):
                    return False
            else:
                if actual != expected:
                    return False
        return True

    def find(self, query: Optional[Dict[str, Any]] = None, *args, **kwargs):
        # args/kwargs peuvent contenir une projection, ignorée en mode in-memory
        query = query or {}
        matched = [d for d in self._docs if self._matches(d, query)]
        return _InMemoryCursor(matched)

    def find_one(self, query: Dict[str, Any]):
        for d in self._docs:
            if self._matches(d, query):
                return d
        return None

    def update_one(self, filter: Dict[str, Any], update: Dict[str, Any], upsert: bool = False):
        for d in self._docs:
            if self._matches(d, filter):
                if "$set" in update and isinstance(update["$set"], dict):
                    d.update(update["$set"])
                return _InMemoryUpdateResult(matched_count=1, modified_count=1)

        if upsert:
            new_doc = dict(filter)
            if "$set" in update and isinstance(update["$set"], dict):
                new_doc.update(update["$set"])
            self.insert_one(new_doc)
            return _InMemoryUpdateResult(matched_count=0, modified_count=1)

        return _InMemoryUpdateResult(matched_count=0, modified_count=0)

    def delete_one(self, filter: Dict[str, Any]):
        for i, d in enumerate(self._docs):
            if self._matches(d, filter):
                del self._docs[i]
                return _InMemoryDeleteResult(deleted_count=1)
        return _InMemoryDeleteResult(deleted_count=0)

    def count_documents(self, query: Optional[Dict[str, Any]] = None):
        return len(list(self.find(query or {})))

class MongoDB:
    """Classe de gestion MongoDB pour remplacer le système de fichiers JSON"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # URL de connexion depuis les variables d'environnement
        self.mongo_url = os.getenv("MONGODB_URL")
        if not self.mongo_url:
            logger.warning("⚠️  MONGODB_URL non défini - mode dégradé sans MongoDB")
            self.client = None
            self.db = None
            self.db_name = "disconnected"
            self._init_inmemory_collections()
            self._initialized = True
            return
        
        try:
            # Connexion à MongoDB Atlas avec timeout court
            self.client = MongoClient(
                self.mongo_url, 
                serverSelectionTimeoutMS=3000,  # 3 secondes
                connectTimeoutMS=3000,
                socketTimeoutMS=3000
            )
            # Test de la connexion
            self.client.admin.command('ping')
            logger.info("✅ Connecté à MongoDB Atlas avec succès")
            
            # Base de données
            self.db_name = os.getenv("MONGODB_DBNAME", "ia_souveraine_bf")
            self.db = self.client[self.db_name]
            
            # Collections pour les 3 panels
            self._init_collections()
            self._create_indexes()
            
            self._initialized = True
            
        except ConnectionFailure as e:
            logger.error(f"❌ Erreur de connexion MongoDB: {e}")
            logger.warning("⚠️  Fonctionnement en mode dégradé sans MongoDB")
            self.client = None
            self.db = None
            self.db_name = "error"
            self._init_inmemory_collections()
            self._initialized = True
        except Exception as e:
            logger.error(f"❌ Erreur inattendue MongoDB: {e}")
            logger.warning("⚠️  Fonctionnement en mode dégradé sans MongoDB")
            self.client = None
            self.db = None
            self.db_name = "error"
            self._init_inmemory_collections()
            self._initialized = True

    def _init_inmemory_collections(self):
        """Initialise des collections en mémoire pour éviter les crashs en mode dégradé."""
        self.contributions = _InMemoryCollection()
        self.validation_queue = _InMemoryCollection()
        self.experts = _InMemoryCollection()

        self.admin_logs = _InMemoryCollection()
        self.api_keys = _InMemoryCollection()
        self.system_stats = _InMemoryCollection()

        self.chat_conversations = _InMemoryCollection()
        self.chat_categories = _InMemoryCollection()

        self.documents = _InMemoryCollection()
        self.notifications = _InMemoryCollection()
        self.audit_logs = _InMemoryCollection()
    
    def _init_collections(self):
        """Initialise toutes les collections nécessaires pour les 3 panels"""
        # Panel Expert
        self.contributions = self.db['contributions']
        self.validation_queue = self.db['validation_queue']
        self.experts = self.db['experts']
        
        # Panel Admin
        self.admin_logs = self.db['admin_logs']
        self.api_keys = self.db['api_keys']
        self.system_stats = self.db['system_stats']
        
        # Panel Chat
        self.chat_conversations = self.db['chat_conversations']
        self.chat_categories = self.db['chat_categories']
        
        # Collections partagées
        self.documents = self.db['documents']
        self.notifications = self.db['notifications']
        self.audit_logs = self.db['audit_logs']
        
        logger.info("✅ Collections MongoDB initialisées")
    
    def _create_indexes(self):
        """Crée les index optimisés pour les 3 panels avec gestion d'erreur"""
        try:
            logger.info("Création des indexes MongoDB...")
            
            # Index pour le Panel Expert
            self.contributions.create_index([("category", ASCENDING)], background=True)
            self.contributions.create_index([("status", ASCENDING)], background=True)
            self.contributions.create_index([("expertId", ASCENDING)], background=True)
            self.contributions.create_index([("createdAt", DESCENDING)], background=True)
            self.contributions.create_index([("title", "text"), ("content", "text")], background=True)
            
            self.validation_queue.create_index([("category", ASCENDING)], background=True)
            self.validation_queue.create_index([("submittedAt", DESCENDING)], background=True)
            self.validation_queue.create_index([("validated", ASCENDING)], background=True)
            
            # Index pour le Panel Admin
            self.admin_logs.create_index([("timestamp", DESCENDING)], background=True)
            self.api_keys.create_index([("active", ASCENDING)], background=True)
            self.system_stats.create_index([("timestamp", DESCENDING)], background=True)
            
            # Index pour le Panel Chat
            self.chat_conversations.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)], background=True)
            self.chat_conversations.create_index([("category", ASCENDING)], background=True)
            self.chat_conversations.create_index([("timestamp", DESCENDING)], background=True)
            
            # Index pour les collections partagées
            self.documents.create_index([("category", ASCENDING)], background=True)
            self.documents.create_index([("uploaded_at", DESCENDING)], background=True)
            self.notifications.create_index([
                ("recipient_type", ASCENDING),
                ("recipient_id", ASCENDING),
                ("read", ASCENDING),
                ("created_at", DESCENDING)
            ], background=True)
            
            logger.info("✅ Index MongoDB créés avec succès")
        except Exception as e:
            logger.warning(f"⚠️  Erreur création indexes (non bloquant): {e}")
            # Ne pas échouer si les indexes ne peuvent pas être créés
            # Ils seront créés automatiquement lors des premières requêtes
    
    def migrate_from_json(self, json_file_path: str = "data/expert_db.json"):
        """Migre les données depuis le fichier JSON vers MongoDB"""
        try:
            if not os.path.exists(json_file_path):
                logger.warning("Fichier JSON non trouvé, création de données initiales")
                self._create_initial_data()
                return
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Migration des contributions
            if 'contributions' in data and data['contributions']:
                for contrib in data['contributions']:
                    # Convertir les dates string en datetime
                    if 'createdAt' in contrib and isinstance(contrib['createdAt'], str):
                        try:
                            contrib['createdAt'] = datetime.fromisoformat(
                                contrib['createdAt'].replace('Z', '+00:00')
                            )
                        except:
                            contrib['createdAt'] = datetime.now()
                    
                    if 'validatedAt' in contrib and contrib['validatedAt'] and isinstance(contrib['validatedAt'], str):
                        try:
                            contrib['validatedAt'] = datetime.fromisoformat(
                                contrib['validatedAt'].replace('Z', '+00:00')
                            )
                        except:
                            contrib['validatedAt'] = None
                
                self.contributions.insert_many(data['contributions'])
                logger.info(f"✅ Migré {len(data['contributions'])} contributions")
            
            # Migration de la file de validation
            if 'validation_queue' in data and data['validation_queue']:
                for item in data['validation_queue']:
                    if 'submittedAt' in item and isinstance(item['submittedAt'], str):
                        try:
                            item['submittedAt'] = datetime.fromisoformat(
                                item['submittedAt'].replace('Z', '+00:00')
                            )
                        except:
                            item['submittedAt'] = datetime.now()
                    item['validated'] = False
                
                self.validation_queue.insert_many(data['validation_queue'])
                logger.info(f"✅ Migré {len(data['validation_queue'])} éléments dans la file de validation")
            
            # Migration des documents
            if 'documents' in data and data['documents']:
                for doc in data['documents']:
                    if 'uploaded_at' in doc and isinstance(doc['uploaded_at'], str):
                        try:
                            doc['uploaded_at'] = datetime.fromisoformat(
                                doc['uploaded_at'].replace('Z', '+00:00')
                            )
                        except:
                            doc['uploaded_at'] = datetime.now()
                
                self.documents.insert_many(data['documents'])
                logger.info(f"✅ Migré {len(data['documents'])} documents")
            
            # Migration des stats
            if 'stats' in data:
                self.system_stats.insert_one({
                    '_id': 'global_stats',
                    **data['stats'],
                    'migrated_at': datetime.now(),
                    'timestamp': datetime.now()
                })
                logger.info("✅ Migré les statistiques")
            
            # Migration des experts (depuis votre dictionnaire Python - à adapter)
            self._migrate_experts()
            
            # Création des catégories de chat
            self._create_chat_categories()
            
            logger.info("🎉 Migration terminée avec succès !")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la migration: {e}")
            raise
    
    def _migrate_experts(self):
        """Migre les experts depuis le dictionnaire Python"""
        experts_data = [
            {
                "username": "expert1",
                "id": "exp_001",
                "name": "Dr. Ibrahim Traoré",
                "email": "expert@ia-burkina.bf",
                "password": "expert123",  # À hasher en production
                "level": 3,
                "specialty": "Agriculture",
                "contributions_count": 42,
                "validation_score": 94.5,
                "join_date": "2024-01-01",
                "created_at": datetime.now(),
                "last_login": None,
                "active": True
            },
            {
                "username": "expert2",
                "id": "exp_002",
                "name": "Dr. Aïcha Diallo",
                "email": "aicha.diallo@example.com",
                "password": "expert456",
                "level": 2,
                "specialty": "Santé",
                "contributions_count": 28,
                "validation_score": 88.2,
                "join_date": "2024-01-05",
                "created_at": datetime.now(),
                "last_login": None,
                "active": True
            },
            {
                "username": "expert3",
                "id": "exp_003",
                "name": "Pr. Moussa Sawadogo",
                "email": "m.sawadogo@example.com",
                "password": "expert789",
                "level": 4,
                "specialty": "Histoire",
                "contributions_count": 67,
                "validation_score": 96.8,
                "join_date": "2023-12-15",
                "created_at": datetime.now(),
                "last_login": None,
                "active": True
            }
        ]
        
        # Vérifie si les experts existent déjà
        for expert in experts_data:
            existing = self.experts.find_one({"username": expert["username"]})
            if not existing:
                self.experts.insert_one(expert)
        
        logger.info(f"✅ Experts migrés")
    
    def _create_chat_categories(self):
        """Crée les catégories pour le chat"""
        categories = [
            {"id": "general", "name": "Général", "description": "Questions générales"},
            {"id": "agriculture", "name": "Agriculture", "description": "Questions agricoles"},
            {"id": "sante", "name": "Santé", "description": "Questions médicales"},
            {"id": "education", "name": "Éducation", "description": "Questions éducatives"},
            {"id": "culture", "name": "Culture", "description": "Culture burkinabè"},
            {"id": "economie", "name": "Économie", "description": "Questions économiques"},
            {"id": "technologie", "name": "Technologie", "description": "Questions techniques"},
            {"id": "droit", "name": "Droit", "description": "Questions juridiques"}
        ]
        
        for category in categories:
            existing = self.chat_categories.find_one({"id": category["id"]})
            if not existing:
                self.chat_categories.insert_one(category)
        
        logger.info("✅ Catégories de chat créées")
    
    def _create_initial_data(self):
        """Crée des données initiales si aucun fichier JSON n'existe"""
        # Données par défaut similaires à celles dans votre Database.init()
        default_contributions = [
            {
                "id": "1",
                "title": "Les techniques agricoles traditionnelles",
                "content": "Les techniques agricoles traditionnelles au Burkina Faso incluent la rotation des cultures, l'utilisation de compost naturel et les techniques d'irrigation traditionnelles comme les diguettes.",
                "category": "Agriculture",
                "source": "Ministère de l'Agriculture",
                "tags": ["agriculture", "tradition", "techniques"],
                "status": "validated",
                "expertId": "exp_001",
                "expertName": "Dr. Ibrahim Traoré",
                "createdAt": datetime(2024, 1, 15, 10, 30, 0),
                "validatedAt": datetime(2024, 1, 16, 14, 20, 0)
            }
        ]
        
        self.contributions.insert_many(default_contributions)
        self._migrate_experts()
        self._create_chat_categories()
        
        logger.info("✅ Données initiales créées")
    
    # ============================================
    # MÉTHODES POUR LE PANEL EXPERT
    # ============================================
    
    def get_contributions(self, filter_by: Dict = None, limit: int = 100) -> List[Dict]:
        """Récupère les contributions avec filtres"""
        query = filter_by or {}
        cursor = self.contributions.find(query).sort("createdAt", DESCENDING).limit(limit)
        return list(cursor)
    
    def get_all_contributions(self, limit: int = 1000) -> List[Dict]:
        """Récupère toutes les contributions (pour admin)"""
        cursor = self.contributions.find().sort("createdAt", DESCENDING).limit(limit)
        return list(cursor)
    
    def add_contribution(self, contribution_data: Dict) -> str:
        """Ajoute une nouvelle contribution"""
        contribution_data['_id'] = ObjectId()
        contribution_data['createdAt'] = datetime.now()
        
        result = self.contributions.insert_one(contribution_data)
        
        # Mettre à jour les stats
        self._update_system_stat('total_contributions', 1)
        
        return str(result.inserted_id)
    

    
    def update_contribution_status(self, contribution_id: str, status: str) -> bool:
        """Met à jour le statut d'une contribution"""
        update_data = {"status": status}
        if status == "validated":
            update_data["validatedAt"] = datetime.now()
        
        result = self.contributions.update_one(
            {"id": contribution_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def get_validation_queue(self) -> List[Dict]:
        """Récupère la file d'attente de validation"""
        return list(self.validation_queue.find({"validated": False}).sort("submittedAt", DESCENDING))
    
    def add_to_validation_queue(self, item_data: Dict) -> str:
        """Ajoute un élément à la file de validation"""
        item_data['_id'] = ObjectId()
        item_data['submittedAt'] = datetime.now()
        item_data['validated'] = False
        
        result = self.validation_queue.insert_one(item_data)
        return str(result.inserted_id)
    
    def validate_item(self, item_id: str, is_valid: bool, corrections: str = None) -> bool:
        """Valide un élément de la file d'attente"""
        update_data = {
            "validated": True,
            "validation_result": "approved" if is_valid else "rejected",
            "validated_at": datetime.now()
        }
        
        if corrections:
            update_data["corrections"] = corrections
        
        result = self.validation_queue.update_one(
            {"id": item_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def get_expert_by_credentials(self, username: str, password: str) -> Optional[Dict]:
        """Récupère un expert par ses identifiants"""
        expert = self.experts.find_one({
            "username": username,
            "password": password,
            "active": True
        })
        return expert
    
    # ============================================
    # MÉTHODES POUR LE PANEL ADMIN
    # ============================================
    
    def add_admin_log(self, action: str, admin_id: str = "system", details: Dict = None):
        """Ajoute un log admin"""
        log_entry = {
            '_id': ObjectId(),
            'timestamp': datetime.now(),
            'action': action,
            'admin_id': admin_id,
            'details': details or {},
            'ip_address': None  # À remplir si disponible
        }
        
        self.admin_logs.insert_one(log_entry)
    
    def get_admin_logs(self, limit: int = 100) -> List[Dict]:
        """Récupère les logs admin"""
        return list(self.admin_logs.find().sort("timestamp", DESCENDING).limit(limit))
    
    def get_system_stats(self) -> Dict:
        """Récupère les statistiques système"""
        stats = self.system_stats.find_one({'_id': 'global_stats'})
        if not stats:
            stats = {
                'total_contributions': 0,
                'pending_validations': 0,
                'total_experts': 0,
                'validation_rate': 0,
                'documents_count': 0,
                'total_conversations': 0,
                'active_users': 0
            }
            self.system_stats.insert_one({'_id': 'global_stats', **stats})
        
        # Retirer l'_id pour la réponse
        if '_id' in stats:
            del stats['_id']
        
        return stats
    
    def _update_system_stat(self, stat_name: str, increment: int = 1):
        """Met à jour une statistique système"""
        self.system_stats.update_one(
            {'_id': 'global_stats'},
            {'$inc': {stat_name: increment}},
            upsert=True
        )

    
    
    # ============================================
    # MÉTHODES POUR LE PANEL CHAT
    # ============================================
    
    def save_chat_conversation(self, conversation_data: Dict) -> str:
        """Sauvegarde une conversation de chat"""
        conversation_data['_id'] = ObjectId()
        conversation_data['timestamp'] = datetime.now()
        
        result = self.chat_conversations.insert_one(conversation_data)
        
        # Mettre à jour les stats
        self._update_system_stat('total_conversations', 1)
        
        return str(result.inserted_id)
    
    def get_chat_categories(self) -> List[Dict]:
        """Récupère toutes les catégories de chat"""
        return list(self.chat_categories.find().sort("name", ASCENDING))
    
    def get_chat_conversations(self, user_id: str = None, limit: int = 50) -> List[Dict]:
        """Récupère les conversations de chat"""
        query = {}
        if user_id:
            query['user_id'] = user_id
        
        return list(self.chat_conversations.find(query).sort("timestamp", DESCENDING).limit(limit))
    
    # ============================================
    # MÉTHODES POUR LES DOCUMENTS (PARTAGÉS)
    # ============================================
    
    def add_document(self, document_data: Dict) -> str:
        """Ajoute un nouveau document"""
        document_data['_id'] = ObjectId()
        document_data['uploaded_at'] = datetime.now()
        
        result = self.documents.insert_one(document_data)
        
        # Mettre à jour les stats
        self._update_system_stat('documents_count', 1)
        
        return str(result.inserted_id)
    
    def get_documents(self, category: str = None) -> List[Dict]:
        """Récupère les documents avec filtre de catégorie"""
        query = {}
        if category:
            query['category'] = category
        
        return list(self.documents.find(query).sort("uploaded_at", DESCENDING))
    
    def get_all_documents(self, limit: int = 1000) -> List[Dict]:
        """Récupère tous les documents (pour admin)"""
        return list(self.documents.find().sort("uploaded_at", DESCENDING).limit(limit))
    
    # ============================================
    # MÉTHODES POUR LES NOTIFICATIONS INTER-PANELS
    # ============================================
    
    def create_notification(self, recipient_type: str, message: str, 
                            action_type: str, related_id: str = None,
                            recipient_id: str = None):
        """Crée une notification pour un panel spécifique"""
        notification = {
            '_id': ObjectId(),
            'recipient_type': recipient_type,  # 'admin', 'expert', 'user'
            'recipient_id': recipient_id,
            'message': message,
            'action_type': action_type,
            'related_id': related_id,
            'read': False,
            'created_at': datetime.now()
        }
        
        self.notifications.insert_one(notification)
        return str(notification['_id'])
    
    def get_unread_notifications(self, recipient_type: str, recipient_id: str = None) -> List[Dict]:
        """Récupère les notifications non lues"""
        query = {
            'recipient_type': recipient_type,
            'read': False
        }
        
        if recipient_id:
            query['recipient_id'] = recipient_id
        
        return list(self.notifications.find(query).sort("created_at", DESCENDING))
    
    # ============================================
    # MÉTHODES UTILITAIRES
    # ============================================
    
    def close_connection(self):
        """Ferme la connexion MongoDB"""
        if self.client:
            self.client.close()
            logger.info("🔌 Connexion MongoDB fermée")

# Instance globale de la base de données
db = MongoDB()