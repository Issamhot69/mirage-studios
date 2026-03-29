"""
Mirage Studios — نور وظلام (Lumière et Ténèbres)
Configuration complète du long métrage fantastique épique.
"""

from dataclasses import dataclass, field
from typing import List

# ── CONFIGURATION DU FILM ─────────────────────────────────

FILM_CONFIG = {
    "title_ar": "نور وظلام",
    "title_fr": "Lumière et Ténèbres",
    "title_en": "Light and Darkness",
    "genre": "Fantastique Épique",
    "duration_minutes": 180,
    "language_primary": "ar",
    "languages_dubbing": ["fr", "en", "es", "de", "ja", "zh", "pt", "it"],
    "target_audience": "Tout public",
    "tone": "Émotionnel et profond",
    "rating": "PG-13",
    "production_year": 2025,
}

# ── LES DEUX MONDES ───────────────────────────────────────

WORLD_OF_LIGHT = {
    "name_ar": "عالم النور",
    "name_fr": "Monde de Lumière",
    "description": "Un royaume céleste baigné de lumière dorée, flottant au-dessus des nuages. Les habitants vivent en harmonie avec la magie lumineuse.",
    "colors": ["#FFD700", "#FFF8DC", "#87CEEB", "#FFFACD"],
    "magic_type": "Lumière, guérison, prophétie",
    "architecture": "Cristal blanc, tours dorées, jardins suspendus",
    "music_theme": "Orchestral lumineux, harpes, chœurs célestes",
    "population": "Les Nouriens — êtres de lumière pure",
    "weakness": "L'obscurité totale les affaiblit",
    "capital": "مدينة الفجر — Cité de l'Aube",
}

WORLD_OF_DARKNESS = {
    "name_ar": "عالم الظلام",
    "name_fr": "Monde des Ténèbres",
    "description": "Un royaume souterrain mystérieux, éclairé par des cristaux noirs et des flammes violettes. Pas maléfique — incompris.",
    "colors": ["#1a0a2e", "#4B0082", "#8B008B", "#2d0a4e"],
    "magic_type": "Ombres, illusion, transformation",
    "architecture": "Obsidienne noire, arches sculptées, forêts de cristaux",
    "music_theme": "Cordes graves, percussions profondes, voix mystérieuses",
    "population": "Les Zoulamiens — maîtres des ombres",
    "weakness": "La lumière directe les blesse",
    "capital": "قلعة الغسق — Forteresse du Crépuscule",
}

# ── LES DEUX HÉROS ────────────────────────────────────────

HERO_LIGHT = {
    "name_ar": "ضياء",
    "name_fr": "Diyaa",
    "age": 19,
    "world": "Monde de Lumière",
    "role": "Prince héritier qui doute de la guerre",
    "power": "Contrôle de la lumière — peut aveugler ou guérir",
    "flaw": "Trop confiant, ne connaît qu'un seul point de vue",
    "arc": "Découvre que les Ténèbres ne sont pas l'ennemi",
    "voice_type": "Jeune, noble, émotionnel",
    "appearance": "Cheveux dorés, yeux bleus lumineux, armure blanche",
    "motivation": "Protéger son peuple — mais à quel prix ?",
}

HERO_DARKNESS = {
    "name_ar": "ظلال",
    "name_fr": "Zhalal",
    "age": 18,
    "world": "Monde des Ténèbres",
    "role": "Fille du roi des ombres, rebelle",
    "power": "Manipulation des ombres — invisibilité, illusions",
    "flaw": "Méfiance totale envers la lumière",
    "arc": "Apprend que la paix est possible",
    "voice_type": "Forte, mystérieuse, vulnérable sous la surface",
    "appearance": "Cheveux noirs, yeux violets, cape d'ombre",
    "motivation": "Prouver que son monde mérite d'exister",
}

# ── STRUCTURE 3 ACTES (180 min) ───────────────────────────

THREE_ACT_STRUCTURE = {
    "act1": {
        "title_ar": "الفصل الأول: الحرب تبدأ",
        "title_fr": "Acte I : La Guerre Commence",
        "duration_minutes": 45,
        "scenes_count": 30,
        "key_moments": [
            "Ouverture épique — bataille ancestrale (flashback)",
            "Introduction Diyaa dans le Monde de Lumière",
            "Introduction Zhalal dans le Monde des Ténèbres",
            "Incident déclencheur — l'artefact de paix est volé",
            "Les deux héros reçoivent la même mission : retrouver l'artefact",
        ]
    },
    "act2": {
        "title_ar": "الفصل الثاني: اللقاء المستحيل",
        "title_fr": "Acte II : La Rencontre Impossible",
        "duration_minutes": 90,
        "scenes_count": 60,
        "key_moments": [
            "Diyaa et Zhalal se rencontrent — ennemis d'abord",
            "Forcés de coopérer pour retrouver l'artefact",
            "Découverte : le vrai ennemi est dans l'un des deux mondes",
            "Développement du lien émotionnel entre les héros",
            "Trahison — tout s'effondre au point de non-retour",
        ]
    },
    "act3": {
        "title_ar": "الفصل الثالث: من أجل السلام",
        "title_fr": "Acte III : Pour la Paix",
        "duration_minutes": 45,
        "scenes_count": 30,
        "key_moments": [
            "Climax — bataille finale entre les deux armées",
            "Diyaa et Zhalal s'interposent ensemble",
            "Révélation : les deux mondes viennent de la même source",
            "Sacrifice et réconciliation",
            "Épilogue — l'aube d'un nouveau monde unifié",
        ]
    }
}

# ── PRÉDICTION COMMERCIALE ────────────────────────────────

COMMERCIAL_PREDICTION = {
    "budget_millions": 120,
    "target_markets": ["Moyen-Orient", "France", "Monde arabe", "International"],
    "box_office_estimate_millions": 480,
    "roi_estimate_percent": 300,
    "streaming_platforms": ["Netflix MENA", "Shahid", "Prime Video", "Disney+"],
    "awards_potential": ["Festival de Cannes", "Oscar Film Étranger", "Arab Film Festival"],
}
