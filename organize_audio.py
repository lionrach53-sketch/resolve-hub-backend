"""
Script d'organisation des fichiers audio pour TTS Mooré et Dioula

Ce script aide à organiser vos 20h d'enregistrements audio et à créer
les fichiers CSV et audio_index.json nécessaires.

Usage:
    python organize_audio.py --help
"""

import os
import json
import csv
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import hashlib

# Configuration
BASE_DIR = Path(__file__).parent
AUDIO_DIR = BASE_DIR / "audio"
MOREE_DIR = AUDIO_DIR / "moree"
DIOULA_DIR = AUDIO_DIR / "dioula"
INDEX_FILE = AUDIO_DIR / "audio_index.json"

# Catégories disponibles
CATEGORIES = [
    "agriculture",
    "transformation",
    "finance",
    "greetings",
    "common",
    "health",
    "education"
]


def load_audio_index() -> Dict:
    """Charge l'index audio existant"""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"mo": {}, "di": {}}


def save_audio_index(index: Dict):
    """Sauvegarde l'index audio"""
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"✅ Index audio sauvegardé : {INDEX_FILE}")


def add_audio_from_csv(csv_path: Path, language: str):
    """
    Ajoute des audios à partir d'un fichier CSV
    
    Format CSV attendu:
    audio_file,text_moree/dioula,text_french,duration,category,quality
    """
    if not csv_path.exists():
        print(f"❌ Fichier CSV introuvable : {csv_path}")
        return
    
    index = load_audio_index()
    lang_code = "mo" if language == "moree" else "di"
    text_col = "text_moree" if language == "moree" else "text_dioula"
    
    added = 0
    errors = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader, 1):
            try:
                audio_file = row['audio_file']
                text = row[text_col]
                translation = row['text_french']
                duration = float(row['duration'])
                category = row['category']
                
                # Vérifier que le fichier audio existe
                audio_path = BASE_DIR / audio_file
                if not audio_path.exists():
                    print(f"⚠️  Ligne {i}: Fichier audio introuvable : {audio_file}")
                    errors += 1
                    continue
                
                # Extraire le chemin relatif (sans moree/ ou dioula/)
                rel_path = audio_file.replace(f"{language}/", "")
                
                # Ajouter à l'index
                index[lang_code][text] = {
                    "file": rel_path,
                    "category": category,
                    "translation_fr": translation,
                    "duration": duration
                }
                
                added += 1
                
            except Exception as e:
                print(f"❌ Ligne {i}: Erreur : {e}")
                errors += 1
    
    save_audio_index(index)
    print(f"✅ {added} audios ajoutés pour {language}")
    if errors > 0:
        print(f"⚠️  {errors} erreurs rencontrées")


