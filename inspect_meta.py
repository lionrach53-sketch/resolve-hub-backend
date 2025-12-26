import pickle

# Charger meta.pkl
meta = pickle.load(open('data/faiss/meta.pkl', 'rb'))

print(f"📊 Total documents: {len(meta)}\n")

# Compter par catégorie
categories = {}
for doc in meta:
    source = doc['source']
    parts = source.split('-')
    if len(parts) > 2:
        cat = parts[2]
        categories[cat] = categories.get(cat, 0) + 1

print("📋 Catégories dans le RAG:")
for cat, count in sorted(categories.items()):
    print(f"  • {cat}: {count} documents")

print("\n📄 Échantillon des 5 premiers:")
for doc in meta[:5]:
    print(f"  - {doc['source']}")
