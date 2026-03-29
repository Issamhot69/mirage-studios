"""
Mirage Studios — Tension Builder
Outil de construction dramatique pour le genre Thriller.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class TensionType(Enum):
    SUSPENSE = "suspense"         # On sait, le personnage ne sait pas
    SURPRISE = "surprise"         # Ni le spectateur ni le personnage ne savent
    DRAMATIC_IRONY = "ironie"     # Le spectateur sait plus que le personnage
    PARANOIA = "paranoïa"         # Qui est l'ennemi ?
    COUNTDOWN = "compte_à_rebours"


@dataclass
class TensionBeat:
    scene_id: str
    tension_type: TensionType
    intensity: int           # 1-10
    description: str
    visual_cue: str          # Indication caméra/montage
    sound_cue: str           # Indication sonore
    resolution: Optional[str] = None  # None = tension maintenue


@dataclass
class TensionArc:
    project_name: str
    beats: List[TensionBeat] = field(default_factory=list)

    def add_beat(self, beat: TensionBeat):
        self.beats.append(beat)

    def get_tension_curve(self) -> List[int]:
        """Retourne la courbe de tension (intensités dans l'ordre)."""
        return [b.intensity for b in self.beats]

    def validate_pacing(self) -> List[str]:
        """Vérifie que la tension monte correctement et signale les problèmes."""
        warnings = []
        curve = self.get_tension_curve()
        for i in range(1, len(curve)):
            if curve[i] < curve[i-1] - 3:
                warnings.append(f"Chute brutale scène {i+1} (de {curve[i-1]} à {curve[i]})")
            if i > 2 and all(c == curve[i] for c in curve[i-2:i+1]):
                warnings.append(f"Plateau plat autour de la scène {i+1} — relancer la tension")
        if curve and curve[-1] < 8:
            warnings.append("Le climax final devrait être ≥ 8/10")
        return warnings

    def generate_brief(self) -> str:
        curve = self.get_tension_curve()
        avg = sum(curve) / len(curve) if curve else 0
        lines = [
            f"ARC DE TENSION — {self.project_name}",
            f"Scènes : {len(self.beats)} | Intensité moyenne : {avg:.1f}/10",
            "─" * 50,
        ]
        for b in self.beats:
            bar = "█" * b.intensity + "░" * (10 - b.intensity)
            lines.append(f"[{b.scene_id}] {bar} {b.intensity}/10 — {b.tension_type.value}")
            lines.append(f"   {b.description}")
            lines.append(f"   🎥 {b.visual_cue} | 🎵 {b.sound_cue}")
        warnings = self.validate_pacing()
        if warnings:
            lines += ["", "⚠️  ALERTES DE RYTHME :"]
            for w in warnings:
                lines.append(f"  • {w}")
        return "\n".join(lines)


# Exemple : thriller paranoïaque
arc = TensionArc("Signal Zéro")
arc.add_beat(TensionBeat("SC01", TensionType.SUSPENSE, 3,
    "Elise trouve un message codé dans son appartement",
    "Plan large, mouvement lent vers l'enveloppe",
    "Silence + souffle d'air conditionné"))
arc.add_beat(TensionBeat("SC08", TensionType.PARANOIA, 6,
    "Son collègue semble la surveiller — ou elle imagine ?",
    "POV Elise, zoom lent, contre-plongée sur le collègue",
    "Violons discordants, basse fréquence"))
arc.add_beat(TensionBeat("SC15", TensionType.COUNTDOWN, 8,
    "Elle a 30 minutes pour déchiffrer le code avant minuit",
    "Montage alterné + insert horloge, caméra portée",
    "Battements cardiaques amplifiés, pas de musique"))
arc.add_beat(TensionBeat("SC19", TensionType.DRAMATIC_IRONY, 10,
    "Le spectateur sait que la taupe est dans la pièce",
    "Plan d'ensemble, visages dans l'ombre",
    "Silence total — maximum d'inconfort"))

if __name__ == "__main__":
    print(arc.generate_brief())
