#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de debug pour la question générale
"""
import sys
sys.path.insert(0, '.')

from ai.service.rag import RAGService

# Initialiser le service RAG
rag = RAGService()

# Tester la question
question = "Pose-moi une question générale"
category = "general"

print("\nTEST DE DEBUG")
print(f"Question: {question}")
print(f"Catégorie: {category}")
print("\n" + "="*70)

# Appeler le RAG
answer, context = rag.ask(question, k=5, language="fr", category=category)

print("\nRÉPONSE:")
print(answer[:300])

print("\nCONTEXTE COMPLET:")
print(context[:500])
