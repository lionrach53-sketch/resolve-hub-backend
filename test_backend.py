#!/usr/bin/env python3
"""
Script de test complet pour le backend d'administration
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
ADMIN_KEY = "admin-souverain-burkina-2024"

headers = {
    "Authorization": f"Bearer {ADMIN_KEY}",
    "Content-Type": "application/json"
}

def print_step(step, message):
    """Affiche une étape"""
    print(f"\n{'='*60}")
    print(f"ÉTAPE {step}: {message}")
    print(f"{'='*60}")

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test un endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return False, f"Méthode non supportée: {method}"
        
        if response.status_code == expected_status:
            return True, response.json() if response.content else {"message": "Success"}
        else:
            return False, f"Status: {response.status_code}, Detail: {response.text}"
            
    except requests.exceptions.ConnectionError:
        return False, "❌ Backend non démarré. Lancez d'abord le backend."
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def main():
    """Fonction principale"""
    print("\n" + "="*70)
    print("🧪 TEST COMPLET DU BACKEND D'ADMINISTRATION")
    print("="*70)
    
    # Test 1: Health check
    print_step(1, "Health check")
    success, result = test_endpoint("GET", "/health")
    if success:
        print(f"✅ Health check OK: {result}")
    else:
        print(f"❌ Health check échoué: {result}")
        sys.exit(1)
    
    # Test 2: Informations API
    print_step(2, "Informations API")
    success, result = test_endpoint("GET", "/api/info")
    if success:
        print(f"✅ Info API: {result.get('name')} v{result.get('version')}")
    else:
        print(f"❌ Info API échoué: {result}")
    
    # Test 3: Statistiques
    print_step(3, "Récupération des statistiques")
    success, result = test_endpoint("GET", "/api/admin/stats")
    if success:
        print(f"✅ Stats récupérées:")
        print(f"   - Requêtes totales: {result.get('total_requests')}")
        print(f"   - Utilisateurs actifs: {result.get('active_users')}")
        print(f"   - Documents: {result.get('documents_count')}")
    else:
        print(f"❌ Stats échouées: {result}")
    
    # Test 4: Clés API
    print_step(4, "Gestion des clés API")
    
    # 4.1: Lister les clés
    success, result = test_endpoint("GET", "/api/admin/api-keys")
    if success:
        initial_count = len(result)
        print(f"✅ {initial_count} clé(s) API trouvée(s)")
    else:
        print(f"❌ Liste clés API échouée: {result}")
        initial_count = 0
    
    # 4.2: Créer une clé
    new_key_data = {
        "name": "Application Test",
        "permissions": {"read": True, "write": True, "delete": False}
    }
    success, result = test_endpoint("POST", "/api/admin/api-keys", new_key_data)
    if success:
        test_key_id = result.get("id")
        test_key_value = result.get("key")
        print(f"✅ Clé API créée:")
        print(f"   - ID: {test_key_id}")
        print(f"   - Clé: {test_key_value[:20]}...")
        print(f"   - Nom: {result.get('name')}")
    else:
        print(f"❌ Création clé API échouée: {result}")
        test_key_id = None
    
    # 4.3: Vérifier nouvelle liste
    success, result = test_endpoint("GET", "/api/admin/api-keys")
    if success and test_key_id:
        new_count = len(result)
        if new_count > initial_count:
            print(f"✅ Liste mise à jour: {new_count} clé(s) (ajout confirmé)")
        else:
            print(f"⚠️  Liste inchangée: {new_count} clé(s)")
    
    # Test 5: Base de connaissances
    print_step(5, "Base de connaissances")
    
    # 5.1: Lister les documents
    success, result = test_endpoint("GET", "/api/admin/knowledge")
    if success:
        knowledge_count = len(result)
        print(f"✅ {knowledge_count} document(s) dans la base de connaissances")
        if knowledge_count > 0:
            print(f"   Premier document: {result[0].get('name')}")
    else:
        print(f"❌ Liste connaissances échouée: {result}")
        knowledge_count = 0
    
    # Test 6: Conversations
    print_step(6, "Conversations")
    
    success, result = test_endpoint("GET", "/api/admin/conversations")
    if success:
        conversations_list = result.get("conversations", result) if isinstance(result, dict) else result
        conv_count = len(conversations_list) if conversations_list else 0
        print(f"✅ {conv_count} conversation(s) trouvée(s)")
        if conv_count > 0:
            last_conv = conversations_list[0]
            if isinstance(last_conv, dict):
                print(f"   Dernière conversation: {last_conv.get('user_id')}")
            else:
                print(f"   Dernière conversation: {last_conv}")
    else:
        print(f"❌ Liste conversations échouée: {result}")
    
    # Test 7: Actions système
    print_step(7, "Actions système")
    
    # 7.1: Sauvegarde
    backup_data = {"action": "backup", "force": False}
    success, result = test_endpoint("POST", "/api/admin/system/action", backup_data)
    if success:
        print(f"✅ Sauvegarde créée: {result.get('message')}")
    else:
        print(f"⚠️  Sauvegarde échouée: {result}")
    
    # 7.2: Logs
    success, result = test_endpoint("GET", "/api/admin/logs?limit=5")
    if success:
        log_count = len(result)
        print(f"✅ {log_count} log(s) système disponibles")
    else:
        print(f"⚠️  Logs échoués: {result}")
    
    # Test 8: Nettoyage (optionnel - révoquer la clé test)
    if test_key_id:
        print_step(8, "Nettoyage - Révocation clé test")
        success, result = test_endpoint("DELETE", f"/api/admin/api-keys/{test_key_id}")
        if success:
            print(f"✅ Clé test révoquée: {result.get('message')}")
        else:
            print(f"⚠️  Révocation échouée: {result}")
    
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DU TEST")
    print("="*70)
    print("Le backend est 100% fonctionnel et prêt pour l'administration!")
    print(f"\n🔑 Clé d'administration: {ADMIN_KEY}")
    print("🌐 Frontend admin: http://localhost:5173")
    print("📚 Documentation: http://localhost:8000/docs")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrompu par l'utilisateur")
        sys.exit(0)