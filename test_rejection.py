#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ai.service.rag import RAGService

rag = RAGService()

tests = [
    ("météo", "fr", None),
    ("voiture rouge", "fr", None),
    ("football", "fr", "Plantes Medicinales"),
    ("Neem estomac", "fr", "Plantes Medicinales"),
]

for q, l, c in tests:
    answer, _ = rag.ask(q, language=l, category=c)
    rejected = any(word in answer.lower() for word in ["reformuler", "pas trouvé", "pas sûr"])
    status = "✅ REJETÉ" if rejected else "❌ ACCEPTÉ"
    print(f"{q:30} -> {status}")
