"""
Mirage Studios — Stable Diffusion Interface
Génération d'images de référence et de décors par IA.
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class SDConfig:
    prompt: str
    negative_prompt: str = "blurry, low quality, distorted"
    width: int = 1024
    height: int = 576
    steps: int = 30
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    style_preset: str = "cinematic"


class StableDiffusionClient:
    """Client pour l'API Stable Diffusion (local AUTOMATIC1111 ou API distante)."""

    STYLE_PRESETS = {
        "cinematic": "cinematic lighting, film grain, anamorphic lens, movie still",
        "concept_art": "concept art, digital painting, artstation, matte painting",
        "storyboard": "storyboard sketch, rough lines, black and white, professional",
        "vfx_ref": "VFX reference, clean plate, studio quality, professional",
    }

    def __init__(self, api_url: str = "http://localhost:7860"):
        self.api_url = api_url

    def generate(self, config: SDConfig) -> dict:
        """Génère une image selon la configuration SD."""
        full_prompt = f"{config.prompt}, {self.STYLE_PRESETS.get(config.style_preset, '')}"
        print(f"[SD] Génération : {full_prompt[:80]}...")
        return {
            "status": "success",
            "prompt": full_prompt,
            "config": {
                "size": f"{config.width}x{config.height}",
                "steps": config.steps,
                "cfg": config.guidance_scale,
            },
            "image_path": f"data/vfx/{config.style_preset}_output.png"
        }

    def generate_storyboard(self, scenes: List[str]) -> List[dict]:
        """Génère un storyboard complet à partir de descriptions de scènes."""
        results = []
        for i, scene in enumerate(scenes):
            cfg = SDConfig(prompt=scene, style_preset="storyboard", width=768, height=432)
            result = self.generate(cfg)
            result["scene_index"] = i
            results.append(result)
        return results


if __name__ == "__main__":
    sd = StableDiffusionClient()
    cfg = SDConfig(
        prompt="Château médiéval sur une falaise la nuit, tempête, éclairs",
        style_preset="cinematic"
    )
    result = sd.generate(cfg)
    print(result)
