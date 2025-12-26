"""
Module d'amélioration du RAG avec métadonnées riches et re-ranking
"""
import re
from typing import List, Dict, Tuple
from collections import Counter


class RAGEnhancer:
    """Améliore le RAG avec métadonnées riches, mots-clés et re-ranking"""
    
    def __init__(self):
        # Termes locaux burkinabè à préserver
        self.local_terms = {
            'moringa', 'karité', 'karite', 'neem', 'kinkeliba', 'baobab',
            'hibiscus', 'artemisia', 'goyavier', 'papayer', 'tamarin',
            'fcfa', 'mossi', 'senoufo', 'poro', 'tengsoba', 'dioula', 'moore',
            'bouillie', 'to', 'tô', 'bissap', 'soumbala', 'dolo',
            'saponification', 'pfnl', 'beurre', 'savon'
        }
        
        # Synonymes pour enrichissement
        self.synonyms = {
            'fatigue': ['anémie', 'faiblesse', 'épuisement', 'énergie'],
            'ventre': ['estomac', 'gastrique', 'digestif', 'intestin'],
            'fièvre': ['paludisme', 'chaleur', 'température', 'malaria'],
            'toux': ['rhume', 'gorge', 'bronches', 'respiration'],
            'savon': ['saponification', 'détergent', 'lessive', 'soude'],
            'karité': ['beurre', 'noix', 'arbre', 'shea'],
            'fatigue': ['énergie', 'force', 'vitalité'],
            'argent': ['fcfa', 'finance', 'épargne', 'budget'],
            'calcul': ['mathématique', 'compter', 'surface', 'mesure']
        }
        
        # Mots-clés par catégorie
        self.category_keywords = {
            "Plantes Medicinales": ["plante", "feuille", "remède", "santé", "soigner", "maladie", "tisane", "infusion"],
            "Transformation PFNL": ["transformer", "sécher", "conserver", "produire", "noix", "fruit", "poudre", "huile"],
            "Science Pratique - Saponification": ["savon", "soude", "huile", "saponification", "liquide", "solide", "formule"],
            "Metiers Informels": ["métier", "activité", "commerce", "atelier", "capital", "client", "vendre"],
            "Civisme": ["citoyen", "droit", "devoir", "document", "identité", "vote", "impôt"],
            "Spiritualite et Traditions": ["tradition", "cérémonie", "masque", "ancêtre", "spirituel", "rituel"],
            "Developpement Personnel": ["développement", "compétence", "objectif", "gérer", "temps", "apprendre"],
            "Mathematiques Pratiques": ["calculer", "mesure", "surface", "prix", "pourcentage", "division"]
        }
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extrait les mots-clés importants d'un texte"""
        text_lower = text.lower()
        
        # 1. Préserver termes locaux
        keywords = [term for term in self.local_terms if term in text_lower]
        
        # 2. Extraire mots longs (probablement importants)
        words = re.findall(r'\b\w{6,}\b', text_lower)
        
        # 3. Compter fréquence
        word_freq = Counter(words)
        
        # 4. Ajouter mots fréquents
        for word, freq in word_freq.most_common(max_keywords - len(keywords)):
            if word not in keywords and word not in ['comment', 'utiliser', 'faire']:
                keywords.append(word)
        
        return keywords[:max_keywords]
    
    def enrich_query(self, query: str, category: str = None) -> str:
        """Enrichit une requête avec synonymes et contexte"""
        query_lower = query.lower()
        enriched = query
        
        # 1. Ajouter synonymes
        for key, syns in self.synonyms.items():
            if key in query_lower:
                # Ajouter 1-2 synonymes pertinents
                enriched += " " + " ".join(syns[:2])
        
        # 2. Ajouter contexte catégorie si requête assez longue
        if category and len(query.split()) >= 3:
            cat_keywords = self.category_keywords.get(category, [])
            enriched += " " + " ".join(cat_keywords[:3])
        
        return enriched.strip()
    
    def create_rich_metadata(self, qa: Dict) -> Dict:
        """Crée des métadonnées enrichies pour un Q/R"""
        question = qa.get('question', '')
        answer = qa.get('answer', '')
        category = qa.get('category', 'general')
        language = qa.get('language', 'fr')
        
        full_text = f"{question} {answer}"
        
        return {
            "source": f"kb-{category}-{language}",
            "text": full_text,
            "category": category,
            "language": language,
            "question": question,
            "answer": answer,
            "keywords": self.extract_keywords(full_text),
            "char_length": len(answer),
            "word_count": len(answer.split()),
            "priority": qa.get('priority', 'normal'),
            "has_local_terms": any(term in full_text.lower() for term in self.local_terms)
        }
    
    def rerank_results(
        self,
        query: str,
        results: List[Dict],
        distances: List[float],
        category: str = None
    ) -> List[Tuple[Dict, float]]:
        """Re-rank les résultats avec score hybride"""
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_results = []
        
        for result, distance in zip(results, distances):
            # 1. Score vectoriel (similarité cosinus normalisée)
            vector_score = 1.0 / (1.0 + distance)
            
            # 2. Score de correspondance mot-clé
            keywords = result.get('keywords', [])
            if keywords:
                keyword_matches = sum(1 for kw in keywords if kw in query_lower)
                keyword_score = keyword_matches / len(keywords)
            else:
                keyword_score = 0.0
            
            # 3. Score de correspondance mots de la question
            result_words = set(result.get('question', '').lower().split())
            word_overlap = len(query_words & result_words)
            word_score = word_overlap / max(len(query_words), 1)
            
            # 4. Bonus catégorie (forte pondération)
            category_bonus = 0.2 if result.get('category') == category else 0.0
            
            # 5. Bonus termes locaux
            local_bonus = 0.1 if result.get('has_local_terms') else 0.0
            
            # 6. Bonus priorité
            priority_bonus = 0.1 if result.get('priority') == 'high' else 0.0
            
            # Score final pondéré
            final_score = (
                0.45 * vector_score +      # Similarité vectorielle (base)
                0.20 * keyword_score +     # Mots-clés
                0.15 * word_score +        # Mots de la question
                category_bonus +           # Catégorie
                local_bonus +              # Termes burkinabè
                priority_bonus             # Priorité
            )
            
            scored_results.append((result, final_score, {
                'vector': vector_score,
                'keyword': keyword_score,
                'word': word_score,
                'category_bonus': category_bonus
            }))
        
        # Trier par score décroissant
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        return scored_results


# Instance globale
rag_enhancer = RAGEnhancer()
