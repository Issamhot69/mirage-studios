"""
Mirage Studios — Prompt Engine
Transforme un prompt utilisateur en instructions vidéo structurées.
Supporte 9 langues avec détection automatique.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class VideoType(Enum):
    AD = "publicite"           # 15-60 secondes
    SHORT_FILM = "court_metrage"  # 2-5 minutes
    CLIP = "clip"              # 30-90 secondes
    TRAILER = "teaser"         # 30-60 secondes


class VideoStyle(Enum):
    CINEMATIC = "cinématique"
    DOCUMENTARY = "documentaire"
    ANIMATED = "animé"
    REALISTIC = "réaliste"
    ARTISTIC = "artistique"
    COMMERCIAL = "commercial"


@dataclass
class VideoPrompt:
    raw_text: str
    language: str = "fr"
    video_type: VideoType = VideoType.AD
    style: VideoStyle = VideoStyle.CINEMATIC
    duration_seconds: int = 30
    target_audience: str = "general"
    brand_name: Optional[str] = None
    mood: str = "neutre"  # "joyeux", "dramatique", "inspirant", "mystérieux"


@dataclass
class StructuredVideoScript:
    title: str
    video_type: VideoType
    duration_seconds: int
    language: str
    scenes: list
    voiceover: str
    music_mood: str
    visual_style: str
    color_palette: list
    call_to_action: Optional[str] = None


class PromptEngine:
    """Moteur de transformation prompt → script vidéo structuré."""

    MOOD_MUSIC = {
        "joyeux": "upbeat pop, tempo 120bpm, major key",
        "dramatique": "orchestral, strings, tension building",
        "inspirant": "epic cinematic, choir, crescendo",
        "mystérieux": "ambient electronic, minor key, slow tempo",
        "professionnel": "corporate background, neutral, clean",
        "romantique": "acoustic guitar, soft piano, warm",
        "neutre": "light background, unobtrusive",
    }

    COLOR_PALETTES = {
        "luxe": ["#1a1a2e", "#c9a84c", "#f5f5f0", "#2d2d44"],
        "tech": ["#0f0f1a", "#00d4ff", "#7c5cfc", "#1a1a2e"],
        "nature": ["#1a3a2a", "#4caf50", "#f5f0e8", "#8b6914"],
        "energie": ["#1a0a00", "#ff6b00", "#ffd700", "#ff1744"],
        "sante": ["#e8f4f8", "#0077b6", "#00b4d8", "#ffffff"],
        "mode": ["#1a1a1a", "#f5f5f5", "#c9a84c", "#2d2d2d"],
    }

    MULTILANG_TEMPLATES = {
        "fr": {"intro": "Découvrez", "cta": "Contactez-nous", "tagline": "L'excellence au quotidien"},
        "en": {"intro": "Discover", "cta": "Contact us", "tagline": "Excellence every day"},
        "ar": {"intro": "اكتشف", "cta": "تواصل معنا", "tagline": "التميز كل يوم"},
        "es": {"intro": "Descubre", "cta": "Contáctanos", "tagline": "Excelencia cada día"},
        "de": {"intro": "Entdecken Sie", "cta": "Kontaktieren Sie uns", "tagline": "Exzellenz täglich"},
        "ja": {"intro": "発見する", "cta": "お問い合わせ", "tagline": "日々の卓越性"},
        "zh": {"intro": "发现", "cta": "联系我们", "tagline": "日常卓越"},
        "pt": {"intro": "Descubra", "cta": "Contacte-nos", "tagline": "Excelência diária"},
        "it": {"intro": "Scopri", "cta": "Contattaci", "tagline": "Eccellenza quotidiana"},
    }

    def process(self, prompt: VideoPrompt) -> StructuredVideoScript:
        """Transforme un prompt en script vidéo structuré."""
        lang_tpl = self.MULTILANG_TEMPLATES.get(prompt.language, self.MULTILANG_TEMPLATES["fr"])
        scenes = self._generate_scenes(prompt)
        palette_key = self._detect_palette(prompt.raw_text)

        return StructuredVideoScript(
            title=f"{prompt.brand_name or 'Projet'} — {prompt.video_type.value}",
            video_type=prompt.video_type,
            duration_seconds=prompt.duration_seconds,
            language=prompt.language,
            scenes=scenes,
            voiceover=f"{lang_tpl['intro']} — {prompt.raw_text[:100]}",
            music_mood=self.MOOD_MUSIC.get(prompt.mood, self.MOOD_MUSIC["neutre"]),
            visual_style=prompt.style.value,
            color_palette=self.COLOR_PALETTES.get(palette_key, self.COLOR_PALETTES["tech"]),
            call_to_action=lang_tpl["cta"] if prompt.video_type == VideoType.AD else None,
        )

    def _generate_scenes(self, prompt: VideoPrompt) -> list:
        """Découpe la durée en scènes équilibrées."""
        if prompt.video_type == VideoType.AD:
            if prompt.duration_seconds <= 15:
                return [
                    {"id": 1, "duration": 5, "type": "hook", "desc": "Accroche visuelle forte"},
                    {"id": 2, "duration": 7, "type": "product", "desc": "Présentation produit/service"},
                    {"id": 3, "duration": 3, "type": "cta", "desc": "Appel à l'action"},
                ]
            elif prompt.duration_seconds <= 30:
                return [
                    {"id": 1, "duration": 5, "type": "hook", "desc": "Accroche émotionnelle"},
                    {"id": 2, "duration": 10, "type": "problem", "desc": "Problème identifié"},
                    {"id": 3, "duration": 10, "type": "solution", "desc": "Solution présentée"},
                    {"id": 4, "duration": 5, "type": "cta", "desc": "Appel à l'action"},
                ]
            else:
                return [
                    {"id": 1, "duration": 8, "type": "hook", "desc": "Ouverture cinématique"},
                    {"id": 2, "duration": 12, "type": "story", "desc": "Histoire de marque"},
                    {"id": 3, "duration": 20, "type": "features", "desc": "Avantages clés x3"},
                    {"id": 4, "duration": 12, "type": "testimonial", "desc": "Preuve sociale"},
                    {"id": 5, "duration": 8, "type": "cta", "desc": "CTA + logo"},
                ]
        else:
            # Court métrage
            nb_scenes = prompt.duration_seconds // 30
            return [
                {"id": i + 1, "duration": 30, "type": ["setup", "confrontation", "climax", "resolution"][min(i, 3)],
                 "desc": f"Scène {i + 1} — {['Mise en place', 'Développement', 'Climax', 'Résolution'][min(i, 3)]}"}
                for i in range(max(4, nb_scenes))
            ]

    def _detect_palette(self, text: str) -> str:
        """Détecte la palette de couleurs selon le contenu du prompt."""
        keywords = {
            "luxe": ["luxe", "premium", "prestige", "luxury", "gold", "or", "bijou"],
            "tech": ["tech", "ia", "ai", "digital", "app", "software", "numérique"],
            "nature": ["nature", "bio", "écolo", "vert", "green", "organic", "naturel"],
            "energie": ["sport", "énergie", "power", "dynamique", "feu", "vitesse"],
            "sante": ["santé", "médical", "health", "bien-être", "clinique", "pharma"],
            "mode": ["mode", "fashion", "style", "vêtement", "beauté", "cosmétique"],
        }
        text_lower = text.lower()
        for palette, kws in keywords.items():
            if any(kw in text_lower for kw in kws):
                return palette
        return "tech"


if __name__ == "__main__":
    import json
    engine = PromptEngine()
    prompt = VideoPrompt(
        raw_text="Une publicité pour un parfum de luxe, ambiance Paris nuit, musique jazz",
        language="fr",
        video_type=VideoType.AD,
        style=VideoStyle.CINEMATIC,
        duration_seconds=30,
        brand_name="Lumière",
        mood="romantique"
    )
    result = engine.process(prompt)
    print(json.dumps(result.__dict__, indent=2, ensure_ascii=False, default=str))
