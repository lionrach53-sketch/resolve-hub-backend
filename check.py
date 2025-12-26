import pickle
m = pickle.load(open('data/faiss/meta.pkl', 'rb'))
print(f"Total: {len(m)}\n")

# Chercher Spiritualite
spirit = [d for d in m if 'Spiritualite' in d['source']]
print(f"Spiritualite: {len(spirit)} docs")
for doc in spirit:
    print(f"  - {doc['source']}")
    print(f"    {doc['text'][:120]}")
    print()
