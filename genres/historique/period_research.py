"""
Mirage Studios — Period Research
Outil de recherche et validation historique pour les productions d'époque.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class HistoricalPeriod(Enum):
    ANTIQUITE = "Antiquité (-800 à 476)"
    MOYEN_AGE = "Moyen Âge (476-1453)"
    RENAISSANCE = "Renaissance (1453-1600)"
    ABSOLUTISME = "Absolutisme (1600-1789)"
    REVOLUTION = "Révolution & Empire (1789-1815)"
    XIXe = "XIXe siècle (1815-1914)"
    GUERRES = "Guerres mondiales (1914-1945)"
    CONTEMPORAIN = "Contemporain (1945+)"


@dataclass
class HistoricalFact:
    period: HistoricalPeriod
    category: str        # "costume", "architecture", "transport", "alimentation", etc.
    fact: str
    source: str
    accuracy_note: str = ""
    anachronism_risk: bool = False


@dataclass
class PeriodResearch:
    project_title: str
    period: HistoricalPeriod
    region: str
    facts: List[HistoricalFact] = field(default_factory=list)
    anachronisms_flagged: List[str] = field(default_factory=list)

    def add_fact(self, fact: HistoricalFact):
        self.facts.append(fact)
        if fact.anachronism_risk:
            self.anachronisms_flagged.append(fact.fact)

    def get_facts_by_category(self, category: str) -> List[HistoricalFact]:
        return [f for f in self.facts if f.category == category]

    def generate_production_brief(self) -> str:
        """Génère un brief de production pour les départements costumes/décors."""
        lines = [
            f"BRIEF HISTORIQUE — {self.project_title}",
            f"Période : {self.period.value}",
            f"Région : {self.region}",
            "=" * 50,
        ]
        categories = set(f.category for f in self.facts)
        for cat in sorted(categories):
            lines.append(f"\n[{cat.upper()}]")
            for fact in self.get_facts_by_category(cat):
                lines.append(f"  • {fact.fact}")
                if fact.accuracy_note:
                    lines.append(f"    → Note : {fact.accuracy_note}")
        if self.anachronisms_flagged:
            lines += ["", "⚠️  ANACHRONISMES À SURVEILLER :"]
            for a in self.anachronisms_flagged:
                lines.append(f"  ✗ {a}")
        return "\n".join(lines)


# Exemple : France Révolutionnaire
FRANCE_1789 = PeriodResearch("La Dernière Noblesse", HistoricalPeriod.REVOLUTION, "Paris, France")
FRANCE_1789.add_fact(HistoricalFact(
    HistoricalPeriod.REVOLUTION, "costume",
    "Les culottes longues (pantalon) remplacent les culottes courtes comme symbole républicain",
    "Musée Carnavalet, Paris", "Différencie visuellement bourgeois/aristocrates"
))
FRANCE_1789.add_fact(HistoricalFact(
    HistoricalPeriod.REVOLUTION, "transport",
    "Carrosses à quatre chevaux pour la noblesse, charrettes pour le peuple",
    "Archives nationales"
))
FRANCE_1789.add_fact(HistoricalFact(
    HistoricalPeriod.REVOLUTION, "éclairage",
    "Bougies de suif (mauvaise odeur, fumée) pour classes populaires, cire d'abeille pour riches",
    "Encyclopédie Diderot", anachronism_risk=False
))

if __name__ == "__main__":
    print(FRANCE_1789.generate_production_brief())
