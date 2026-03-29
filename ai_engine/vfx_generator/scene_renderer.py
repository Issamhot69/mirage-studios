"""
Mirage Studios — Scene Renderer
Composition finale et rendu des scènes avec calques VFX.
"""

from dataclasses import dataclass, field
from typing import List
from enum import Enum


class LayerType(Enum):
    BACKGROUND = "bg"
    MIDGROUND = "mg"
    FOREGROUND = "fg"
    VFX = "vfx"
    GRADE = "grade"


@dataclass
class RenderLayer:
    name: str
    layer_type: LayerType
    source: str
    opacity: float = 1.0
    blend_mode: str = "normal"
    enabled: bool = True


@dataclass
class SceneRender:
    scene_id: str
    width: int = 1920
    height: int = 1080
    fps: int = 24
    layers: List[RenderLayer] = field(default_factory=list)

    def add_layer(self, layer: RenderLayer):
        self.layers.append(layer)

    def render(self, output_path: str) -> dict:
        """Lance le rendu de la scène."""
        active = [l for l in self.layers if l.enabled]
        print(f"[Renderer] Scène {self.scene_id} → {len(active)} calques actifs")
        for layer in active:
            print(f"  ├─ [{layer.layer_type.value}] {layer.name} (opacity={layer.opacity})")
        return {
            "scene": self.scene_id,
            "output": output_path,
            "resolution": f"{self.width}x{self.height}",
            "fps": self.fps,
            "layers_rendered": len(active),
        }

    def preview(self) -> dict:
        return self.render(f"previews/{self.scene_id}_preview.jpg")


if __name__ == "__main__":
    scene = SceneRender("SC042_nuit_chateau")
    scene.add_layer(RenderLayer("Fond ciel nocturne", LayerType.BACKGROUND, "bg/night_sky.exr"))
    scene.add_layer(RenderLayer("Château", LayerType.MIDGROUND, "assets/castle.png"))
    scene.add_layer(RenderLayer("Particules magie", LayerType.VFX, "vfx/magic_particles.mov", opacity=0.8))
    scene.add_layer(RenderLayer("Color Grade", LayerType.GRADE, "luts/cinematic_cold.cube"))
    result = scene.render("output/SC042_final.mov")
    print(result)
