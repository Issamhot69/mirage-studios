"""
Mirage Studios — Joke Generator
Génération de gags, quiproquos et situations comiques pour le cinéma.
"""

import random
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ComedyType(Enum):
    QUIPROQUO = "quiproquo"           # Malentendu sur identité/objet
    RUNNING_GAG = "running_gag"        # Gag répétitif qui monte en puissance
    FISH_OUT_OF_WATER = "dépaysement"  # Personnage hors de son élément
    IRONY = "ironie_dramatique"        # Le spectateur en sait plus
    CALLBACK = "callback"              # Reprise d'un gag antérieur
    SLAPSTICK = "burlesque"            # Comédie physique


@dataclass
class ComedyBeat:
    scene_id: str
    comedy_type: ComedyType
    setup: str        # Mise en place (planting)
    payoff: str       # Résolution (the punchline)
    escalation: Optional[str] = None  # Pour les running gags
    timing_note: str = ""
    callback_ref: Optional[str] = None  # ID de la scène initiale si callback


@dataclass
class ComedyStructure:
    project_name: str
    beats: List[ComedyBeat] = field(default_factory=list)
    running_gags: List[str] = field(default_factory=list)

    def add_beat(self, beat: ComedyBeat):
        self.beats.append(beat)
        if beat.comedy_type == ComedyType.RUNNING_GAG and beat.setup not in self.running_gags:
            self.running_gags.append(beat.setup)

    def get_callbacks(self) -> List[ComedyBeat]:
        return [b for b in self.beats if b.comedy_type == ComedyType.CALLBACK]

    def validate_callbacks(self) -> List[str]:
        """Vérifie que tous les callbacks ont une scène de setup correspondante."""
        scene_ids = {b.scene_id for b in self.beats}
        issues = []
        for b in self.get_callbacks():
            if b.callback_ref and b.callback_ref not in scene_ids:
                issues.append(f"Callback {b.scene_id} → setup introuvable : {b.callback_ref}")
        return issues

    def generate_comedy_map(self) -> str:
        lines = [f"CARTE COMIQUE — {self.project_name}", "=" * 50]
        for b in self.beats:
            emoji = {"quiproquo": "🔀", "running_gag": "🔄", "dépaysement": "🌍",
                     "ironie_dramatique": "😏", "callback": "↩️", "burlesque": "💥"
                     }.get(b.comedy_type.value, "😄")
            lines.append(f"\n{emoji} [{b.scene_id}] {b.comedy_type.value.upper()}")
            lines.append(f"   Setup   : {b.setup}")
            lines.append(f"   Payoff  : {b.payoff}")
            if b.escalation:
                lines.append(f"   ↑ Esca. : {b.escalation}")
            if b.timing_note:
                lines.append(f"   ⏱️  {b.timing_note}")
        if self.running_gags:
            lines += ["", "🔄 RUNNING GAGS actifs :"]
            for rg in self.running_gags:
                lines.append(f"  • {rg}")
        return "\n".join(lines)


# Exemple
comedy = ComedyStructure("Mon Patron est un Robot")
comedy.add_beat(ComedyBeat(
    "SC05", ComedyType.QUIPROQUO,
    "Léo envoie accidentellement son journal intime au DG au lieu de son rapport",
    "Le DG croit que c'est un document RH révolutionnaire sur 'l'authenticité'",
    timing_note="Laisser le silence après la lecture — regard du DG = 3 secondes minimum"
))
comedy.add_beat(ComedyBeat(
    "SC12", ComedyType.RUNNING_GAG,
    "La machine à café refuse systématiquement la carte de Léo",
    "Léo repart bredouille pour la 3ème fois, regard caméra",
    escalation="À la SC25 : la machine lui donne 6 cafés d'un coup",
    timing_note="Rythme rapide, pas de dialogue — jeu muet"
))
comedy.add_beat(ComedyBeat(
    "SC30", ComedyType.CALLBACK,
    "Référence au journal intime de SC05",
    "Le DG cite Léo lors du discours annuel en croyant citer Freud",
    callback_ref="SC05",
    timing_note="La salle applaudit — gros plan Léo qui veut disparaître"
))

if __name__ == "__main__":
    print(comedy.generate_comedy_map())
    issues = comedy.validate_callbacks()
    if issues:
        print("\n⚠️  Problèmes détectés :", issues)
    else:
        print("\n✅ Tous les callbacks sont valides.")
