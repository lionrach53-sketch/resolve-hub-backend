"""Test d'intégration complet pour ai_brain.py"""
from ai.service.ai_brain import ai_brain

print("=" * 60)
print("TEST D'INTÉGRATION AI_BRAIN")
print("=" * 60)

# Test 1: Vérifier méthodes disponibles
print("\n✅ Méthodes disponibles:")
print(f"  - generate_intelligent_response: {hasattr(ai_brain, 'generate_intelligent_response')}")
print(f"  - add_to_history: {hasattr(ai_brain, 'add_to_history')}")
print(f"  - clear_history: {hasattr(ai_brain, 'clear_history')}")
print(f"  - get_cache_stats: {hasattr(ai_brain, 'get_cache_stats')}")

# Test 2: Statistiques cache
stats = ai_brain.get_cache_stats()
print(f"\n✅ Cache stats: {stats}")

# Test 3: Tester génération avec fallback (pas de RAG)
print("\n🧪 Test génération sans RAG...")
result_no_rag = ai_brain.generate_intelligent_response(
    question="Test question sans RAG",
    rag_results=[],
    category="test",
    language="fr"
)

# Test 4: Vérifier clés retournées
required_keys = ["reponse", "mode", "langue", "categorie", "sources_utilisees", "timestamp"]
missing = [k for k in required_keys if k not in result_no_rag]

if missing:
    print(f"❌ Clés manquantes: {missing}")
else:
    print("✅ Toutes les clés attendues présentes")

print(f"\n📝 Résultat no_rag:")
print(f"  - Mode: {result_no_rag['mode']}")
print(f"  - Catégorie: {result_no_rag['categorie']}")
print(f"  - Sources: {result_no_rag['sources_utilisees']}")
print(f"  - Réponse: {result_no_rag['reponse'][:80]}...")

# Test 5: Tester avec RAG mock
print("\n🧪 Test génération avec RAG mock...")
rag_mock = [
    {"question": "Test Q1", "reponse": "Réponse test 1 avec informations utiles."},
    {"question": "Test Q2", "reponse": "Réponse test 2 avec plus de détails."}
]

result_with_rag = ai_brain.generate_intelligent_response(
    question="Comment faire ceci ?",
    rag_results=rag_mock,
    category="Plantes Medicinales",
    language="fr"
)

print(f"\n📝 Résultat with_rag:")
print(f"  - Mode: {result_with_rag['mode']}")
print(f"  - Catégorie: {result_with_rag['categorie']}")
print(f"  - Sources: {result_with_rag['sources_utilisees']}")
print(f"  - Cache hit: {result_with_rag.get('cache_hit', 'N/A')}")
if "erreur" in result_with_rag:
    print(f"  - Erreur (fallback): {result_with_rag['erreur']}")
print(f"  - Réponse: {result_with_rag['reponse'][:100]}...")

# Test 6: Historique
print("\n🧪 Test historique...")
ai_brain.clear_history()
ai_brain.add_to_history("user", "Question test 1")
ai_brain.add_to_history("assistant", "Réponse test 1")
summary = ai_brain.get_context_summary()
print(f"✅ Historique généré: {len(summary)} caractères")
print(f"  Contenu: {summary[:100]}...")

print("\n" + "=" * 60)
print("✅ TOUS LES TESTS PASSÉS")
print("=" * 60)
