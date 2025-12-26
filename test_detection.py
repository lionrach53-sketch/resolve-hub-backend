import sys
from pathlib import Path

# Assurer que la racine du projet est dans sys.path (chemins avec espaces inclus)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.ai.service.conversation import ConversationService

conv = ConversationService()

# Tester la détection de langue
questions = [
    "Salut",
    "connais tu le burkina faso",
    "Que signifie Burkina Faso ?",
    "Burkina Faso yɩlɩg yaa ?",
    "I ni sɔgɔma"
]

print("🧪 Test de détection de langue:\n")
for q in questions:
    lang = conv.detect_language(q)
    intent = conv.detect_intent(q, lang)
    print(f"Question: '{q}'")
    print(f"  → Langue: {lang}")
    print(f"  → Intent: {intent}")
    print()
