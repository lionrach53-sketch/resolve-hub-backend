# ai/service/query_understanding.py
"""
Module pour comprendre l'intention de la question et suggérer des reformulations
"""
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class QueryUnderstanding:
    """
    Analyse les questions pour comprendre l'intention et suggérer des alternatives
    """
    
    # Dictionnaire de mapping symptômes → catégorie
    SYMPTOM_MAPPING = {
        # Problèmes digestifs
        'gaz': 'estomac',
        'ballonnement': 'estomac',
        'constipation': 'estomac',
        'diarrhée': 'estomac',
        'ventre': 'estomac',
        'intestin': 'estomac',
        'digestion': 'estomac',
        'nausée': 'estomac',
        'vomissement': 'estomac',
        
        # Problèmes respiratoires
        'toux': 'respiratoire',
        'rhume': 'respiratoire',
        'grippe': 'respiratoire',
        'bronche': 'respiratoire',
        
        # Douleurs
        'mal de tête': 'cephalée',
        'migraine': 'cephalée',
        'céphalée': 'cephalée',
        
        # Fièvre/infections
        'fièvre': 'infection',
        'paludisme': 'infection',
        'malaria': 'infection',
    }
    
    @staticmethod
    def understand_health_query(query: str) -> Optional[Dict]:
        """
        Comprend une question de santé et retourne des informations
        
        Returns:
            Dict avec:
            - category: catégorie du problème
            - reformulated_query: question reformulée pour le RAG
            - suggestion: suggestion pour l'utilisateur
        """
        query_lower = query.lower()
        
        # Chercher des symptômes connus
        for symptom, category in QueryUnderstanding.SYMPTOM_MAPPING.items():
            if symptom in query_lower:
                if category == 'estomac':
                    return {
                        'category': 'plantes_medicinales',
                        'reformulated_query': f"plantes médicinales pour traiter les maux d'estomac ventre digestion gastrique {symptom}",
                        'suggestion': "Je cherche des remèdes pour les problèmes digestifs..."
                    }
                elif category == 'respiratoire':
                    return {
                        'category': 'plantes_medicinales',
                        'reformulated_query': f"plantes médicinales pour traiter {symptom} toux rhume respiratoire",
                        'suggestion': f"Je cherche des remèdes pour les problèmes respiratoires..."
                    }
                elif category == 'cephalée':
                    return {
                        'category': 'plantes_medicinales',
                        'reformulated_query': f"plantes médicinales pour traiter mal de tête céphalée migraine",
                        'suggestion': "Je cherche des remèdes pour les maux de tête..."
                    }
                elif category == 'infection':
                    return {
                        'category': 'plantes_medicinales',
                        'reformulated_query': f"plantes médicinales pour traiter fièvre paludisme infection",
                        'suggestion': "Je cherche des remèdes pour les infections et la fièvre..."
                    }
        
        return None
    
    @staticmethod
    def suggest_alternatives(query: str) -> str:
        """
        Suggère des formulations alternatives si la requête est vague
        """
        query_lower = query.lower()
        
        # Cas trop vagues
        if any(word in query_lower for word in ['mal', 'douleur', 'souffre']):
            if len(query.split()) <= 4:  # Question très courte
                return "Pouvez-vous préciser où vous avez mal ? (estomac, tête, gorge, etc.)"
        
        if 'ça fait mal' in query_lower or 'j\'ai mal' in query_lower:
            return "Où avez-vous mal exactement ? Cela m'aidera à trouver le bon remède."
        
        return ""
