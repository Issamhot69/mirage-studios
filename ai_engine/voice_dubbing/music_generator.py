"""
Mirage Studios — Music Generator
Génération musicale via MusicGen (Meta) sur Replicate.
Tous les styles : orchestral, jazz, électronique, arabe, etc.
"""

import os
import time
import requests
from dataclasses import dataclass
from typing import Optional

REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")

# Styles musicaux par genre de film
MUSIC_STYLES = {
    "fantastique": "epic orchestral fantasy music, strings, choir, dramatic, cinematic",
    "thriller": "dark suspense music, tension, low strings, piano, mysterious",
    "drame": "emotional piano, strings, melancholic, deep, touching",
    "comedie": "upbeat playful music, fun, light, happy, comedic",
    "historique": "period music, classical orchestra, authentic, grand",
    "romantique": "romantic piano, soft strings, warm, tender, love theme",
    "action": "intense action music, drums, brass, fast tempo, powerful",
    "horreur": "dark ambient, horror, dissonant, scary, tension",
    "publicite": "commercial background, upbeat, professional, brand music",
    "arabe": "arabic music, oud, darbuka, maqam, oriental, traditional",
    "jazz": "jazz piano, saxophone, upright bass, swing, smooth",
    "electronique": "electronic ambient, synthesizer, modern, cinematic",
    "custom": ""  # Style libre défini par l'utilisateur
}


@dataclass
class MusicRequest:
    style: str                    # Clé dans MUSIC_STYLES ou "custom"
    duration_seconds: int = 30    # 5 à 120 secondes
    custom_prompt: str = ""       # Si style = "custom"
    mood: str = "neutral"         # "happy", "sad", "tense", "epic"
    tempo: str = "medium"         # "slow", "medium", "fast"
    instrumental: bool = True     # Pas de paroles par défaut
    film_title: str = ""          # Pour personnaliser le prompt


@dataclass
class MusicResult:
    success: bool
    audio_url: Optional[str] = None
    prediction_id: Optional[str] = None
    status: str = "pending"
    duration_seconds: int = 0
    style: str = ""
    prompt_used: str = ""
    error: Optional[str] = None
    cost_estimate: float = 0.01


