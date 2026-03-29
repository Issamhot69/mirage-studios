"""
Mirage Studios — Emotion Arc
Construction des arcs émotionnels pour le genre Drame.
"""

from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum


class EmotionState(Enum):
    EQUILIBRE = "équilibre"
    TROUBLE = "trouble"
    CRISE = "crise"
    RUPTURE = "rupture"
    DEUIL = "deuil"
    ACCEPTATION = "acceptation"
    TRANSFORMATION = "transformation"
    REDEMPTION = "rédemption"


@dataclass
class EmotionalMoment:
    scene_id: str
    character: str
    state: EmotionState
    trigger: str              # Ce qui provoque l'émotion
    internal_reaction: str    # Ce que le personnage ressent (intérieur)
    external_expression: str  # Ce que le spectateur voit (jeu d'acteur)
    direction_note: str = ""  # Note pour le réalisateur/acteur


@dataclass
class CharacterEmotionArc:
    character_name: str
    arc_type: str             # "redemption", "tragédie", "éveil", "deuil"
    moments: List[EmotionalMoment] = field(default_factory=list)

    def add_moment(self, moment: EmotionalMoment):
        self.moments.append(moment)

    def get_arc_summary(self) -> List[str]:
        return [f"{m.scene_id} → {m.state.value}" for m in self.moments]

    def generate_actor_notes(self) -> str:
        lines = [
            f"NOTES D'ACTEUR — {self.character_name.upper()}",
            f"Type d'arc : {self.arc_type}",
            "=" * 50
        ]
        for m in self.moments:
            lines += [
                f"\n[{m.scene_id}] {m.state.value.upper()}",
                f"Déclencheur : {m.trigger}",
                f"Ressenti intérieur : {m.internal_reaction}",
                f"Expression visible : {m.external_expression}",
            ]
            if m.direction_note:
                lines.append(f"🎬 Régie : {m.direction_note}")
        return "\n".join(lines)


# Exemple : arc de deuil
arc = CharacterEmotionArc("Sophie Marchand", "deuil → acceptation")
arc.add_moment(EmotionalMoment(
    "SC03", "Sophie", EmotionState.EQUILIBRE,
    "Vie quotidienne normale, avant la rupture",
    "Sécurité, amour, routine confortable",
    "Sourires authentiques, mouvements fluides",
    "Jouer la légèreté — contraste maximal avec la suite"
))
arc.add_moment(EmotionalMoment(
    "SC11", "Sophie", EmotionState.RUPTURE,
    "Annonce du décès de sa mère",
    "Choc, dissociation, le sol se dérobe",
    "Visage figé, regard vide, silence long",
    "Pas de larmes immédiates — le choc précède la douleur"
))
arc.add_moment(EmotionalMoment(
    "SC24", "Sophie", EmotionState.CRISE,
    "Retour dans la maison d'enfance vide",
    "Vague de souvenirs, culpabilité, regrets",
    "Tremble légèrement, touche les objets comme des reliques",
    "Micro-expressions — laisser le silence faire le travail"
))
arc.add_moment(EmotionalMoment(
    "SC38", "Sophie", EmotionState.ACCEPTATION,
    "Lettre découverte, paroles de sa mère depuis l'au-delà",
    "Paix progressive, larmes libératrices",
    "Pleure enfin, mais avec un sourire naissant",
    "Le turning point — ne pas sur-jouer"
))

if __name__ == "__main__":
    print(arc.generate_actor_notes())
