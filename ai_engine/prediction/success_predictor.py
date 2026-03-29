"""
Mirage Studios — Success Predictor
Modèle ML pour prédire le potentiel commercial d'un projet cinématographique.
"""

import json
from dataclasses import dataclass, field
from typing import List


@dataclass
class ProjectFeatures:
    genre: str
    budget_millions: float
    director_score: float        # 0-10 notoriété réalisateur
    cast_score: float            # 0-10 notoriété casting
    has_franchise: bool
    target_demographic: str      # "18-25", "25-40", "family", "all"
    release_season: str          # "summer", "winter", "awards", "spring"
    marketing_budget_ratio: float
    runtime_minutes: int
    sequel_number: int = 0


@dataclass
class PredictionResult:
    project_name: str
    box_office_low: float
    box_office_mid: float
    box_office_high: float
    roi_estimate: float
    streaming_potential: float   # 0-10
    awards_potential: float      # 0-10
    risk_level: str              # "low", "medium", "high"
    key_factors: List[str] = field(default_factory=list)


class SuccessPredictor:
    GENRE_MULTIPLIERS = {
        "fantastique": 1.4, "action": 1.3, "comedie": 1.1,
        "drame": 0.9, "thriller": 1.0, "historique": 0.85,
    }
    SEASON_MULTIPLIERS = {
        "summer": 1.35, "winter": 1.25, "awards": 0.95, "spring": 1.0
    }

    def predict(self, name: str, features: ProjectFeatures) -> PredictionResult:
        base = features.budget_millions * 2.5
        genre_mult = self.GENRE_MULTIPLIERS.get(features.genre, 1.0)
        season_mult = self.SEASON_MULTIPLIERS.get(features.release_season, 1.0)
        talent_mult = 1 + (features.director_score + features.cast_score) / 40
        franchise_bonus = 1.2 if features.has_franchise else 1.0

        mid = base * genre_mult * season_mult * talent_mult * franchise_bonus
        roi = (mid - features.budget_millions) / features.budget_millions * 100

        factors = []
        if features.cast_score > 7: factors.append("Casting premium")
        if features.has_franchise: factors.append("IP établie")
        if features.release_season == "summer": factors.append("Fenêtre estivale favorable")
        if roi < 50: factors.append("⚠️ ROI sous le seuil recommandé")

        return PredictionResult(
            project_name=name,
            box_office_low=round(mid * 0.6, 1),
            box_office_mid=round(mid, 1),
            box_office_high=round(mid * 1.5, 1),
            roi_estimate=round(roi, 1),
            streaming_potential=min(10, round(8 - features.budget_millions / 50, 1)),
            awards_potential=round(features.director_score * 0.8 if features.genre == "drame" else 3.0, 1),
            risk_level="low" if roi > 100 else "medium" if roi > 30 else "high",
            key_factors=factors,
        )


if __name__ == "__main__":
    predictor = SuccessPredictor()
    features = ProjectFeatures(
        genre="fantastique", budget_millions=80.0, director_score=7.5, cast_score=8.0,
        has_franchise=True, target_demographic="18-40", release_season="summer",
        marketing_budget_ratio=0.35, runtime_minutes=128,
    )
    result = predictor.predict("Mirage — L'Éveil", features)
    print(json.dumps(result.__dict__, indent=2, ensure_ascii=False))
