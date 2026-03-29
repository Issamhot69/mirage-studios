"""
Mirage Studios — Genre Classifier
Classifie automatiquement un texte dans un genre cinématographique.
"""

from typing import Tuple

GENRE_KEYWORDS = {
    "fantastique": ["magie", "dragon", "sorcier", "royaume", "portail", "artefact"],
    "thriller": ["suspect", "meurtrier", "enquête", "fuite", "complot", "piège"],
    "drame": ["famille", "rupture", "deuil", "rédemption", "sacrifice", "amour"],
    "comedie": ["malentendu", "farce", "ironie", "absurde", "gag", "quiproquo"],
    "historique": ["guerre", "empire", "révolution", "conquête", "époque", "siècle"],
}


class GenreClassifier:
    def __init__(self):
        self.keywords = GENRE_KEYWORDS

    def classify(self, text: str) -> Tuple[str, float]:
        """Retourne le genre et le score de confiance."""
        text_lower = text.lower()
        scores = {}
        for genre, kws in self.keywords.items():
            score = sum(1 for kw in kws if kw in text_lower)
            scores[genre] = score / len(kws)
        best = max(scores, key=scores.get)
        return best, round(scores[best], 2)

    def classify_all(self, text: str) -> dict:
        """Retourne les scores pour tous les genres."""
        text_lower = text.lower()
        return {
            genre: round(sum(1 for kw in kws if kw in text_lower) / len(kws), 2)
            for genre, kws in self.keywords.items()
        }


if __name__ == "__main__":
    clf = GenreClassifier()
    sample = "Un sorcier découvre un artefact magique dans un royaume lointain."
    genre, conf = clf.classify(sample)
    print(f"Genre détecté : {genre} (confiance : {conf})")
