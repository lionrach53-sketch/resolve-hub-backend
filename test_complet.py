#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test complet : questions valides + hors sujet
"""
import requests

BASE_URL = "http://localhost:8000"

print("\n" + "="*70)
print("TEST COMPLET - QUESTIONS VALIDES")
print("="*70)

# Questions valides
valid_tests = [
    ("Neem pour estomac", "Plantes Medicinales", True),
    ("Comment faire du savon", "Science Pratique - Saponification", True),
    ("Que peux-tu m'apprendre", "general", True),
]

for question, category, should_work in valid_tests:
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/guest",
            json={"message": question, "language": "fr", "category": category}
        )
        
        if response.status_code == 200:
            answer = response.json().get("response", "")
            is_rejected = any(word in answer.lower() for word in ["reformuler", "pas trouvé", "pas sûr"])
            
            if should_work:
                status = "✅ OK" if not is_rejected else "❌ REJETÉ (devrait accepter)"
            else:
                status = "✅ OK" if is_rejected else "❌ ACCEPTÉ (devrait rejeter)"
            
            print(f"\n{status}")
            print(f"  Q: {question}")
            print(f"  Cat: {category}")
            print(f"  R: {answer[:80]}...")
        else:
            print(f"\n❌ Erreur {response.status_code}: {question}")
    except Exception as e:
        print(f"\n❌ Exception: {question} - {e}")

print("\n" + "="*70)
print("TEST SALUTATIONS (doivent être gérées AVANT le RAG)")
print("="*70)

# Salutations
greetings = ["Bonjour", "Salut", "Bonsoir", "Merci", "Merci beaucoup"]

for greeting in greetings:
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/guest",
            json={"message": greeting, "language": "fr"}
        )
        
        if response.status_code == 200:
            answer = response.json().get("response", "")
            intent = response.json().get("intent", "")
            
            # Salutations doivent être courtes et ne pas appeler le RAG
            is_short = len(answer) < 100
            is_greeting_intent = intent in ["greeting", "thanks"]
            
            if is_short and is_greeting_intent:
                print(f"✅ {greeting:20} -> {answer[:60]}")
            else:
                print(f"❌ {greeting:20} -> Trop long ou mauvais intent ({intent})")
        else:
            print(f"❌ {greeting:20} -> Erreur {response.status_code}")
    except Exception as e:
        print(f"❌ {greeting:20} -> Exception: {e}")

print("\n" + "="*70)
print("✓ Tests terminés")
print("="*70)
