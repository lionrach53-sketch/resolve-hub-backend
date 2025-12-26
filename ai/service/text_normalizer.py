# ai/service/text_normalizer.py
"""
Normalisation et correction automatique des textes avec fautes de frappe
Gère les erreurs courantes en français et dans le contexte burkinabè
"""
import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class TextNormalizer:
    """
    Normalise et corrige automatiquement les fautes de frappe courantes
    """
    
    def __init__(self):
        # Corrections de fautes courantes en français
        self.common_typos = {
            
            "utilizer": "utiliser",
            "utilisé": "utiliser",
            "utilisr": "utiliser",
            "utilise": "utiliser",
            
            "coment": "comment",
            "commant": "comment",
            "comant": "comment",
            
            "ou": "où",  # Contextuel
            "sa": "ça",  # Contextuel
            
            # Fautes de frappe rapides (touches adjacentes)
            "commentt": "comment",
            "commemt": "comment",
            "commebt": "comment",
            "commetn": "comment",
            "ocmment": "comment",
            "coment": "comment",
            "comant": "comment",
            
            "tutu": "tu",
            "ttu": "tu",
            
            "tappel": "t'appel",
            "tapel": "t'appel",
            "tappelle": "t'appelles",
            "tapelle": "t'appelles",
            "tapel": "t'appel",
            
            "jee": "je",
            "jje": "je",
            "jeu": "je",
            
            "parque": "parle",
            "parlke": "parle",
            "prle": "parle",
            "prale": "parle",
            
            "francais": "français",
            "francias": "français",
            "fransais": "français",
            "francai": "français",
            "francai": "français",
            
            "merçi": "merci",
            "meci": "merci",
            "mreci": "merci",
            "merdi": "merci",
            
            "bonjur": "bonjour",
            "bonjourr": "bonjour",
            "bonjou": "bonjour",
            "bjr": "bonjour",
            "bonour": "bonjour",
            "bonjr": "bonjour",
            "bnjr": "bonjour",
            
            "saltu": "salut",
            "salaut": "salut",
            "salu": "salut",
            "slut": "salut",
            "salout": "salut",
            
            "merçi": "merci",
            "meci": "merci",
            "mreci": "merci",
            "merdi": "merci",
            "mérci": "merci",
            "mersi": "merci",
            
            "beaucoup": "beaucoup",
            "bokoup": "beaucoup",
            "boucoup": "beaucoup",
            "bocoup": "beaucoup",
            "beaucoups": "beaucoup",
            
            "quii": "qui",
            "qiu": "qui",
            "qu": "qui",
            "ki": "qui",
            
            "esst": "est",
            "eest": "est",
            
            "sa": "ça",
            "ca": "ça",
            "cà": "ça",
            
            "pouvoir": "pouvoir",
            "pouvoire": "pouvoir",
            "pouvor": "pouvoir",
            
            "aider": "aider",
            "aidé": "aider",
            "aiddé": "aider",
            
            "faire": "faire",
            "fair": "faire",
            "fer": "faire",
            
            "metre": "mettre",
            "mètre": "mettre",
            "metrte": "mettre",
            
            "voualir": "vouloir",
            "voulior": "vouloir",
            "vouloire": "vouloir",
            
            # Contractions et abréviations
            "stp": "s'il te plaît",
            "svp": "s'il vous plaît",
            "pk": "pourquoi",
            "pq": "pourquoi",
            "prkoi": "pourquoi",
            "pcq": "parce que",
            "pcke": "parce que",
            "tkt": "ne t'inquiète pas",
            "jsp": "je ne sais pas",
            "jpp": "je ne peux pas",
            "jpeu": "je peux",
            "jpeux": "je peux",
            
            # Erreurs avec apostrophes
            "jai": "j'ai",
            "j'ai": "j'ai",
            "jai": "j'ai",
            "cest": "c'est",
            "c'est": "c'est",
            "sest": "s'est",
            "ces": "c'est",  # Contextuel
            
            
            "moriga": "moringa",
            "moringa": "moringa",
            "moringua": "moringa",
            "morniga": "moringa",
            "moringas": "moringa",
            
            "karite": "karité",
            "karité": "karité",
            "kariter": "karité",
            
            "mil": "mil",
            "mille": "mil",  # Contextuel agriculture
            
            "sorgho": "sorgho",
            "sorgo": "sorgho",
            "sorgot": "sorgho",
            
            # Mots courants mal orthographiés
            "quel": "quel",
            "quelle": "quelle",
            "kel": "quel",
            "kelle": "quelle",
            
            "aussi": "aussi",
            "ossi": "aussi",
            "ausi": "aussi",
            
            "avec": "avec",
            "avek": "avec",
            "aver": "avec",
            
            "plante": "plante",
            "plente": "plante",
            "plantte": "plante",
            
            "maladie": "maladie",
            "maladis": "maladie",
            "maladi": "maladie",
            
            "fatigue": "fatigue",
            "fatige": "fatigue",
            "fatigué": "fatigue",
        }
        
        # Variations acceptables (pas vraiment des fautes)
        self.variations = {
            "moore": ["mooré", "moré", "more"],
            "dioula": ["dyula", "jula", "diola"],
            "burkina": ["bourkina", "burkinabé", "burkinabè"],
        }
        
        # Mots à préserver (ne pas corriger)
        self.preserve_words = {
            "moringa", "karité", "shea", "mil", "sorgho", "fonio",
            "baobab", "néré", "soumbala", "tô", "dolo",
            "moore", "mooré", "dioula", "fulfuldé", "bissa",
            "fcfa", "cfa"
        }
    
    def normalize(self, text: str) -> str:
        """
        Normalise le texte en corrigeant les fautes courantes
        """
        if not text or not text.strip():
            return text
        
        original_text = text
        
        # 1. Normalisation de base
        text = text.strip()
        
        # 2. Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # 3. Corriger les contractions mal formées
        text = re.sub(r'\bj\s+ai\b', "j'ai", text, flags=re.IGNORECASE)
        text = re.sub(r'\bc\s+est\b', "c'est", text, flags=re.IGNORECASE)
        text = re.sub(r'\bt\s+as\b', "t'as", text, flags=re.IGNORECASE)
        text = re.sub(r'\bs\s+il\b', "s'il", text, flags=re.IGNORECASE)
        text = re.sub(r'\bqu\s+est\s+ce\b', "qu'est-ce", text, flags=re.IGNORECASE)
        
        # 4. Corriger les mots avec le dictionnaire
        words = text.split()
        corrected_words = []
        
        for word in words:
            word_lower = word.lower()
            
            # Préserver les mots importants
            if word_lower in self.preserve_words:
                corrected_words.append(word)
                continue
            
            # Enlever la ponctuation pour la comparaison
            word_clean = re.sub(r'[^\w\'-]', '', word_lower)
            
            # Vérifier si c'est une faute connue
            if word_clean in self.common_typos:
                correction = self.common_typos[word_clean]
                
                # Préserver la casse du premier caractère
                if word[0].isupper():
                    correction = correction.capitalize()
                
                # Remettre la ponctuation
                punctuation = re.findall(r'[^\w\'-]', word)
                if punctuation:
                    correction += ''.join(punctuation)
                
                corrected_words.append(correction)
                logger.info(f"📝 Correction: '{word}' → '{correction}'")
            else:
                corrected_words.append(word)
        
        corrected_text = ' '.join(corrected_words)
        
        # 5. Log si correction effectuée
        if corrected_text.lower() != original_text.lower():
            logger.info(f"✏️ Texte normalisé: '{original_text}' → '{corrected_text}'")
        
        return corrected_text
    
    def calculate_similarity(self, word1: str, word2: str) -> float:
        """
        Calcule la similarité entre deux mots (distance de Levenshtein normalisée)
        Retourne un score entre 0 (différent) et 1 (identique)
        """
        word1 = word1.lower()
        word2 = word2.lower()
        
        if word1 == word2:
            return 1.0
        
        # Distance de Levenshtein simplifiée
        len1, len2 = len(word1), len(word2)
        
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # Matrice de distance
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if word1[i-1] == word2[j-1] else 1
                matrix[i][j] = min(
                    matrix[i-1][j] + 1,      # Suppression
                    matrix[i][j-1] + 1,      # Insertion
                    matrix[i-1][j-1] + cost  # Substitution
                )
        
        distance = matrix[len1][len2]
        max_len = max(len1, len2)
        
        # Normaliser entre 0 et 1
        similarity = 1 - (distance / max_len)
        return similarity
    
    def find_closest_word(self, word: str, candidates: List[str], threshold: float = 0.7) -> Tuple[str, float]:
        """
        Trouve le mot le plus proche dans une liste de candidats
        Retourne (mot_trouve, score_similarite)
        """
        word_lower = word.lower()
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            score = self.calculate_similarity(word_lower, candidate.lower())
            if score > best_score:
                best_score = score
                best_match = candidate
        
        if best_score >= threshold:
            return best_match, best_score
        
        return word, 0.0
    
    def smart_correct(self, text: str, context_words: List[str] = None) -> str:
        """
        Correction intelligente avec contexte
        Utilise des mots de contexte pour améliorer la correction
        """
        # Normalisation de base
        text = self.normalize(text)
        
        # Si pas de contexte, retourner la normalisation simple
        if not context_words:
            return text
        
        # Correction avec contexte
        words = text.split()
        corrected = []
        
        for word in words:
            word_clean = re.sub(r'[^\w\'-]', '', word.lower())
            
            # Vérifier si proche d'un mot du contexte
            if len(word_clean) > 3:  # Seulement mots de 4+ caractères
                closest, score = self.find_closest_word(word_clean, context_words, threshold=0.75)
                
                if score > 0.75 and closest != word_clean:
                    logger.info(f"🎯 Correction contextuelle: '{word}' → '{closest}' (score: {score:.2f})")
                    corrected.append(closest)
                    continue
            
            corrected.append(word)
        
        return ' '.join(corrected)


# Instance globale
text_normalizer = TextNormalizer()
