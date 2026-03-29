"""
Mirage Studios — VFX Pipeline
Orchestration de la chaîne de traitement des effets visuels.
"""

from dataclasses import dataclass, field
from typing import List
from enum import Enum


class VFXType(Enum):
    PARTICLE = "particle"
    BACKGROUND = "background"
    CHARACTER = "character_fx"
    TRANSITION = "transition"
    COLOR_GRADE = "color_grade"


@dataclass
class VFXShot:
    shot_id: str
    scene: str
    fx_type: VFXType
    duration_frames: int
    resolution: tuple = (1920, 1080)
    notes: str = ""


@dataclass
class VFXPipeline:
    project_name: str
    shots: List[VFXShot] = field(default_factory=list)
    output_dir: str = "renders/"

    def add_shot(self, shot: VFXShot):
        self.shots.append(shot)
        print(f"[VFX] Shot ajouté : {shot.shot_id} ({shot.fx_type.value})")

    def process_all(self):
        """Traite tous les shots dans l'ordre."""
        for shot in self.shots:
            self._process_shot(shot)

    def _process_shot(self, shot: VFXShot):
        print(f"[VFX] Rendu {shot.shot_id} → {shot.fx_type.value} @ {shot.resolution[0]}x{shot.resolution[1]}")

    def generate_report(self) -> dict:
        return {
            "project": self.project_name,
            "total_shots": len(self.shots),
            "total_frames": sum(s.duration_frames for s in self.shots),
            "fx_types": list({s.fx_type.value for s in self.shots}),
        }


if __name__ == "__main__":
    import json
    pipeline = VFXPipeline("Mirage_Project_Alpha")
    pipeline.add_shot(VFXShot("S01", "Scène du château", VFXType.BACKGROUND, 120))
    pipeline.add_shot(VFXShot("S02", "Combat final", VFXType.PARTICLE, 240))
    pipeline.process_all()
    print(json.dumps(pipeline.generate_report(), indent=2))
