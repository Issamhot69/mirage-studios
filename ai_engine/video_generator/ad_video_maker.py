"""
Mirage Studios — Ad Video Maker
Génération automatique de vidéos publicitaires (15-60 secondes).
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from prompt_engine import PromptEngine, VideoPrompt, VideoType, VideoStyle, StructuredVideoScript


class AdFormat(Enum):
    STORY = "9:16"        # Instagram/TikTok Stories
    SQUARE = "1:1"        # Instagram Feed
    LANDSCAPE = "16:9"    # YouTube / TV
    VERTICAL = "4:5"      # Instagram Feed vertical


@dataclass
class AdConfig:
    brand_name: str
    product_description: str
    target_audience: str
    duration_seconds: int       # 15, 30, 45 ou 60
    format: AdFormat
    language: str = "fr"
    mood: str = "professionnel"
    style: VideoStyle = VideoStyle.COMMERCIAL
    include_voiceover: bool = True
    include_subtitles: bool = True
    music_track: Optional[str] = None


@dataclass
class AdVideoResult:
    config: AdConfig
    script: StructuredVideoScript
    storyboard: List[dict]
    assets_required: List[str]
    estimated_render_time: int   # secondes
    output_formats: List[str]


class AdVideoMaker:
    """Générateur de vidéos publicitaires IA."""

    PLATFORM_SPECS = {
        AdFormat.STORY: {"width": 1080, "height": 1920, "safe_zone": 0.8},
        AdFormat.SQUARE: {"width": 1080, "height": 1080, "safe_zone": 0.9},
        AdFormat.LANDSCAPE: {"width": 1920, "height": 1080, "safe_zone": 0.9},
        AdFormat.VERTICAL: {"width": 1080, "height": 1350, "safe_zone": 0.85},
    }

    def __init__(self):
        self.prompt_engine = PromptEngine()

    def generate(self, config: AdConfig) -> AdVideoResult:
        """Génère une vidéo publicitaire complète."""
        print(f"[AdMaker] Génération pub {config.duration_seconds}s pour {config.brand_name}")

        # Créer le prompt structuré
        prompt = VideoPrompt(
            raw_text=config.product_description,
            language=config.language,
            video_type=VideoType.AD,
            style=config.style,
            duration_seconds=config.duration_seconds,
            brand_name=config.brand_name,
            mood=config.mood,
            target_audience=config.target_audience,
        )

        script = self.prompt_engine.process(prompt)
        storyboard = self._generate_storyboard(script, config)
        assets = self._list_required_assets(script, config)

        return AdVideoResult(
            config=config,
            script=script,
            storyboard=storyboard,
            assets_required=assets,
            estimated_render_time=config.duration_seconds * 3,
            output_formats=self._get_output_formats(config),
        )

    def _generate_storyboard(self, script: StructuredVideoScript, config: AdConfig) -> List[dict]:
        """Génère le storyboard visuel scène par scène."""
        specs = self.PLATFORM_SPECS[config.format]
        storyboard = []
        for scene in script.scenes:
            frame = {
                "scene_id": scene["id"],
                "duration": scene["duration"],
                "type": scene["type"],
                "description": scene["desc"],
                "resolution": f"{specs['width']}x{specs['height']}",
                "format": config.format.value,
                "safe_zone": specs["safe_zone"],
                "visual_prompt": self._build_visual_prompt(scene, script, config),
                "text_overlay": self._get_text_overlay(scene, script, config),
                "transition": "fade" if scene["type"] == "cta" else "cut",
            }
            storyboard.append(frame)
        return storyboard

    def _build_visual_prompt(self, scene: dict, script: StructuredVideoScript, config: AdConfig) -> str:
        """Construit le prompt Stable Diffusion pour chaque scène."""
        base = f"{script.visual_style} style, {script.color_palette[0]} dominant color"
        scene_prompts = {
            "hook": f"dramatic opening shot, {config.brand_name}, high impact visual",
            "problem": "relatable everyday situation, natural lighting, authentic",
            "solution": f"product hero shot, {config.brand_name}, premium quality",
            "features": "split screen benefit visualization, clean composition",
            "testimonial": "authentic person, warm lighting, trust and confidence",
            "cta": f"{config.brand_name} logo, brand colors, call to action text",
            "product": f"product closeup, {config.brand_name}, commercial photography",
            "story": "narrative scene, cinematic, emotional connection",
        }
        scene_specific = scene_prompts.get(scene["type"], "cinematic shot, professional")
        return f"{scene_specific}, {base}, 4K, commercial quality, no text"

    def _get_text_overlay(self, scene: dict, script: StructuredVideoScript, config: AdConfig) -> dict:
        """Définit les textes à superposer sur chaque scène."""
        if scene["type"] == "cta":
            return {
                "headline": script.call_to_action,
                "subtext": config.brand_name,
                "position": "center",
                "style": "bold",
            }
        elif scene["type"] == "hook":
            return {
                "headline": config.brand_name,
                "subtext": None,
                "position": "bottom_third",
                "style": "elegant",
            }
        return {"headline": None, "subtext": None, "position": None, "style": None}

    def _list_required_assets(self, script: StructuredVideoScript, config: AdConfig) -> List[str]:
        assets = [
            f"logo_{config.brand_name.lower().replace(' ', '_')}.png",
            f"music_{script.music_mood[:20].replace(' ', '_')}.mp3",
        ]
        if config.include_voiceover:
            assets.append(f"voiceover_{config.language}.mp3")
        if config.include_subtitles:
            assets.append(f"subtitles_{config.language}.srt")
        for i in range(len(script.scenes)):
            assets.append(f"scene_{i+1:02d}_visual.png")
        return assets

    def _get_output_formats(self, config: AdConfig) -> List[str]:
        base = [f"output_{config.format.value.replace(':', 'x')}.mp4"]
        if config.format == AdFormat.LANDSCAPE:
            base.extend(["output_story_9x16.mp4", "output_square_1x1.mp4"])
        return base

    def quick_generate(self, prompt_text: str, brand: str, duration: int = 30,
                       language: str = "fr", format: AdFormat = AdFormat.LANDSCAPE) -> AdVideoResult:
        """Génération rapide depuis un simple prompt texte."""
        config = AdConfig(
            brand_name=brand,
            product_description=prompt_text,
            target_audience="general",
            duration_seconds=duration,
            format=format,
            language=language,
        )
        return self.generate(config)


if __name__ == "__main__":
    import json
    maker = AdVideoMaker()
    result = maker.quick_generate(
        prompt_text="Parfum de luxe pour femme, notes florales, ambiance Paris nuit",
        brand="Lumière Paris",
        duration=30,
        language="fr",
        format=AdFormat.LANDSCAPE,
    )
    print(f"✅ Pub générée : {result.script.title}")
    print(f"📋 {len(result.storyboard)} scènes")
    print(f"🎨 Palette : {result.script.color_palette}")
    print(f"🎵 Musique : {result.script.music_mood}")
    print(f"📦 Assets requis : {len(result.assets_required)}")
    print(f"⏱️  Rendu estimé : {result.estimated_render_time}s")
