from sentence_transformers import SentenceTransformer
import numpy as np
import logging

class EmbeddingService:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        logging.basicConfig(level=logging.INFO)
        logging.info(f"Chargement du modèle d'embedding: {model_name}...")
        self.model = SentenceTransformer(model_name)
        logging.info("Modèle chargé avec succès.")

    def embed(self, texts):
        # Si c'est une seule chaîne de caractères, la convertir en liste
        if isinstance(texts, str):
            texts = [texts]
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            # Conversion en float32 pour FAISS
            embeddings = np.array(embeddings).astype('float32')
            return embeddings
        except Exception as e:
            logging.error(f"Erreur lors de l'encodage des textes: {e}")
            return np.array([], dtype='float32')
