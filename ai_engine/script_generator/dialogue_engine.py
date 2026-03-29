"""
Mirage Studios — Dialogue Engine
Génère des dialogues dynamiques et cohérents par personnage.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Character:
    name: str
    archetype: str    # "hero", "villain", "mentor", "comic_relief"
    voice_style: str  # "formal", "casual", "poetic", "terse"
    backstory: str = ""


@dataclass
class DialogueLine:
    character: str
    line: str
    emotion: str = "neutral"
    cue: str = ""  # direction de jeu


class DialogueEngine:
    def __init__(self):
        self.characters: List[Character] = []
        self.history: List[DialogueLine] = []

    def add_character(self, character: Character):
        self.characters.append(character)

    def generate_exchange(self, scene_context: str, turns: int = 4) -> List[DialogueLine]:
        """Génère un échange dialogué entre les personnages de la scène."""
        exchange = []
        chars = self.characters[:2] if len(self.characters) >= 2 else self.characters
        for i in range(turns):
            char = chars[i % len(chars)]
            line = DialogueLine(
                character=char.name,
                line=f"[{char.voice_style.upper()}] Réplique {i+1} — contexte : {scene_context[:40]}...",
                emotion="tension" if i % 2 == 0 else "resolve",
                cue="(regard intense)" if char.archetype == "villain" else "",
            )
            exchange.append(line)
            self.history.append(line)
        return exchange

    def export_script_format(self) -> str:
        """Formate les dialogues au standard industrie (FDX-like)."""
        lines = []
        for dl in self.history:
            lines.append(f"\n{dl.character.upper()}")
            if dl.cue:
                lines.append(f"  ({dl.cue})")
            lines.append(f"  {dl.line}")
        return "\n".join(lines)


if __name__ == "__main__":
    engine = DialogueEngine()
    engine.add_character(Character("Aelion", "hero", "poetic", "Fils d'un ancien roi"))
    engine.add_character(Character("Morvar", "villain", "terse", "Seigneur des ombres"))
    exchange = engine.generate_exchange("La tour de cristal, nuit de pleine lune")
    print(engine.export_script_format())
