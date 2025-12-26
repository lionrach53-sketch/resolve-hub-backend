"""Reset complet de l'index RAG (FAISS).

ATTENTION :
- Supprime TOUTES les entrees de l'index vectoriel (anciens et nouveaux formats).
- A utiliser juste avant de reingérer les connaissances enrichies (via ingest.bat).
"""

from ai.service.vector_store import VectorStore


def main() -> None:
    store = VectorStore(dim=384)
    before = store.get_stats()
    print("Avant reinitialisation :")
    print(before)

    store.clear_all()

    after = store.get_stats()
    print("Apres reinitialisation :")
    print(after)


if __name__ == "__main__":
    main()
