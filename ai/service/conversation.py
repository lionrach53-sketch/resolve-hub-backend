# ai/service/conversation.py
"""
Service de conversation intelligent avec détection de langue et analyse contextuelle
"""
import logging
import re
from typing import Tuple, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationService:
    """
    Service de conversation intelligent qui :
    - Détecte la langue (français, mooré, dioula)
    - Analyse l'intention (salutation, question, demande d'aide)
    - Génère des réponses contextuelles
    - Pose des questions de clarification si nécessaire
    """
    
    def __init__(self):
        # Patterns de salutations par langue
        self.greetings = {
            'fr': ['bonjour', 'salut', 'bonsoir', 'hello', 'hi', 'coucou', 'hey'],
            'mo': ['ne y kɔɔrɛ', 'ne y kyɛɛrɛ', 'ne y zɔɔrɛ', 'woto', 'an-soama'],
            'di': ['i ni sɔgɔma', 'i ni tile', 'i ni wula', 'aw ni ce']
        }
        
        # Patterns de remerciements
        self.thanks = {
            'fr': ['merci', 'thank', 'grand merci', "c'est gentil", 'ok merci'],
            'mo': ['barka', 'yamba', 'n barika', 'la fii'],
            'di': ['i ni ce', 'i ni ɲininka', 'an bi se']
        }
        
        # Patterns d'affirmation/satisfaction
        self.affirmations = {
            'fr': ['oui', 'ok', 'bien', 'compris', 'parfait', "d'accord", 'exact'],
            'mo': ['eeŋ', 'aaŋ', 'awã', 'n bãng', 'raabo'],
            'di': ['ɔ̃w', 'awɔ', 'tiɲɛ', 'a ka ɲi']
        }
        
        # Mots-clés par langue pour détection
        self.lang_markers = {
            'fr': ['est', 'le', 'la', 'les', 'un', 'une', 'des', 'que', 'qui', 'comment', 'pourquoi', 'quand'],
            'mo': ['yɩlɩg', 'woto', 'yaa', 'ne', 'sãn', 'kẽ', 'n', 'na', 'bɩ', 'pʋgẽ', 'taaba'],
            'di': ['ye', 'ka', 'bɛ', 'kɛ', 'ni', 'ma', 'wa', 'kɔrɔ', 'fɔ', 'min', 'tɛ']
        }
        
        # Questions types par catégorie
        self.follow_up_questions = {
            'histoire': {
                'fr': "Voulez-vous en savoir plus sur l'histoire du Burkina Faso, ses personnalités ou ses événements importants ?",
                'mo': "Y bãng n ka Burkina Faso tarek, n taaba yamb ned n sã n kẽnd be kɔɔga ?",
                'di': "I b'a fɛ ka Burkina Faso tariku, a ka mɔgɔba walima a ka fɛn kunba ye wa ?"
            },
            'agriculture': {
                'fr': "Souhaitez-vous des informations sur les cultures, les techniques agricoles ou les saisons de plantation ?",
                'mo': "Y bãng n ka bʋʋlg tɩɩsa, bãnd tigsi ned bãnd yĩnga kɔɔga ?",
                'di': "I b'a fɛ ka sɛnɛkɛ kow, sɛnɛkɛli kow walima donkow ye wa ?"
            },
            'sante': {
                'fr': "Avez-vous besoin d'informations sur une maladie spécifique, la prévention ou les remèdes traditionnels ?",
                'mo': "Y bãng kɩndɩg tɩɩsa, kɩndɩg yɩlsgo ned tãab tɩɩm kɔɔga ?",
                'di': "I b'a fɛ ka bana dɔ ye, bana tanga walima fura kow ye wa ?"
            },
            'general': {
                'fr': "Comment puis-je vous aider aujourd'hui ? Vous avez des questions sur l'agriculture, la santé, l'histoire, ou autre chose ?",
                'mo': "Woto n tõe yɩɩlã yem bo ? Y kẽ kɩtugã bãndã, kɩndɩgã, tarekã ned tʋʋma be sãn ?",
                'di': "Ne bɛ se ka i dɛmɛ cogo di bi ? I ka ɲininka b'i fɛ sɛnɛkɛ, kɛnɛya, tariku walima fɛn wɛrɛ kan wa ?"
            }
        }
        
        # Réponses aux salutations
        self.greeting_responses = {
            'fr': [
                "Bonjour ! Je suis l'IA Souveraine du Burkina Faso. Comment puis-je vous aider aujourd'hui ?",
                "Salut ! Ravi de vous parler. Que voulez-vous savoir ?",
                "Bonjour ! Je suis là pour répondre à vos questions sur le Burkina Faso. Que cherchez-vous ?"
            ],
            'mo': [
                "Ne y kɔɔrɛ ! M yaa Burkina Faso AI taaba. Woto n tõe yɩɩlã yem bo ?",
                "An-soama ! N yaa yõodo n yɩ ne. Fo sãn ye ?",
                "Waka ! M yaa yãnd b'a yɩ ne Burkina Faso sũur. Fo kẽ be kɩtugã ?"
            ],
            'di': [
                "I ni sɔgɔma ! Ne ye Burkina Faso AI ye. Ne bɛ se ka i dɛmɛ cogo di ?",
                "I ni ce ! Ne b'a fɛ ka kuma ni i ye. I b'a fɛ ka mun lɔn ?",
                "I ka kɛnɛ ! Ne ye yan ka i ɲininkaw jaabi. I be mun ɲini ?"
            ]
        }
    
    def detect_language(self, text: str) -> str:
        """
        Détecte la langue du texte (fr, mo, di)
        """
        import re
        
        text_lower = text.lower()
        scores = {'fr': 0, 'mo': 0, 'di': 0}
        
        # Compter les marqueurs de langue avec word boundaries
        for lang, markers in self.lang_markers.items():
            for marker in markers:
                # Utiliser word boundary pour éviter les faux positifs
                # \b ne marche pas avec les caractères spéciaux, alors on cherche avec espaces/ponctuation
                pattern = r'(?:^|\s|[,;.!?])' + re.escape(marker) + r'(?:\s|[,;.!?]|$)'
                if re.search(pattern, text_lower):
                    scores[lang] += 1
        
        # Vérifier les caractères spéciaux mooré et dioula
        if any(char in text for char in ['ɩ', 'ɛ', 'ɔ', 'ʋ', 'ɲ', 'ŋ']):
            if 'ɩ' in text or 'ʋ' in text or 'ɛ' in text:
                scores['mo'] += 3
            if 'ɔ' in text or 'ɲ' in text:
                scores['di'] += 2
        
        # Retourner la langue avec le score le plus élevé
        detected = max(scores, key=scores.get)
        
        # Si aucun marqueur, par défaut français
        if scores[detected] == 0:
            return 'fr'
        
        logger.info(f"🌍 Langue détectée: {detected} (scores: {scores})")
        return detected
    
    def detect_intent(self, text: str, lang: str) -> str:
        """
        Détecte l'intention de l'utilisateur :
        - greeting: salutation
        - thanks: remerciement
        - affirmation: confirmation
        - question: question
        - clarification: demande de clarification
        """
        text_lower = text.lower()
        
        # Vérifier salutation
        if any(greet in text_lower for greet in self.greetings.get(lang, [])):
            return 'greeting'
        
        # Vérifier remerciement
        if any(thank in text_lower for thank in self.thanks.get(lang, [])):
            return 'thanks'
        
        # Vérifier affirmation
        if any(affirm in text_lower for affirm in self.affirmations.get(lang, [])):
            return 'affirmation'
        
        # Vérifier si c'est une question
        question_markers = {
            'fr': ['?', 'comment', 'pourquoi', 'quand', 'où', 'qui', 'que', 'quel', 'quelle'],
            'mo': ['?', 'woto', 'yaa', 'fo', 'ãnsɛɛm', 'kãn'],
            'di': ['?', 'mun', 'cogo di', 'joli', 'yan', 'min']
        }
        
        if any(marker in text_lower for marker in question_markers.get(lang, [])):
            return 'question'
        
        return 'statement'
    
    def generate_greeting_response(self, lang: str) -> str:
        """Génère une réponse de salutation"""
        import random
        responses = self.greeting_responses.get(lang, self.greeting_responses['fr'])
        return random.choice(responses)
    
    def generate_thanks_response(self, lang: str) -> str:
        """Génère une réponse aux remerciements"""
        responses = {
            'fr': "De rien ! N'hésitez pas si vous avez d'autres questions. 😊",
            'mo': "Bãmb ra ! Fo kẽ kɩtugã be, fo tɩ n yel.",
            'di': "A tɛ fɔ ! N'i bɛ ɲininka wɛrɛ, i k'a fɔ ne ye."
        }
        return responses.get(lang, responses['fr'])
    
    def suggest_follow_up(self, category: str, lang: str) -> str:
        """Suggère une question de suivi selon la catégorie"""
        # Toujours retourner une question générale car nous avons de nouvelles catégories
        # qui ne sont pas dans le dictionnaire follow_up_questions
        responses = {
            'fr': f"Avez-vous d'autres questions sur {category} ou un autre sujet ?",
            'mo': f"Y kẽ kɩtugã be {category} ned tʋʋma be sãn ?",
            'di': f"I ka ɲininka wɛrɛw b'i fɛ {category} walima fɛn wɛrɛ kan wa ?"
        }
        return responses.get(lang, responses['fr'])
    
    def is_too_vague(self, text: str) -> bool:
        """Détermine si la question est trop vague"""
        words = text.lower().split()
        
        # Questions d'un ou deux mots sont généralement vagues
        if len(words) <= 2:
            return True
        
        # Patterns vagues
        vague_patterns = [
            r'^(quoi|comment|pourquoi|qui|que)\s*$',
            r'^(mun|woto|yaa)\s*$',
            r'^(aide|help|info)\s*$',
        ]
        
        return any(re.match(pattern, text.lower().strip()) for pattern in vague_patterns)
    
    def format_response(self, raw_answer: str, lang: str, intent: str, category: str, add_follow_up: bool = True) -> str:
        """
        Formate la réponse de manière conversationnelle
        IMPORTANT: Force la langue de la réponse selon la langue détectée
        """
        # Nettoyer la réponse brute
        answer = raw_answer.strip()
        
        # Retirer les préfixes génériques
        prefixes_to_remove = [
            "Selon les connaissances locales :",
            "Selon les connaissances locales: ",
            "D'après les informations :",
            "Voici ce que je sais :"
        ]
        
        for prefix in prefixes_to_remove:
            if answer.startswith(prefix):
                answer = answer[len(prefix):].strip()
        
        # Si c'est une salutation, retourner juste la salutation
        if intent == 'greeting':
            return self.generate_greeting_response(lang)
        
        # Si c'est un remerciement
        if intent == 'thanks':
            return self.generate_thanks_response(lang)
        
        # VÉRIFIER SI LA RÉPONSE EST DANS LA MAUVAISE LANGUE
        # Si question en français mais réponse contient caractères mooré/dioula
        answer_lang = self.detect_language(answer)
        
        if lang != answer_lang:
            # La réponse est dans une mauvaise langue
            # Ajouter un message d'excuse dans la langue de l'utilisateur
            excuse_messages = {
                'fr': "⚠️ Désolé, la réponse disponible est en {detected_lang}. Voici ce que j'ai trouvé :\n\n",
                'mo': "⚠️ Gʋlsã, n gom sã n ka {detected_lang} ne. N ka yaa ne :\n\n",
                'di': "⚠️ Hakɛto, jaabi ye {detected_lang} la. Yan ne ye ne y'a sɔrɔ :\n\n"
            }
            
            lang_names = {'fr': 'français', 'mo': 'mooré', 'di': 'dioula'}
            excuse = excuse_messages.get(lang, excuse_messages['fr'])
            excuse = excuse.replace('{detected_lang}', lang_names.get(answer_lang, answer_lang))
            answer = excuse + answer
        
        # Pour les questions, formater la réponse
        formatted = answer
        
        # Ajouter une question de suivi si pertinent
        if add_follow_up and intent == 'question' and len(answer) > 50:
            follow_up = self.suggest_follow_up(category, lang)
            formatted = f"{answer}\n\n💡 {follow_up}"
        
        return formatted
    
    def analyze_and_respond(self, user_message: str, raw_rag_answer: str, category: str = "general") -> Dict[str, any]:
        """
        Analyse complète du message et génération de réponse intelligente
        
        Returns:
            Dict avec:
            - language: langue détectée
            - intent: intention (greeting, question, etc.)
            - response: réponse formatée
            - needs_clarification: bool si besoin de clarification
            - follow_up_suggestion: suggestion de question de suivi
        """
        # 1. Détection de langue
        lang = self.detect_language(user_message)
        
        # 2. Détection d'intention
        intent = self.detect_intent(user_message, lang)
        
        # 3. Vérifier si la question est trop vague
        needs_clarification = self.is_too_vague(user_message)
        
        # 4. Formater la réponse
        if intent == 'greeting':
            response = self.generate_greeting_response(lang)
            add_follow_up = True
        elif intent == 'thanks':
            response = self.generate_thanks_response(lang)
            add_follow_up = False
        elif needs_clarification:
            clarification = {
                'fr': f"Je comprends que vous cherchez des informations, mais pourriez-vous être plus précis ? {self.suggest_follow_up(category, lang)}",
                'mo': f"N gom sã y kẽ kɩtugã, bala y tõe maan yɩɩlã sũuri ? {self.suggest_follow_up(category, lang)}",
                'di': f"Ne y'a faamu i b'a ɲini, nka i bɛ se k'a jira ka tɛmɛ wa ? {self.suggest_follow_up(category, lang)}"
            }
            response = clarification.get(lang, clarification['fr'])
            add_follow_up = False
        else:
            response = self.format_response(raw_rag_answer, lang, intent, category, add_follow_up=True)
            add_follow_up = False  # Déjà ajouté dans format_response
        
        # 5. Retourner l'analyse complète
        return {
            'language': lang,
            'intent': intent,
            'response': response,
            'needs_clarification': needs_clarification,
            'follow_up_suggestion': self.suggest_follow_up(category, lang) if add_follow_up else None
        }
