"""
Mirage Studios — Short Film Maker
Génération de courts métrages (2-5 minutes) depuis un prompt utilisateur.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from prompt_engine import PromptEngine, VideoPrompt, VideoType, VideoStyle, StructuredVideoScript


@dataclass
class ShortFilmConfig:
    title: str
    logline: str              # Résumé en 1 phrase
    genre: str                # fantastique, thriller, drame, comedie, historique
    duration_minutes: int     # 2, 3, 4 ou 5
    language: str = "fr"
    style: VideoStyle = VideoStyle.CINEMATIC
    mood: str = "dramatique"
    director_style: str = "classique"   # "classique", "avant-garde", "documentaire"
    include_subtitles: bool = True
    target_festival: Optional[str] = None  # "Cannes", "Sundance", etc.


@dataclass
class FilmScene:
    scene_number: int
    location: str
    time_of_day: str          # "jour", "nuit", "aube", "crépuscule"
    duration_seconds: int
    characters: List[str]
    action: str
    dialogue_lines: int
    visual_prompt: str
    camera_movement: str      # "fixe", "panoramique", "travelling", "drone"
    lighting: str


@dataclass
class ShortFilmResult:
    config: ShortFilmConfig
    script: StructuredVideoScript
    scenes: List[FilmScene]
    cast: List[dict]
    technical_sheet: dict
    festival_notes: Optional[str] = None


class ShortFilmMaker:
    """Générateur de courts métrages IA."""

    GENRE_VISUAL_STYLES = {
        "fantastique": "epic fantasy cinematography, magical lighting, otherworldly",
        "thriller": "high contrast, shadows, tension, cold color grade",
        "drame": "natural lighting, handheld camera, intimate, warm tones",
        "comedie": "bright, colorful, dynamic cuts, expressive",
        "historique": "desaturated, film grain, period accurate, muted palette",
    }

    CAMERA_MOVEMENTS = {
        "classique": ["fixe", "panoramique", "travelling"],
        "avant-garde": ["drone", "steadicam", "fish-eye", "macro"],
        "documentaire": ["handheld", "fixe", "zoom"],
    }

    def __init__(self):
        self.prompt_engine = PromptEngine()

    def generate(self, config: ShortFilmConfig) -> ShortFilmResult:
        """Génère un court métrage complet."""
        print(f"[ShortFilm] Génération : '{config.title}' ({config.duration_minutes} min, {config.genre})")

        prompt = VideoPrompt(
            raw_text=config.logline,
            language=config.language,
            video_type=VideoType.SHORT_FILM,
            style=config.style,
            duration_seconds=config.duration_minutes * 60,
            mood=config.mood,
        )

        script = self.prompt_engine.process(prompt)
        scenes = self._generate_film_scenes(config)
        cast = self._generate_cast(config)
        tech_sheet = self._technical_sheet(config, scenes)
        festival_notes = self._festival_notes(config) if config.target_festival else None

        return ShortFilmResult(
            config=config,
            script=script,
            scenes=scenes,
            cast=cast,
            technical_sheet=tech_sheet,
            festival_notes=festival_notes,
        )

    def _generate_film_scenes(self, config: ShortFilmConfig) -> List[FilmScene]:
        """Génère les scènes du court métrage."""
        total_seconds = config.duration_minutes * 60
        structure = self._three_act_structure(total_seconds)
        visual_base = self.GENRE_VISUAL_STYLES.get(config.genre, "cinematic, professional")
        movements = self.CAMERA_MOVEMENTS.get(config.director_style, self.CAMERA_MOVEMENTS["classique"])
        scenes = []

        for i, act in enumerate(structure):
            scene = FilmScene(
                scene_number=i + 1,
                location=act["location"],
                time_of_day=act["time"],
                duration_seconds=act["duration"],
                characters=act["characters"],
                action=act["action"],
                dialogue_lines=act["dialogue_lines"],
                visual_prompt=f"{visual_base}, {act['visual_note']}, 4K film quality",
                camera_movement=movements[i % len(movements)],
                lighting=act["lighting"],
            )
            scenes.append(scene)
        return scenes

    def _three_act_structure(self, total_seconds: int) -> List[dict]:
        """Structure en 3 actes : 25% / 50% / 25%."""
        act1 = int(total_seconds * 0.25)
        act2 = int(total_seconds * 0.50)
        act3 = total_seconds - act1 - act2
        return [
            {"location": "Lieu principal", "time": "jour", "duration": act1 // 2,
             "characters": ["Protagoniste"], "action": "Introduction du personnage et du contexte",
             "dialogue_lines": 3, "visual_note": "establishing shot, wide angle",
             "lighting": "natural daylight"},
            {"location": "Lieu principal", "time": "jour", "duration": act1 // 2,
             "characters": ["Protagoniste", "Antagoniste"],
             "action": "Élément perturbateur — le monde change",
             "dialogue_lines": 5, "visual_note": "two shot, medium close-up",
             "lighting": "motivated light, slight shadow"},
            {"location": "Lieu secondaire", "time": "nuit", "duration": act2 // 3,
             "characters": ["Protagoniste"], "action": "Première tentative de résolution — échec",
             "dialogue_lines": 2, "visual_note": "low angle, dramatic shadow",
             "lighting": "low key, high contrast"},
            {"location": "Lieu secondaire", "time": "nuit", "duration": act2 // 3,
             "characters": ["Protagoniste", "Allié"],
             "action": "Rencontre clé — nouveau plan",
             "dialogue_lines": 8, "visual_note": "intimate framing, shallow depth",
             "lighting": "warm practical lights"},
            {"location": "Lieu principal", "time": "aube", "duration": act2 // 3,
             "characters": ["Protagoniste", "Antagoniste"],
             "action": "Confrontation principale — point de non-retour",
             "dialogue_lines": 6, "visual_note": "dynamic cuts, close-ups",
             "lighting": "golden hour, backlight"},
            {"location": "Lieu final", "time": "jour", "duration": act3,
             "characters": ["Protagoniste"], "action": "Résolution — le monde transformé",
             "dialogue_lines": 1, "visual_note": "slow motion, wide shot, silence",
             "lighting": "soft diffused, peaceful"},
        ]

    def _generate_cast(self, config: ShortFilmConfig) -> List[dict]:
        return [
            {"role": "Protagoniste", "age_range": "25-35", "voice_type": "warm",
             "tts_profile": f"Hero_{config.language.upper()}"},
            {"role": "Antagoniste", "age_range": "35-50", "voice_type": "authoritative",
             "tts_profile": f"Villain_{config.language.upper()}"},
            {"role": "Allié", "age_range": "20-30", "voice_type": "friendly",
             "tts_profile": f"Friend_{config.language.upper()}"},
        ]

    def _technical_sheet(self, config: ShortFilmConfig, scenes: List[FilmScene]) -> dict:
        return {
            "format": "16:9 — 1920x1080 — 24fps",
            "color_space": "Rec.709",
            "audio": f"Stéréo 48kHz — {config.language.upper()} + sous-titres",
            "total_scenes": len(scenes),
            "total_duration": f"{config.duration_minutes} min",
            "locations": list({s.location for s in scenes}),
            "vfx_shots": sum(1 for s in scenes if "magical" in s.visual_prompt or "vfx" in s.visual_prompt),
            "dialogue_lines_total": sum(s.dialogue_lines for s in scenes),
            "director_style": config.director_style,
        }

    def _festival_notes(self, config: ShortFilmConfig) -> str:
        notes = {
            "Cannes": "Format DCP requis. Durée max recommandée : 15 min. Sous-titres anglais obligatoires.",
            "Sundance": "Fichier ProRes 4444. Première mondiale exigée. Anglais ou sous-titres EN.",
            "Clermont-Ferrand": "Format numérique accepté. Toutes langues avec sous-titres FR/EN.",
        }
        return notes.get(config.target_festival, f"Vérifier les specs techniques de {config.target_festival}.")


if __name__ == "__main__":
    maker = ShortFilmMaker()
    config = ShortFilmConfig(
        title="Le Dernier Signal",
        logline="Un astronaute reçoit un message de sa fille disparue depuis l'espace lointain.",
        genre="thriller",
        duration_minutes=3,
        language="fr",
        mood="mystérieux",
        director_style="avant-garde",
        target_festival="Cannes",
    )
    result = maker.generate(config)
    print(f"✅ Court métrage : {result.config.title}")
    print(f"🎬 {len(result.scenes)} scènes")
    print(f"👥 Cast : {[c['role'] for c in result.cast]}")
    print(f"🎥 Fiche technique : {result.technical_sheet['format']}")
    if result.festival_notes:
        print(f"🏆 Notes festival : {result.festival_notes}")
