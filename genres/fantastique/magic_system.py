"""
Mirage Studios — Magic System
Système de magie cohérent pour le genre Fantastique.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class MagicSchool(Enum):
    ELEMENTAL = "élémentaire"   # Feu, eau, terre, air
    TEMPORAL = "temporelle"     # Manipulation du temps
    SHADOW = "ombre"            # Illusion, obscurité
    HEALING = "guérison"        # Restauration
    ARCANE = "arcanique"        # Magie pure, rare


@dataclass
class Spell:
    name: str
    school: MagicSchool
    cost_mana: int
    cast_time_seconds: float
    range_meters: float
    description: str
    visual_effect: str          # Description VFX pour équipe effets


@dataclass
class MagicSystem:
    world_name: str
    magic_source: str           # "étoiles", "sang", "mots anciens", "émotions"
    rules: List[str] = field(default_factory=list)
    spells: List[Spell] = field(default_factory=list)
    forbidden: List[str] = field(default_factory=list)

    def add_rule(self, rule: str):
        self.rules.append(rule)

    def add_spell(self, spell: Spell):
        self.spells.append(spell)

    def get_spells_by_school(self, school: MagicSchool) -> List[Spell]:
        return [s for s in self.spells if s.school == school]

    def to_script_note(self) -> str:
        """Génère une note de production pour l'équipe créative."""
        lines = [f"=== SYSTÈME DE MAGIE — {self.world_name.upper()} ===",
                 f"Source : {self.magic_source}", "",
                 "RÈGLES FONDAMENTALES:"]
        for r in self.rules:
            lines.append(f"  • {r}")
        lines += ["", f"SORTS DISPONIBLES : {len(self.spells)}", "INTERDITS :"]
        for f in self.forbidden:
            lines.append(f"  ✗ {f}")
        return "\n".join(lines)


# Système par défaut pour un projet fantastique épique
DEFAULT_SYSTEM = MagicSystem(
    world_name="Aeloria",
    magic_source="Énergie des étoiles captée par les cristaux de lune"
)
DEFAULT_SYSTEM.add_rule("Toute magie a un coût proportionnel à sa puissance")
DEFAULT_SYSTEM.add_rule("La magie temporelle est instable au-delà de 24 heures")
DEFAULT_SYSTEM.add_rule("Les non-initiés ne peuvent percevoir la magie qu'à travers ses effets")
DEFAULT_SYSTEM.add_spell(Spell(
    "Lumiveil", MagicSchool.ARCANE, 30, 2.0, 50,
    "Crée un bouclier de lumière pure repoussant les ombres",
    "Sphère lumineuse blanche avec particules dorées, lueur pulsante"
))
DEFAULT_SYSTEM.add_spell(Spell(
    "Fracture Temporelle", MagicSchool.TEMPORAL, 80, 5.0, 10,
    "Ralentit le temps dans une zone restreinte pendant 10 secondes",
    "Distorsion visuelle ondulatoire, désaturation de la zone, particules suspendues"
))
DEFAULT_SYSTEM.forbidden.append("Résurrection complète d'un mort (brise l'équilibre)")
DEFAULT_SYSTEM.forbidden.append("Magie de contrôle mental permanent")

if __name__ == "__main__":
    print(DEFAULT_SYSTEM.to_script_note())
