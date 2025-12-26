# ai/service/tts_service.py
"""
Service de synthèse vocale (TTS) pour langues burkinabè
Supporte mooré et dioula avec audio natif
"""
import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class TTSService:
    """
    Service de Text-to-Speech pour mooré et dioula
    
    Fonctionnalités:
    1. Audio pré-enregistré natif (haute qualité)
    2. Génération TTS de base (fallback)
    3. Future: Modèle Coqui TTS personnalisé
    """
    
    def __init__(self):
        # Chemins des dossiers audio
        self.base_path = Path(__file__).parent.parent.parent / "audio"
        self.moree_path = self.base_path / "moree"
        self.dioula_path = self.base_path / "dioula"
        self.generated_path = self.base_path / "generated"
        
        # Créer les dossiers si nécessaires
        self.moree_path.mkdir(parents=True, exist_ok=True)
        self.dioula_path.mkdir(parents=True, exist_ok=True)
        self.generated_path.mkdir(parents=True, exist_ok=True)
        
        # Cache des audios pré-enregistrés
        self.audio_cache = {
            "mo": {},  # mooré
            "di": {}   # dioula
        }
        
        # Charger l'index des audios pré-enregistrés
        self._load_audio_index()
        
        # TTS Engine (pyttsx3 comme fallback)
        self.tts_available = False
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_available = True
            logger.info("✅ TTS Engine (pyttsx3) initialisé")
        except Exception as e:
            logger.warning(f"⚠️ TTS Engine non disponible: {e}")
            self.tts_engine = None
    
    def _load_audio_index(self):
        """
        Charge l'index des fichiers audio pré-enregistrés
        Format: audio_index.json
        """
        index_file = self.base_path / "audio_index.json"
        
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    self.audio_cache = index_data
                    logger.info(f"📚 Index audio chargé: {len(self.audio_cache.get('mo', {}))} mooré, {len(self.audio_cache.get('di', {}))} dioula")
            except Exception as e:
                logger.error(f"❌ Erreur chargement index audio: {e}")
        else:
            logger.info("📝 Pas d'index audio trouvé, création d'un nouveau")
            self._create_default_index()
    
    def _create_default_index(self):
        """
        Crée un index par défaut avec structure pour audios natifs
        """
        default_index = {
            "mo": {
                # Salutations
                "Ne y kɔɔrɛ": {"file": "greetings/bonjour.mp3", "category": "greeting"},
                "Yamba": {"file": "greetings/merci.mp3", "category": "thanks"},
                "La fii": {"file": "greetings/aurevoir.mp3", "category": "bye"},
                
                # Questions communes
                "Fo kẽ be kɩtugã?": {"file": "common/question_help.mp3", "category": "question"},
                
                # Agriculture (exemples)
                "Moringa sã yaa?": {"file": "agriculture/moringa_info.mp3", "category": "agriculture"},
                "Bãndã tɩ wakat?": {"file": "agriculture/when_cultivate.mp3", "category": "agriculture"},
            },
            "di": {
                # Salutations
                "I ni sɔgɔma": {"file": "greetings/bonjour.mp3", "category": "greeting"},
                "I ni ce": {"file": "greetings/merci.mp3", "category": "thanks"},
                "An bi se": {"file": "greetings/aurevoir.mp3", "category": "bye"},
                
                # Questions communes
                "N bɛ se ka i dɛmɛ cogo di?": {"file": "common/question_help.mp3", "category": "question"},
                
                # Agriculture
                "Moringa ye mun ye?": {"file": "agriculture/moringa_info.mp3", "category": "agriculture"},
            }
        }
        
        # Sauvegarder l'index par défaut
        index_file = self.base_path / "audio_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(default_index, f, ensure_ascii=False, indent=2)
        
        self.audio_cache = default_index
        logger.info("✅ Index audio par défaut créé")
    
    def get_audio_for_text(self, text: str, language: str) -> Optional[str]:
        """
        Récupère le chemin de l'audio pré-enregistré pour un texte donné
        
        Args:
            text: Texte en mooré ou dioula
            language: 'mo' (mooré) ou 'di' (dioula)
        
        Returns:
            Chemin relatif du fichier audio ou None
        """
        if language not in self.audio_cache:
            return None
        
        # Recherche exacte
        audio_info = self.audio_cache[language].get(text)
        if audio_info:
            audio_file = audio_info.get("file")
            
            # Construire le chemin complet
            if language == "mo":
                full_path = self.moree_path / audio_file
            else:
                full_path = self.dioula_path / audio_file
            
            # Vérifier si le fichier existe
            if full_path.exists():
                # Retourner le chemin relatif pour l'API
                return f"/audio/{language}/{audio_file}"
            else:
                logger.warning(f"⚠️ Fichier audio introuvable: {full_path}")
        
        return None
    
    def generate_audio(self, text: str, language: str) -> Tuple[Optional[str], str]:
        """
        Génère ou récupère l'audio pour un texte donné
        
        Args:
            text: Texte à convertir en audio
            language: 'mo', 'di', ou 'fr'
        
        Returns:
            Tuple (audio_url, mode)
            - audio_url: URL de l'audio ou None
            - mode: 'pre_recorded', 'tts_generated', 'not_available'
        """
        # Français: pas d'audio
        if language == "fr":
            return None, "not_available"
        
        # 1. Chercher dans les audios pré-enregistrés
        audio_url = self.get_audio_for_text(text, language)
        if audio_url:
            logger.info(f"🎵 Audio pré-enregistré trouvé: {audio_url}")
            return audio_url, "pre_recorded"
        
        # 2. Générer avec TTS si disponible
        if self.tts_available:
            try:
                generated_url = self._generate_tts(text, language)
                if generated_url:
                    logger.info(f"🔊 Audio TTS généré: {generated_url}")
                    return generated_url, "tts_generated"
            except Exception as e:
                logger.error(f"❌ Erreur génération TTS: {e}")
        
        # 3. Pas d'audio disponible
        logger.info(f"⚠️ Pas d'audio disponible pour: '{text[:50]}...'")
        return None, "not_available"
    
    def _generate_tts(self, text: str, language: str) -> Optional[str]:
        """
        Génère un fichier audio avec pyttsx3 (fallback)
        """
        if not self.tts_engine:
            return None
        
        try:
            # Créer un hash unique pour le fichier
            text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{language}_{timestamp}_{text_hash}.mp3"
            output_path = self.generated_path / filename
            
            # Configurer la voix (approximatif pour mooré/dioula)
            # Note: pyttsx3 n'a pas de voix natives pour ces langues
            # La prononciation sera approximative
            
            # Sauvegarder vers fichier
            self.tts_engine.save_to_file(text, str(output_path))
            self.tts_engine.runAndWait()
            
            # Retourner l'URL relative
            return f"/audio/generated/{filename}"
            
        except Exception as e:
            logger.error(f"❌ Erreur TTS génération: {e}")
            return None
    
    def add_native_audio(self, text: str, language: str, audio_file: str, category: str = "general") -> bool:
        """
        Ajoute un nouvel audio natif à l'index
        
        Args:
            text: Texte en mooré/dioula
            language: 'mo' ou 'di'
            audio_file: Nom du fichier audio (relatif au dossier langue)
            category: Catégorie (greeting, agriculture, etc.)
        
        Returns:
            True si ajouté avec succès
        """
        if language not in ['mo', 'di']:
            logger.error(f"❌ Langue invalide: {language}")
            return False
        
        # Ajouter à l'index en mémoire
        if language not in self.audio_cache:
            self.audio_cache[language] = {}
        
        self.audio_cache[language][text] = {
            "file": audio_file,
            "category": category,
            "added_at": datetime.now().isoformat()
        }
        
        # Sauvegarder l'index
        index_file = self.base_path / "audio_index.json"
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(self.audio_cache, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Audio natif ajouté: {text} → {audio_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde index: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques du service TTS
        """
        return {
            "moree_audios": len(self.audio_cache.get("mo", {})),
            "dioula_audios": len(self.audio_cache.get("di", {})),
            "tts_available": self.tts_available,
            "base_path": str(self.base_path),
            "categories": {
                "mo": self._count_by_category("mo"),
                "di": self._count_by_category("di")
            }
        }
    
    def _count_by_category(self, language: str) -> Dict[str, int]:
        """Compte les audios par catégorie"""
        categories = {}
        for text, info in self.audio_cache.get(language, {}).items():
            cat = info.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1
        return categories


# Instance globale
tts_service = TTSService()
