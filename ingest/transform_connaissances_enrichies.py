import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
SRC_FILE = os.path.join(BASE_DIR, "connaissances_backup_20251225_144103.json")
OUT_FILE = os.path.join(BASE_DIR, f"connaissances_enrichies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")


def first_sentence(text: str, max_len: int = 180) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    # Couper à la première phrase si possible
    for sep in [". ", "? ", "! "]:
        if sep in text:
            text = text.split(sep)[0] + sep.strip()
            break
    # Limiter la longueur
    if len(text) > max_len:
        return text[: max_len - 3].rstrip() + "..."
    return text


def guess_intention(question: str) -> str:
    q = (question or "").lower()
    if q.startswith("comment ") or "comment " in q:
        return "utilisation"
    if q.startswith("quelles sont") or "quels sont" in q:
        return "liste"
    if q.startswith("quelle est") or q.startswith("qu'est-ce"):
        return "information"
    if q.endswith("?"):
        return "question_generale"
    return "information_generale"


def guess_question_type(question: str) -> str:
    q = (question or "").lower()
    if "étapes" in q or "etapes" in q or "processus" in q:
        return "procedure"
    if "comment" in q:
        return "utilisation"
    if "pourquoi" in q:
        return "cause"
    if "combien" in q or "capital" in q:
        return "quantite"
    return "autre"


def default_warning_for_category(category: str) -> str:
    c = (category or "").lower()
    if "plantes" in c or "sante" in c or "santé" in c:
        return (
            "En cas de maladie grave, de symptômes persistants ou d'aggravation, "
            "il est important de consulter un agent de santé ou un médecin."
        )
    return ""


def transform_item(item: dict) -> dict:
    """Retourne un nouvel item avec structure enrichie, sans casser les champs existants."""
    category = item.get("categorie", "general")
    langues = item.get("langues", {})

    # On copie l'item pour ne rien perdre
    new_item = dict(item)

    # Champ de niveau par défaut
    if "niveau" not in new_item:
        new_item["niveau"] = "grand_public"

    # On peut garder "sous_categorie" vide ou égal à categorie pour l'instant
    if "sous_categorie" not in new_item:
        new_item["sous_categorie"] = category

    new_langues = {}
    for lang_code, lang_data in langues.items():
        ld = dict(lang_data or {})
        question = (ld.get("question") or "").strip()
        reponse = (ld.get("reponse") or "").strip()

        # Conserver les champs existants tels quels
        # Ajouter les champs enrichis si absents
        if "reponse_detaillee" not in ld:
            ld["reponse_detaillee"] = reponse
        if "reponse_courte" not in ld:
            ld["reponse_courte"] = first_sentence(reponse)

        # Intentions/question_type basés sur la question, si pas déjà fournis
        if "intention" not in ld:
            ld["intention"] = guess_intention(question)
        if "question_type" not in ld:
            ld["question_type"] = guess_question_type(question)

        # Conseil et avertissement : on laisse vide sauf si déjà fourni,
        # mais pour les catégories santé on met au moins un avertissement générique.
        if "avertissement" not in ld or not ld.get("avertissement"):
            warn = default_warning_for_category(category)
            if warn:
                ld["avertissement"] = warn

        if "conseil" not in ld:
            ld["conseil"] = ld.get("conseil", "")

        new_langues[lang_code] = ld

    new_item["langues"] = new_langues
    return new_item


def main() -> None:
    if not os.path.exists(SRC_FILE):
        raise SystemExit(f"Fichier source introuvable: {SRC_FILE}")

    with open(SRC_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise SystemExit("Le JSON source doit être un tableau de connaissances.")

    enriched = [transform_item(item) for item in data]

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print(f"✅ Fichier enrichi généré: {OUT_FILE}")


if __name__ == "__main__":
    main()
