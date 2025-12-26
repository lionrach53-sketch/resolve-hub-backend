#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test des questions hors sujet et du système de confiance
"""
import requests

BASE_URL = "http://localhost:8000"

def test_question(question: str, category: str = None, expected_result: str = "valid"):
    """
    Test une question
    expected_result: 'valid' (doit retourner une réponse) ou 'reject' (doit être rejetée)
    """
    print(f"\n{'='*70}")
    print(f"Q: {question}")
    if category:
        print(f"Catégorie: {category}")
    
    response = requests.post(
        f"{BASE_URL}/api/chat/guest",
        json={
            "message": question,
            "language": "fr",
            "category": category
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        answer = data.get("response", "")
        
        # Vérifier si c'est un message de rejet
        is_rejected = any(word in answer.lower() for word in [
            "reformuler", "pas trouvé", "pas sûr", "comprendre"
        ])
        
        if expected_result == "reject":
            if is_rejected:
                print(f"✅ REJETÉ (attendu): {answer[:150]}")
            else:
                print(f"❌ ACCEPTÉ (devrait rejeter): {answer[:150]}")
        else:
            if is_rejected:
                print(f"❌ REJETÉ (devrait accepter): {answer[:150]}")
            else:
                print(f"✅ ACCEPTÉ: {answer[:150]}")
    else:
        print(f"❌ Erreur {response.status_code}")

if __name__ == "__main__":
    print("\n🧪 TEST DU SYSTÈME DE CONFIANCE")
    print("="*70)
    
    # Tests de questions VALIDES (doivent être acceptées)
    print("\n\n📌 QUESTIONS VALIDES (doivent être acceptées)")
    print("="*70)
    
    test_question(
        "Quelle plante pour les maux d'estomac ?",
        "Plantes Medicinales",
        "valid"
    )
    
    test_question(
        "Comment faire du savon ?",
        "Science Pratique - Saponification",
        "valid"
    )
    
    # Tests de questions HORS SUJET (doivent être rejetées)
    print("\n\n📌 QUESTIONS HORS SUJET (doivent être rejetées)")
    print("="*70)
    
    test_question(
        "Quelle est la météo aujourd'hui ?",
        None,
        "reject"
    )
    
    test_question(
        "Comment aller sur Mars ?",
        None,
        "reject"
    )
    
    test_question(
        "Qui a gagné la coupe du monde ?",
        "Plantes Medicinales",
        "reject"
    )
    
    test_question(
        "salu",
        None,
        "reject"
    )
    
    test_question(
        "blablabla test xyz",
        "general",
        "reject"
    )
    
    print("\n" + "="*70)
    print("✅ Tests terminés!")
