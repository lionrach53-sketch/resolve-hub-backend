import pickle

# Charger les métadonnées
meta = pickle.load(open('data/faiss/meta.pkl', 'rb'))

# Extraire les catégories
categories = {}
for doc in meta:
    source = doc['source']
    parts = source.split('-')
    if len(parts) > 2:
        category = parts[2]
        categories[category] = categories.get(category, 0) + 1

print("\n" + "="*50)
print("📋 CATEGORIES DISPONIBLES DANS LE RAG")
print("="*50 + "\n")

for cat, count in sorted(categories.items()):
    print(f"  {cat:<30} {count} docs")

print("\n" + "="*50)
print(f"Total: {len(categories)} catégories, {len(meta)} documents")
print("="*50 + "\n")
