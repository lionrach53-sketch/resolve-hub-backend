import unicodedata

def normalize_text(text):
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.lower().replace(' ', '').replace('&', '')

# Test
category = "Spiritualite et Traditions"
source = "admin-json-Spiritualite et Traditions-fr"

cat_norm = normalize_text(category)
source_norm = normalize_text(source)

print(f"Catégorie: '{category}'")
print(f"Catégorie normalisée: '{cat_norm}'")
print(f"\nSource: '{source}'")
print(f"Source normalisée: '{source_norm}'")
print(f"\nMatch: {cat_norm in source_norm}")

# Test autres catégories
tests = [
    ("Developpement Personnel", "admin-json-Developpement Personal-fr"),
    ("Metiers Informels", "admin-json-Metiers Informels-fr"),
    ("Science Pratique - Saponification", "admin-json-Science Pratique - Saponification-fr")
]

print("\n" + "="*60)
for cat, src in tests:
    cat_n = normalize_text(cat)
    src_n = normalize_text(src)
    match = cat_n in src_n
    print(f"\nCatégorie: {cat}")
    print(f"Source: {src}")
    print(f"Match: {match} ({'✅' if match else '❌'})")
