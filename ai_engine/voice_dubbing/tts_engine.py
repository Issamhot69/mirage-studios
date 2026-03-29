"""
Mirage Studios — TTS Engine
Synthèse vocale multilingue pour le doublage automatique.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class VoiceGender(Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


@dataclass
class VoiceProfile:
    name: str
    gender: VoiceGender
    language: str       # "fr", "en", "es", "ar", "de"
    pitch: float = 1.0
    speed: float = 1.0
    emotion: str = "neutral"
    provider: str = "elevenlabs"


@dataclass
class TTSRequest:
    text: str
    voice: VoiceProfile
    output_path: str
    sync_to_video: bool = False
    phoneme_timing: bool = True


class TTSEngine:
    SUPPORTED_LANGUAGES = ["fr", "en", "es", "ar", "de", "ja", "zh", "pt", "it"]

    def __init__(self):
        self.voice_library: List[VoiceProfile] = []
        self._load_default_voices()

    def _load_default_voices(self):
        defaults = [
            VoiceProfile("Narrator_FR", VoiceGender.MALE, "fr", pitch=0.95),
            VoiceProfile("Hero_EN", VoiceGender.MALE, "en", pitch=1.0, emotion="calm"),
            VoiceProfile("Villain_FR", VoiceGender.MALE, "fr", pitch=0.7, emotion="angry"),
            VoiceProfile("Guide_Female", VoiceGender.FEMALE, "fr", pitch=1.1),
        ]
        self.voice_library.extend(defaults)

    def synthesize(self, request: TTSRequest) -> dict:
        """Synthétise la voix et retourne les métadonnées."""
        print(f"[TTS] Synthèse : {request.voice.name} ({request.voice.language}) → {request.output_path}")
        word_count = len(request.text.split())
        duration_est = round(word_count / (request.voice.speed * 130 / 60), 1)
        return {
            "output": request.output_path,
            "duration_seconds": duration_est,
            "voice": request.voice.name,
            "language": request.voice.language,
            "word_count": word_count,
        }

    def batch_synthesize(self, requests: List[TTSRequest]) -> List[dict]:
        return [self.synthesize(r) for r in requests]

    def list_voices(self, language: Optional[str] = None) -> List[VoiceProfile]:
        if language:
            return [v for v in self.voice_library if v.language == language]
        return self.voice_library


if __name__ == "__main__":
    engine = TTSEngine()
    req = TTSRequest(
        text="Dans les profondeurs du château, une lumière étrange pulsait au rythme des étoiles.",
        voice=VoiceProfile("Narrator_FR", VoiceGender.MALE, "fr", pitch=0.9, emotion="calm"),
        output_path="audio/narration_sc01.mp3"
    )
    result = engine.synthesize(req)
    print(result)