class MusicGenerator:
    """Générateur de musique IA via MusicGen sur Replicate."""

    BASE_URL = "https://api.replicate.com/v1"
    # MusicGen Large — meilleure qualité
    MODEL = "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043692f5a8f6a32f8f3d5e28c18"

    def __init__(self):
        self.token = REPLICATE_TOKEN
        self.headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
        }

    def is_configured(self) -> bool:
        return bool(self.token and len(self.token) > 10)

    def generate(self, request: MusicRequest) -> MusicResult:
        """Génère une musique complète."""
        if not self.is_configured():
            return MusicResult(
                success=False,
                error="Token Replicate manquant"
            )

        prompt = self._build_prompt(request)
        print(f"[MusicGen] Génération : {prompt[:80]}...")
        print(f"[MusicGen] Durée : {request.duration_seconds}s | Style : {request.style}")

        try:
            response = requests.post(
                f"{self.BASE_URL}/predictions",
                headers=self.headers,
                json={
                    "version": self.MODEL,
                    "input": {
                        "prompt": prompt,
                        "duration": request.duration_seconds,
                        "model_version": "large",
                        "output_format": "mp3",
                        "normalization_strategy": "peak",
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            prediction = response.json()
            pred_id = prediction.get("id")
            print(f"[MusicGen] Prédiction : {pred_id}")

            result = self._wait_for_result(pred_id, request)
            return result

        except Exception as e:
            print(f"[MusicGen] Erreur : {e}")
            return MusicResult(success=False, error=str(e))

    def generate_async(self, request: MusicRequest) -> dict:
        """Lance la génération sans attendre."""
        if not self.is_configured():
            return {
                "demo": True,
                "prediction_id": "demo_music_" + str(int(time.time())),
                "message": "Mode démo — token requis"
            }

        prompt = self._build_prompt(request)
        try:
            response = requests.post(
                f"{self.BASE_URL}/predictions",
                headers=self.headers,
                json={
                    "version": self.MODEL,
                    "input": {
                        "prompt": prompt,
                        "duration": request.duration_seconds,
                        "model_version": "large",
                        "output_format": "mp3",
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            prediction = response.json()
            return {
                "prediction_id": prediction.get("id"),
                "status": prediction.get("status", "starting"),
                "prompt": prompt,
                "duration": request.duration_seconds,
                "estimated_cost": f"${self.estimate_cost(request.duration_seconds)}",
            }
        except Exception as e:
            return {"error": str(e)}

    def get_status(self, prediction_id: str) -> dict:
        if prediction_id.startswith("demo_"):
            return {
                "status": "succeeded",
                "output": "https://example.com/demo_music.mp3"
            }
        try:
            response = requests.get(
                f"{self.BASE_URL}/predictions/{prediction_id}",
                headers=self.headers,
                timeout=10
            )
            data = response.json()
            return {
                "status": data.get("status"),
                "output": data.get("output"),
                "error": data.get("error"),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _build_prompt(self, request: MusicRequest) -> str:
        """Construit le prompt musical optimal."""
        if request.style == "custom" and request.custom_prompt:
            base = request.custom_prompt
        else:
            base = MUSIC_STYLES.get(request.style, MUSIC_STYLES["publicite"])

        # Ajouter humeur et tempo
        mood_map = {
            "happy": "joyful, uplifting",
            "sad": "melancholic, emotional",
            "tense": "suspenseful, tense",
            "epic": "epic, powerful, grand",
            "neutral": ""
        }
        tempo_map = {"slow": "slow tempo", "medium": "medium tempo", "fast": "fast tempo"}

        parts = [base]
        mood_str = mood_map.get(request.mood, "")
        if mood_str:
            parts.append(mood_str)
        parts.append(tempo_map.get(request.tempo, "medium tempo"))
        if request.instrumental:
            parts.append("instrumental, no vocals, no lyrics")
        if request.film_title:
            parts.append(f"for the film '{request.film_title}'")

        return ", ".join(filter(None, parts))

    def _wait_for_result(self, prediction_id: str,
                         request: MusicRequest, timeout: int = 180) -> MusicResult:
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_status(prediction_id)
            print(f"[MusicGen] Status : {status['status']}")

            if status["status"] == "succeeded":
                output = status.get("output")
                audio_url = output if isinstance(output, str) else (output[0] if output else None)
                return MusicResult(
                    success=True,
                    audio_url=audio_url,
                    prediction_id=prediction_id,
                    status="succeeded",
                    duration_seconds=request.duration_seconds,
                    style=request.style,
                    prompt_used=self._build_prompt(request),
                    cost_estimate=self.estimate_cost(request.duration_seconds)
                )
            elif status["status"] == "failed":
                return MusicResult(
                    success=False,
                    error=status.get("error", "Génération échouée"),
                    prediction_id=prediction_id,
                    status="failed"
                )
            time.sleep(3)

        return MusicResult(success=False, error="Timeout")

    def estimate_cost(self, duration_seconds: int) -> float:
        """Estime le coût : ~$0.01 par 10 secondes."""
        return round(0.01 * (duration_seconds / 10), 3)

    def get_styles_for_genre(self, genre: str) -> str:
        """Retourne le style musical recommandé pour un genre."""
        return MUSIC_STYLES.get(genre.lower(), MUSIC_STYLES["publicite"])

    def list_styles(self) -> dict:
        """Liste tous les styles disponibles."""
        return {k: v[:60] + "..." if len(v) > 60 else v
                for k, v in MUSIC_STYLES.items()}


if __name__ == "__main__":
    gen = MusicGenerator()

    if not gen.is_configured():
        print("⚠️  Token Replicate manquant !")
    else:
        print("✅ MusicGen configuré !")
        print("\nStyles disponibles :")
        for style, desc in gen.list_styles().items():
            print(f"  {style}: {desc[:50]}")

        req = MusicRequest(
            style="fantastique",
            duration_seconds=30,
            mood="epic",
            tempo="fast",
            film_title="نور وظلام"
        )
        cost = gen.estimate_cost(req.duration_seconds)
        print(f"\n💰 Coût estimé : ${cost}")
        result = gen.generate_async(req)
        print(f"🎵 Résultat : {result}")