from ai.service.ai_brain import ai_brain

rag_results = [{
    "question": "Quelle plante pour les maux d'estomac ?",
    "reponse": "Les feuilles et écorces de l'arbre 'Neem' (Azadirachta indica), infusées, sont utilisées pour traiter les douleurs gastriques et les ulcères."
}]

res = ai_brain.generate_intelligent_response(
    question="Quelle plante pour les maux d'estomac ?",
    rag_results=rag_results,
    category="Plantes Medicinales",
    language="fr"
)

print({"mode": res.get("mode"), "reponse": res.get("reponse")[:120]})