def create_template_csv(language: str, output_path: Path):
    """Crée un fichier CSV template avec exemples"""
    text_col = "text_moree" if language == "moree" else "text_dioula"
    
    template_rows = [
        {
            "audio_file": f"{language}/greetings/bonjour.wav",
            text_col: "Ne y kɔɔrɛ" if language == "moree" else "I ni sɔgɔma",
            "text_french": "Bonjour",
            "duration": "2.0",
            "category": "greetings",
            "quality": "good"
        },
        {
            "audio_file": f"{language}/agriculture/exemple_001.wav",
            text_col: "Exemple de texte agriculture...",
            "text_french": "Exemple de traduction française...",
            "duration": "5.0",
            "category": "agriculture",
            "quality": "excellent"
        },
        {
            "audio_file": f"{language}/finance/exemple_001.wav",
            text_col: "Exemple de texte finance...",
            "text_french": "Exemple de traduction française...",
            "duration": "4.5",
            "category": "finance",
            "quality": "good"
        }
    ]
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ["audio_file", text_col, "text_french", "duration", "category", "quality"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(template_rows)
    
    print(f"✅ Template CSV créé : {output_path}")


def organize_audio_files(source_dir: Path, language: str):
    """
    Organise les fichiers audio d'un dossier source vers la structure correcte
    
    Demande interactivement la catégorie pour chaque fichier
    """
    if not source_dir.exists():
        print(f"❌ Dossier source introuvable : {source_dir}")
        return
    
    dest_dir = MOREE_DIR if language == "moree" else DIOULA_DIR
    
    # Trouver tous les fichiers audio
    audio_extensions = ['.wav', '.mp3', '.m4a', '.flac']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(source_dir.glob(f"**/*{ext}"))
    
    if not audio_files:
        print(f"❌ Aucun fichier audio trouvé dans {source_dir}")
        return
    
    print(f"\n📁 {len(audio_files)} fichiers audio trouvés")
    print(f"📂 Destination : {dest_dir}")
    print("\nCatégories disponibles :")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i}. {cat}")
    print()
    
    organized = 0
    csv_rows = []
    
    for audio_file in audio_files:
        print(f"\n🎵 Fichier : {audio_file.name}")
        
        # Demander la catégorie
        while True:
            cat_input = input(f"Catégorie (1-{len(CATEGORIES)}) ou 's' pour skip : ").strip()
            
            if cat_input.lower() == 's':
                print("⏭️  Fichier ignoré")
                break
            
            try:
                cat_idx = int(cat_input) - 1
                if 0 <= cat_idx < len(CATEGORIES):
                    category = CATEGORIES[cat_idx]
                    
                    # Demander le texte
                    text_col = "Mooré" if language == "moree" else "Dioula"
                    text = input(f"Texte en {text_col} : ").strip()
                    text_fr = input(f"Traduction française : ").strip()
                    
                    if not text or not text_fr:
                        print("❌ Texte obligatoire !")
                        continue
                    
                    # Créer le dossier de destination
                    cat_dir = dest_dir / category
                    cat_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Copier le fichier
                    dest_path = cat_dir / audio_file.name
                    shutil.copy2(audio_file, dest_path)
                    
                    # Ajouter au CSV
                    rel_path = f"{language}/{category}/{audio_file.name}"
                    csv_rows.append({
                        "audio_file": rel_path,
                        f"text_{language}": text,
                        "text_french": text_fr,
                        "duration": "0.0",  # À calculer avec librosa si besoin
                        "category": category,
                        "quality": "good"
                    })
                    
                    organized += 1
                    print(f"✅ Copié vers {category}/")
                    break
                else:
                    print("❌ Numéro invalide !")
            except ValueError:
                print("❌ Entrée invalide !")
    
    # Sauvegarder le CSV
    if csv_rows:
        csv_path = BASE_DIR / f"organized_{language}_{len(csv_rows)}_files.csv"
        text_col = "text_moree" if language == "moree" else "text_dioula"
        
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ["audio_file", text_col, "text_french", "duration", "category", "quality"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        
        print(f"\n✅ CSV créé : {csv_path}")
        print(f"✅ {organized} fichiers organisés")
        
        # Proposer d'ajouter à l'index
        if input("\nAjouter ces fichiers à l'audio_index.json ? (o/n) : ").lower() == 'o':
            add_audio_from_csv(csv_path, language)


def stats_audio_index():
    """Affiche les statistiques de l'index audio"""
    index = load_audio_index()
    
    print("\n📊 STATISTIQUES AUDIO INDEX")
    print("=" * 50)
    
    for lang_code, lang_name in [("mo", "Mooré"), ("di", "Dioula")]:
        audios = index.get(lang_code, {})
        print(f"\n🔤 {lang_name} ({lang_code}) : {len(audios)} audios")
        
        # Grouper par catégorie
        categories = {}
        for text, data in audios.items():
            cat = data.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            print("   Catégories :")
            for cat, count in sorted(categories.items()):
                print(f"     - {cat}: {count}")
    
    print("\n" + "=" * 50)


def create_coqui_metadata(language: str, output_path: Path):
    """
    Crée un fichier metadata.csv au format Coqui TTS
    
    Format: filename|text (pipe-separated)
    """
    index = load_audio_index()
    lang_code = "mo" if language == "moree" else "di"
    
    audios = index.get(lang_code, {})
    if not audios:
        print(f"❌ Aucun audio pour {language}")
        return
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for text, data in audios.items():
            filename = f"{language}/{data['file']}"
            f.write(f"{filename}|{text}\n")
    
    print(f"✅ Metadata Coqui créé : {output_path}")
    print(f"   {len(audios)} entrées pour {language}")


def main():
    parser = argparse.ArgumentParser(description="Organisation des fichiers audio TTS")
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande: template
    template_parser = subparsers.add_parser('template', help='Créer un CSV template')
    template_parser.add_argument('language', choices=['moree', 'dioula'], help='Langue')
    template_parser.add_argument('-o', '--output', help='Chemin de sortie', default=None)
    
    # Commande: organize
    organize_parser = subparsers.add_parser('organize', help='Organiser des fichiers audio')
    organize_parser.add_argument('language', choices=['moree', 'dioula'], help='Langue')
    organize_parser.add_argument('source', type=Path, help='Dossier source avec les audios')
    
    # Commande: add-csv
    add_parser = subparsers.add_parser('add-csv', help='Ajouter audios depuis CSV')
    add_parser.add_argument('language', choices=['moree', 'dioula'], help='Langue')
    add_parser.add_argument('csv_file', type=Path, help='Fichier CSV')
    
    # Commande: stats
    subparsers.add_parser('stats', help='Afficher les statistiques')
    
    # Commande: coqui
    coqui_parser = subparsers.add_parser('coqui', help='Créer metadata Coqui TTS')
    coqui_parser.add_argument('language', choices=['moree', 'dioula'], help='Langue')
    coqui_parser.add_argument('-o', '--output', help='Chemin de sortie', default=None)
    
    args = parser.parse_args()
    
    if args.command == 'template':
        output = Path(args.output) if args.output else BASE_DIR / f"template_{args.language}.csv"
        create_template_csv(args.language, output)
    
    elif args.command == 'organize':
        organize_audio_files(args.source, args.language)
    
    elif args.command == 'add-csv':
        add_audio_from_csv(args.csv_file, args.language)
    
    elif args.command == 'stats':
        stats_audio_index()
    
    elif args.command == 'coqui':
        output = Path(args.output) if args.output else BASE_DIR / f"metadata_{args.language}.csv"
        create_coqui_metadata(args.language, output)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
