"""
Service Speech-to-Text (STT) pour Mooré et Dioula

Utilise OpenAI Whisper pour la reconnaissance vocale en langues locales.
Whisper supporte 100+ langues et fonctionne bien pour les langues africaines.
"""

import os
import logging
from pathlib import Path
from typing import Tuple, Optional
import tempfile

# Ajouter FFmpeg au PATH pour Whisper
FFMPEG_PATH = r"C:\ffmpeg\ffmpeg-master-latest-win64-gpl\bin"
if os.path.exists(FFMPEG_PATH) and FFMPEG_PATH not in os.environ.get("PATH", ""):
    os.environ["PATH"] = FFMPEG_PATH + os.pathsep + os.environ.get("PATH", "")

logger = logging.getLogger(__name__)

class STTService:
    """Service de reconnaissance vocale pour langues locales"""
    
    def __init__(self):
        self.whisper_available = False
        self.model = None
        self.model_size = "base"  # Options: tiny, base, small, medium, large
        
        # Tentative de chargement de Whisper
        try:
            import whisper
            self.whisper_available = True
            logger.info("✅ Whisper disponible pour STT")
            
            # Charger le modèle (base par défaut, bon compromis vitesse/qualité)
            try:
                self.model = whisper.load_model(self.model_size)
                logger.info(f"✅ Modèle Whisper '{self.model_size}' chargé")
            except Exception as e:
                logger.warning(f"⚠️ Erreur chargement modèle Whisper: {e}")
                self.whisper_available = False
                
        except ImportError:
            logger.warning("⚠️ Whisper non installé. STT non disponible.")
            logger.info("💡 Installer avec: pip install openai-whisper")
    
    def transcribe_audio(
        self, 
        audio_path: Path,
        language: Optional[str] = None
    ) -> Tuple[str, str, float]:
        """
        Transcrit un fichier audio en texte
        
        Args:
            audio_path: Chemin vers le fichier audio
            language: Code langue ("mo" pour mooré, "di" pour dioula, None = auto-détection)
        
        Returns:
            (transcription, langue_détectée, confiance)
        """
        if not self.whisper_available or not self.model:
            return ("", "unknown", 0.0)
        
        try:
            # Mapper codes internes vers codes Whisper
            language_map = {
                "mo": "mos",  # Mooré (code ISO 639-3)
                "di": "dyu",  # Dioula (code ISO 639-3)
                "fr": "fr"
            }
            
            whisper_lang = None
            if language:
                whisper_lang = language_map.get(language, language)
            
            # Transcription avec Whisper
            logger.info(f"🎤 Transcription audio: {audio_path.name}")
            
            # Options de transcription
            options = {
                "language": whisper_lang,  # None = auto-détection
                "task": "transcribe",  # "transcribe" ou "translate"
                "fp16": False,  # Désactiver FP16 pour compatibilité CPU
                "verbose": False  # Réduire les logs
            }
            
            # Whisper accepte directement les fichiers audio (WAV, MP3, WebM, etc.)
            result = self.model.transcribe(str(audio_path), **options)
            
            transcription = result.get("text", "").strip()
            detected_lang = result.get("language", "unknown")
            
            # Mapper code Whisper vers code interne
            reverse_map = {v: k for k, v in language_map.items()}
            detected_lang_code = reverse_map.get(detected_lang, detected_lang)
            
            # Confiance (moyenne des segments)
            segments = result.get("segments", [])
            if segments:
                confidences = [1.0 - seg.get("no_speech_prob", 0.5) for seg in segments]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.8
            else:
                avg_confidence = 0.8  # Valeur par défaut
            
            logger.info(f"✅ Transcription: '{transcription[:50]}...' ({detected_lang_code}, confiance: {avg_confidence:.2f})")
            
            return (transcription, detected_lang_code, avg_confidence)
            
        except Exception as e:
            logger.error(f"❌ Erreur transcription: {e}")
            import traceback
            traceback.print_exc()
            return ("", "unknown", 0.0)
    
    def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: Optional[str] = None
    ) -> Tuple[str, str, float]:
        """
        Transcrit des données audio en mémoire
        
        Args:
            audio_bytes: Données audio en bytes
            filename: Nom du fichier (pour extension)
            language: Code langue optionnel
        
        Returns:
            (transcription, langue_détectée, confiance)
        """
        if not self.whisper_available:
            return ("", "unknown", 0.0)
        
        # Créer fichier temporaire
        with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = Path(tmp_file.name)
        
        try:
            result = self.transcribe_audio(tmp_path, language)
            return result
        finally:
            # Nettoyer fichier temporaire
            try:
                tmp_path.unlink()
            except:
                pass
    
    def is_available(self) -> bool:
        """Vérifie si le service STT est disponible"""
        return self.whisper_available and self.model is not None
    
    def get_supported_languages(self) -> dict:
        """Retourne les langues supportées"""
        return {
            "mo": {
                "name": "Mooré",
                "iso_code": "mos",
                "supported": self.whisper_available
            },
            "di": {
                "name": "Dioula",
                "iso_code": "dyu",
                "supported": self.whisper_available
            },
            "fr": {
                "name": "Français",
                "iso_code": "fr",
                "supported": self.whisper_available
            }
        }
    
    def change_model_size(self, size: str = "base"):
        """
        Change la taille du modèle Whisper
        
        Args:
            size: "tiny", "base", "small", "medium", "large"
        
        Tiny: 39M paramètres, ~1GB RAM, très rapide
        Base: 74M paramètres, ~1GB RAM, rapide (RECOMMANDÉ)
        Small: 244M paramètres, ~2GB RAM, bon
        Medium: 769M paramètres, ~5GB RAM, très bon
        Large: 1550M paramètres, ~10GB RAM, excellent
        """
        if not self.whisper_available:
            logger.warning("⚠️ Whisper non disponible")
            return False
        
        try:
            import whisper
            logger.info(f"🔄 Chargement modèle Whisper '{size}'...")
            self.model = whisper.load_model(size)
            self.model_size = size
            logger.info(f"✅ Modèle '{size}' chargé")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur changement modèle: {e}")
            return False


# Instance globale
stt_service = STTService()


# Exemple d'utilisation
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python stt_service.py <fichier_audio.wav>")
        print("\nModèles disponibles:")
        print("  tiny   : 39M params, ~1GB RAM, très rapide")
        print("  base   : 74M params, ~1GB RAM, rapide (défaut)")
        print("  small  : 244M params, ~2GB RAM, bon")
        print("  medium : 769M params, ~5GB RAM, très bon")
        print("  large  : 1550M params, ~10GB RAM, excellent")
        sys.exit(1)
    
    audio_file = Path(sys.argv[1])
    
    if not audio_file.exists():
        print(f"❌ Fichier introuvable: {audio_file}")
        sys.exit(1)
    
    # Test transcription
    print(f"\n🎤 Transcription de: {audio_file.name}")
    print("⏳ Traitement en cours...\n")
    
    text, lang, confidence = stt_service.transcribe_audio(audio_file)
    
    print("=" * 60)
    print(f"📝 Transcription: {text}")
    print(f"🌍 Langue: {lang}")
    print(f"📊 Confiance: {confidence:.2%}")
    print("=" * 60)
