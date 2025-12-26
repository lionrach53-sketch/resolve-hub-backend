#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inspecter les sources dans meta.pkl
"""
import pickle

# Charger les métadonnées
with open('data/faiss/meta.pkl', 'rb') as f:
    meta = pickle.load(f)

print(f"\n📊 Total: {len(meta)} items dans l'index\n")

# Chercher les items "general"
general_items = [m for m in meta if 'general' in m.get('source', '').lower()]
print(f"✅ {len(general_items)} items avec 'general':")
for item in general_items[:10]:
    source = item.get('source', '')
    text = item.get('text', '')[:80]
    print(f"  - {source}")
    print(f"    Text: {text}...\n")

# Chercher les items "metiers"
metiers_items = [m for m in meta if 'metier' in m.get('source', '').lower()]
print(f"\n📌 {len(metiers_items)} items avec 'metier':")
for item in metiers_items[:5]:
    source = item.get('source', '')
    text = item.get('text', '')[:80]
    print(f"  - {source}")
    print(f"    Text: {text}...\n")
