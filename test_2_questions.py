#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test des 2 questions problématiques
"""
import requests

BASE_URL = "http://localhost:8000"

def test_question(question: str, category: str):
    """Test une question"""
    print(f"\n📌 {category}")
    print(f"   Q: {question}")
    
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
        print(f"   R: {answer[:200]}...")
    else:
        print(f"   ❌ Erreur {response.status_code}")

if __name__ == "__main__":
    print("\n🧪 TEST DES 2 QUESTIONS PROBLÉMATIQUES\n" + "="*70)
    
    # Question 1: Savon artisanal
    test_question(
        "Comment fabriquer du savon artisanal ?",
        "Science Pratique - Saponification"
    )
    
    # Question 2: Question générale
    test_question(
        "Pose-moi une question générale",
        "general"
    )
    
    print("\n" + "="*70)
    print("✅ Tests terminés!")
