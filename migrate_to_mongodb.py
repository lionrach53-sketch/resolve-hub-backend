# migrate_to_mongodb.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mongodb import db

def main():
    print("🚀 Début de la migration des données vers MongoDB...")
    
    try:
        # Chemin vers votre fichier JSON existant
        json_file = "data/expert_db.json"
        
        # Exécuter la migration
        db.migrate_from_json(json_file)
        
        print("\n✅ Migration terminée avec succès !")
        print("\n📊 Vérifiez les données dans MongoDB Compass ou avec ces commandes:")
        print(f"   - Contributions: {db.contributions.count_documents({})}")
        print(f"   - File de validation: {db.validation_queue.count_documents({})}")
        print(f"   - Documents: {db.documents.count_documents({})}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())