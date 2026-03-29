"""
Mirage Studios — Long Métrage Generator
Génère le scénario complet de "نور وظلام" (180 minutes).
"""

from dataclasses import dataclass, field
from typing import List, Optional
from film_config import (FILM_CONFIG, WORLD_OF_LIGHT, WORLD_OF_DARKNESS,
                          HERO_LIGHT, HERO_DARKNESS, THREE_ACT_STRUCTURE)


@dataclass
class Scene:
    number: int
    act: int
    title_ar: str
    title_fr: str
    location: str
    world: str           # "light", "darkness", "border", "both"
    duration_minutes: float
    characters: List[str]
    description: str
    dialogue_lines: int
    vfx_required: bool
    vfx_description: str = ""
    emotion: str = "neutre"
    camera: str = "medium shot"


@dataclass
class FeatureFilmScript:
    config: dict
    acts: List[dict]
    scenes: List[Scene]
    total_scenes: int
    total_vfx_shots: int
    characters: List[dict]
    world_building: dict


class FeatureFilmGenerator:
    """Générateur de long métrage complet."""

    def generate(self) -> FeatureFilmScript:
        print(f"[LongMétrage] Génération : {FILM_CONFIG['title_ar']} — {FILM_CONFIG['duration_minutes']} min")
        scenes = self._generate_all_scenes()
        characters = self._generate_characters()
        vfx_count = sum(1 for s in scenes if s.vfx_required)

        print(f"[LongMétrage] ✅ {len(scenes)} scènes générées")
        print(f"[LongMétrage] 🎬 {vfx_count} shots VFX planifiés")
        print(f"[LongMétrage] 👥 {len(characters)} personnages")

        return FeatureFilmScript(
            config=FILM_CONFIG,
            acts=list(THREE_ACT_STRUCTURE.values()),
            scenes=scenes,
            total_scenes=len(scenes),
            total_vfx_shots=vfx_count,
            characters=characters,
            world_building={"light": WORLD_OF_LIGHT, "darkness": WORLD_OF_DARKNESS},
        )

    def _generate_all_scenes(self) -> List[Scene]:
        scenes = []
        scenes.extend(self._act1_scenes())
        scenes.extend(self._act2_scenes())
        scenes.extend(self._act3_scenes())
        return scenes

    def _act1_scenes(self) -> List[Scene]:
        return [
            Scene(1, 1, "فجر الحرب الأولى", "L'Aube de la Première Guerre",
                  "Ciel entre les deux mondes", "border", 4,
                  ["Narrateur"], "Flashback épique — la guerre ancestrale il y a 1000 ans",
                  0, True, "Bataille massive CGI, deux armées de lumière et d'ombre", "épique", "drone"),
            Scene(2, 1, "مدينة الفجر", "La Cité de l'Aube",
                  WORLD_OF_LIGHT["capital"], "light", 3,
                  [HERO_LIGHT["name_fr"]], "Diyaa s'entraîne — maîtrise de la lumière",
                  2, True, "Boules de lumière, magie dorée", "confiant", "steadicam"),
            Scene(3, 1, "قلعة الغسق", "La Forteresse du Crépuscule",
                  WORLD_OF_DARKNESS["capital"], "darkness", 3,
                  [HERO_DARKNESS["name_fr"]], "Zhalal observe son monde depuis les hauteurs",
                  3, True, "Cristaux noirs, flammes violettes, ombres animées", "mélancolique", "fixe"),
            Scene(4, 1, "مجلس الحرب", "Le Conseil de Guerre",
                  "Salle du trône — Monde de Lumière", "light", 4,
                  [HERO_LIGHT["name_fr"], "Roi de Lumière", "Conseil"],
                  "Le roi annonce la guerre — Diyaa doute",
                  12, False, "", "tension", "medium shot"),
            Scene(5, 1, "سرقة القطعة الأثرية", "Le Vol de l'Artefact",
                  "Temple sacré — frontière des mondes", "border", 5,
                  ["Voleur masqué"], "L'artefact de paix est dérobé — identité inconnue",
                  0, True, "Portail magique, explosion de lumière et d'ombre", "mystère", "close-up"),
            Scene(6, 1, "المهمة المستحيلة", "La Mission Impossible",
                  "Deux trônes — montage parallèle", "both", 4,
                  [HERO_LIGHT["name_fr"], HERO_DARKNESS["name_fr"]],
                  "Les deux héros reçoivent la même mission séparément",
                  8, False, "", "détermination", "split screen"),
        ]

    def _act2_scenes(self) -> List[Scene]:
        return [
            Scene(7, 2, "المواجهة الأولى", "La Première Confrontation",
                  "Zone frontière — Forêt de cristaux", "border", 5,
                  [HERO_LIGHT["name_fr"], HERO_DARKNESS["name_fr"]],
                  "Diyaa et Zhalal se rencontrent — combat immédiat",
                  6, True, "Lumière vs ombres — duel magique spectaculaire", "combat", "travelling"),
            Scene(8, 2, "هدنة مؤقتة", "Trêve Temporaire",
                  "Grotte entre les deux mondes", "border", 4,
                  [HERO_LIGHT["name_fr"], HERO_DARKNESS["name_fr"]],
                  "Blessés, ils sont forcés de s'abriter ensemble",
                  15, False, "", "méfiance", "close-up"),
            Scene(9, 2, "أسرار الظلام", "Les Secrets des Ténèbres",
                  WORLD_OF_DARKNESS["capital"], "darkness", 6,
                  [HERO_LIGHT["name_fr"], HERO_DARKNESS["name_fr"], "Habitants"],
                  "Diyaa visite le Monde des Ténèbres — ses préjugés s'effondrent",
                  10, True, "Architecture obsidienne, beauté sombre inattendue", "émerveillement", "drone"),
            Scene(10, 2, "جمال النور", "La Beauté de la Lumière",
                  WORLD_OF_LIGHT["capital"], "light", 6,
                  [HERO_LIGHT["name_fr"], HERO_DARKNESS["name_fr"]],
                  "Zhalal découvre le Monde de Lumière — bouleversée",
                  10, True, "Jardins dorés, cascades de lumière", "émerveillement", "steadicam"),
            Scene(11, 2, "الحقيقة المخفية", "La Vérité Cachée",
                  "Archives secrètes — Monde de Lumière", "light", 5,
                  [HERO_LIGHT["name_fr"], HERO_DARKNESS["name_fr"]],
                  "Découverte : le vrai voleur est un conseiller du Monde de Lumière",
                  14, False, "", "choc", "close-up"),
            Scene(12, 2, "الخيانة", "La Trahison",
                  "Frontière des mondes", "border", 7,
                  [HERO_LIGHT["name_fr"], HERO_DARKNESS["name_fr"], "Armées"],
                  "Le conseiller révèle les héros — les deux armées les encerclent",
                  8, True, "Deux armées face à face, magie explosive", "désespoir", "drone"),
        ]

    def _act3_scenes(self) -> List[Scene]:
        return [
            Scene(13, 3, "المعركة الأخيرة", "La Bataille Finale",
                  "Champ entre les deux mondes", "both", 12,
                  [HERO_LIGHT["name_fr"], HERO_DARKNESS["name_fr"], "Toutes armées"],
                  "Bataille épique — les deux héros s'interposent",
                  6, True, "Bataille massive CGI — 500+ soldats des deux mondes", "épique", "drone"),
            Scene(14, 3, "التضحية", "Le Sacrifice",
                  "Centre du champ de bataille", "both", 8,
                  [HERO_LIGHT["name_fr"], HERO_DARKNESS["name_fr"]],
                  "Les deux héros fusionnent leur magie — sacrifice",
                  10, True, "Explosion de lumière et d'ombre — nova magique", "émotion maximale", "slow motion"),
            Scene(15, 3, "الفجر الجديد", "L'Aube Nouvelle",
                  "Les deux mondes réunis", "both", 5,
                  ["Tous les personnages"],
                  "Les deux mondes commencent à fusionner — paix",
                  4, True, "Transformation paysage — lumière et ombre en harmonie", "espoir", "drone"),
            Scene(16, 3, "خاتمة", "Épilogue",
                  "Nouvelle cité unifiée — 1 an après", "both", 4,
                  [HERO_LIGHT["name_fr"], HERO_DARKNESS["name_fr"]],
                  "Diyaa et Zhalal construisent ensemble le nouveau monde",
                  6, False, "", "sérénité", "wide shot"),
        ]

    def _generate_characters(self) -> List[dict]:
        return [
            {**HERO_LIGHT, "type": "protagonist", "importance": "principal"},
            {**HERO_DARKNESS, "type": "protagonist", "importance": "principal"},
            {"name_ar": "ملك النور", "name_fr": "Roi de Lumière", "age": 55,
             "world": "Monde de Lumière", "role": "Père de Diyaa — belliciste",
             "arc": "Apprend l'humilité", "type": "antagonist_redeemed", "importance": "secondaire"},
            {"name_ar": "ملك الظلام", "name_fr": "Roi des Ténèbres", "age": 60,
             "world": "Monde des Ténèbres", "role": "Père de Zhalal — protecteur",
             "arc": "Accepte la paix", "type": "antagonist_redeemed", "importance": "secondaire"},
            {"name_ar": "المستشار الخائن", "name_fr": "Le Conseiller Traître", "age": 45,
             "world": "Monde de Lumière", "role": "Vrai antagoniste — veut la guerre pour le pouvoir",
             "arc": "Démasqué et vaincu", "type": "villain", "importance": "principal"},
            {"name_ar": "الحكيمة", "name_fr": "La Sage", "age": 200,
             "world": "Frontière", "role": "Guide des deux héros",
             "arc": "Révèle la vérité sur les origines", "type": "mentor", "importance": "secondaire"},
        ]

    def print_synopsis(self):
        """Affiche le synopsis complet."""
        print(f"""
{'='*60}
{FILM_CONFIG['title_ar']} — {FILM_CONFIG['title_fr']}
{'='*60}

SYNOPSIS :
Dans un univers divisé entre le radieux Monde de Lumière
et le mystérieux Monde des Ténèbres, deux héros — Diyaa
et Zhalal — sont envoyés en mission par leurs royaumes
ennemis pour retrouver un artefact de paix volé.

Ennemis d'abord, ils découvrent que le véritable danger
vient de l'intérieur... et que les deux mondes partagent
une origine commune.

Un film sur les préjugés, la paix et le courage de voir
la beauté dans ce qui nous est étranger.

DURÉE    : {FILM_CONFIG['duration_minutes']} minutes
GENRE    : {FILM_CONFIG['genre']}
LANGUE   : Arabe + 8 doublages
PUBLIC   : {FILM_CONFIG['target_audience']}
{'='*60}
        """)


if __name__ == "__main__":
    generator = FeatureFilmGenerator()
    generator.print_synopsis()
    script = generator.generate()
    print(f"\n📊 STATISTIQUES :")
    print(f"  Scènes totales    : {script.total_scenes}")
    print(f"  Shots VFX         : {script.total_vfx_shots}")
    print(f"  Personnages       : {len(script.characters)}")
    print(f"  Durée totale      : {FILM_CONFIG['duration_minutes']} min")
    print(f"  Langues           : {len(FILM_CONFIG['languages_dubbing'])+1}")
