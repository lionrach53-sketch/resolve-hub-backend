# ai/service/hybrid_search.py
"""
Recherche hybride: combine recherche par mots-clés et recherche sémantique
pour trouver les meilleurs documents
"""
import logging
from typing import List, Tuple
import re

logger = logging.getLogger(__name__)

class HybridSearch:
    """
    Combine recherche par mots-clés (BM25-like) et recherche sémantique (embeddings)
    pour améliorer la précision
    """
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """Extrait les mots-clés importants d'un texte"""
        # Enlever ponctuation et mettre en minuscules
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Mots vides français à ignorer
        stop_words = {
            'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'mais',
            'pour', 'dans', 'sur', 'avec', 'sans', 'à', 'au', 'aux', 'ce', 'cet',
            'cette', 'ces', 'que', 'qui', 'quoi', 'dont', 'où', 'comment', 'quand',
            'quel', 'quelle', 'quels', 'quelles', 'est', 'sont', 'être', 'avoir',
            'fait', 'faire', 'peut', 'peux', 'tu', 'il', 'elle', 'on', 'nous', 'vous',
            'ils', 'elles', 'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses',
            'je', 'me', 'te', 'se', 'nous', 'vous', 'leur', 'leurs'
        }
        
        # Extraire les mots
        words = text.split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    @staticmethod
    def keyword_score(query_keywords: List[str], document_text: str) -> float:
        """
        Score BM25-like simple basé sur la fréquence des mots-clés
        """
        doc_lower = document_text.lower()
        score = 0.0
        
        for keyword in query_keywords:
            # Compter les occurrences du mot-clé
            count = doc_lower.count(keyword)
            if count > 0:
                # Score augmente avec le nombre d'occurrences, mais avec diminution marginale
                score += 1.0 + (count - 1) * 0.3
        
        return score
    
    @staticmethod
    def rerank_results(
        query: str,
        results: List[dict],
        semantic_scores: List[float],
        keyword_weight: float = 0.4
    ) -> Tuple[List[dict], List[float]]:
        """
        Réordonne les résultats en combinant scores sémantiques et par mots-clés
        
        Args:
            query: Question de l'utilisateur
            results: Liste des documents trouvés
            semantic_scores: Scores de similarité sémantique
            keyword_weight: Poids des mots-clés (0.0 = 100% sémantique, 1.0 = 100% mots-clés)
        
        Returns:
            Tuple[List[dict], List[float]]: Résultats réordonnés et nouveaux scores
        """
        query_keywords = HybridSearch.extract_keywords(query)
        
        logger.info(f"🔑 Mots-clés extraits: {query_keywords}")
        
        # Calculer les scores hybrides
        hybrid_scores = []
        for i, (result, sem_score) in enumerate(zip(results, semantic_scores)):
            doc_text = result.get('text', '')
            
            # Score par mots-clés
            kw_score = HybridSearch.keyword_score(query_keywords, doc_text)
            
            # Normaliser le score de mots-clés (max 5 mots-clés matchés = score 1.0)
            kw_score_norm = min(kw_score / 5.0, 1.0)
            
            # Score hybride (combinaison linéaire)
            hybrid = (1.0 - keyword_weight) * sem_score + keyword_weight * kw_score_norm
            
            hybrid_scores.append(hybrid)
            
            if i < 3:  # Logger les 3 premiers
                logger.info(f"  Doc {i+1}: sem={sem_score:.3f}, kw={kw_score_norm:.3f} → hybrid={hybrid:.3f}")
        
        # Trier par score hybride décroissant
        sorted_indices = sorted(range(len(hybrid_scores)), key=lambda i: hybrid_scores[i], reverse=True)
        
        reranked_results = [results[i] for i in sorted_indices]
        reranked_scores = [hybrid_scores[i] for i in sorted_indices]
        
        return reranked_results, reranked_scores
