import pickle
import numpy as np
import faiss
import os

# Charger l'index FAISS et les métadonnées
faiss_dir = os.path.join('data', 'faiss')
index_path = os.path.join(faiss_dir, 'index.faiss')
meta_path = os.path.join(faiss_dir, 'meta.pkl')

# Charger
index = faiss.read_index(index_path)
with open(meta_path, 'rb') as f:
    meta = pickle.load(f)

print(f"📊 Avant nettoyage: {len(meta)} documents")

# Identifier les indices à supprimer (sans -fr, -mo, -di)
indices_to_delete = []
for i, m in enumerate(meta):
    source = m.get('source', '')
    if not any(lang in source for lang in ['-fr', '-mo', '-di']):
        print(f"   ❌ Suppression: {source}")
        indices_to_delete.append(i)

if not indices_to_delete:
    print("✅ Aucun document à supprimer!")
    exit(0)

# Garder uniquement les bons documents
indices_to_keep = [i for i in range(len(meta)) if i not in indices_to_delete]

print(f"\n🔄 Reconstruction de l'index FAISS...")

# Extraire les vecteurs à garder
vectors_to_keep = []
meta_to_keep = []

for i in indices_to_keep:
    # Récupérer le vecteur (reconstruct retourne numpy array directement)
    vector = index.reconstruct(int(i))
    vectors_to_keep.append(vector)
    meta_to_keep.append(meta[i])

# Créer nouvel index
dim = index.d
new_index = faiss.IndexFlatL2(dim)

if vectors_to_keep:
    vectors_array = np.array(vectors_to_keep).astype('float32')
    new_index.add(vectors_array)

# Sauvegarder
faiss.write_index(new_index, index_path)
with open(meta_path, 'wb') as f:
    pickle.dump(meta_to_keep, f)

print(f"\n✅ Nettoyage terminé!")
print(f"   Documents supprimés: {len(indices_to_delete)}")
print(f"   Documents restants: {len(meta_to_keep)}")
print(f"   Répartition:")

# Compter par langue
langs = {'fr': 0, 'mo': 0, 'di': 0}
for m in meta_to_keep:
    source = m.get('source', '')
    if '-fr' in source:
        langs['fr'] += 1
    elif '-mo' in source:
        langs['mo'] += 1
    elif '-di' in source:
        langs['di'] += 1

print(f"      🇫🇷 Français: {langs['fr']}")
print(f"      🗣️  Mooré: {langs['mo']}")
print(f"      💬 Dioula: {langs['di']}")
