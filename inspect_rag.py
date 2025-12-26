import pickle
import os

# Charger les métadonnées FAISS
meta_path = os.path.join('data', 'faiss', 'meta.pkl')

if not os.path.exists(meta_path):
    print("❌ Fichier meta.pkl introuvable")
    exit(1)

with open(meta_path, 'rb') as f:
    meta = pickle.load(f)

print(f"✅ Total: {len(meta)} documents\n")

# Analyser par langue
languages = {'fr': 0, 'mo': 0, 'di': 0, 'unknown': 0}
sources = set()

for m in meta:
    source = m.get('source', '')
    sources.add(source)
    
    if '-fr' in source:
        languages['fr'] += 1
    elif '-mo' in source:
        languages['mo'] += 1
    elif '-di' in source:
        languages['di'] += 1
    else:
        languages['unknown'] += 1

print("📊 Distribution par langue:")
print(f"   🇫🇷 Français: {languages['fr']}")
print(f"   🗣️  Mooré: {languages['mo']}")
print(f"   💬 Dioula: {languages['di']}")
print(f"   ❓ Unknown: {languages['unknown']}")
print()

print("📝 Sources uniques trouvées:")
for source in sorted(sources):
    print(f"   - {source}")
print()

print("📄 Premiers 5 documents:")
for i, m in enumerate(meta[:5]):
    source = m.get('source', 'N/A')
    text = m.get('text', '')[:100].replace('\n', ' ')
    print(f"\n{i}. Source: {source}")
    print(f"   Texte: {text}...")
