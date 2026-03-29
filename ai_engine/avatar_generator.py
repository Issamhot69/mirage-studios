"""
Mirage Studios — Avatar IA Generator
Transforme une photo en video avec avatar parlant via D-ID API.
"""

import os
import time
import requests
from dataclasses import dataclass
from typing import Optional

DID_API_KEY = os.environ.get("DID_API_KEY", "")
DID_BASE_URL = "https://api.d-id.com"

VOICES = {
    "fr": {
        "male": {"provider": "microsoft", "voice_id": "fr-FR-HenriNeural"},
        "female": {"provider": "microsoft", "voice_id": "fr-FR-DeniseNeural"},
    },
    "ar": {
        "male": {"provider": "microsoft", "voice_id": "ar-SA-HamedNeural"},
        "female": {"provider": "microsoft", "voice_id": "ar-SA-ZariyahNeural"},
    },
    "en": {
        "male": {"provider": "microsoft", "voice_id": "en-US-GuyNeural"},
        "female": {"provider": "microsoft", "voice_id": "en-US-JennyNeural"},
    },
    "es": {
        "male": {"provider": "microsoft", "voice_id": "es-ES-AlvaroNeural"},
        "female": {"provider": "microsoft", "voice_id": "es-ES-ElviraNeural"},
    },
    "de": {
        "male": {"provider": "microsoft", "voice_id": "de-DE-ConradNeural"},
        "female": {"provider": "microsoft", "voice_id": "de-DE-KatjaNeural"},
    },
}


@dataclass
class AvatarRequest:
    image_url: str
    text: str
    language: str = "fr"
    voice_id: str = ""
    provider: str = "microsoft"
    gender: str = "male"


@dataclass
class AvatarResult:
    success: bool
    video_url: Optional[str] = None
    talk_id: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None
    cost_estimate: float = 0.10


class AvatarGenerator:

    def __init__(self):
        self.api_key = os.environ.get("DID_API_KEY", DID_API_KEY)
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def _get_voice(self, language: str, gender: str) -> dict:
        lang_voices = VOICES.get(language, VOICES["fr"])
        return lang_voices.get(gender, lang_voices["male"])

    def create_async(self, request: AvatarRequest) -> dict:
        if not self.is_configured():
            return {
                "demo": True,
                "talk_id": "demo_avatar_" + str(int(time.time())),
                "message": "Mode demo - cle D-ID requise"
            }

        voice = self._get_voice(request.language, request.gender)
        payload = {
            "source_url": request.image_url,
            "script": {
                "type": "text",
                "input": request.text,
                "provider": {
                    "type": voice["provider"],
                    "voice_id": voice["voice_id"],
                }
            }
        }

        print(f"[Avatar] Envoi requete D-ID...")
        print(f"[Avatar] URL: {DID_BASE_URL}/talks")
        print(f"[Avatar] Payload: {payload}")

        response = requests.post(
            f"{DID_BASE_URL}/talks",
            headers=self.headers,
            json=payload,
            timeout=30
        )

        print(f"[Avatar] Status code: {response.status_code}")
        print(f"[Avatar] Response: {response.text[:300]}")

        if response.status_code not in [200, 201]:
            return {"error": f"D-ID erreur {response.status_code}: {response.text[:200]}"}

        data = response.json()
        talk_id = data.get("id")
        print(f"[Avatar] Talk ID: {talk_id}")

        return {
            "talk_id": talk_id,
            "status": data.get("status", "created"),
            "check_url": f"/api/avatar/check/{talk_id}",
            "estimated_cost": "$0.10",
        }

    def get_status(self, talk_id: str) -> dict:
        if talk_id.startswith("demo_"):
            return {
                "status": "done",
                "result_url": "https://example.com/demo_avatar.mp4"
            }
        response = requests.get(
            f"{DID_BASE_URL}/talks/{talk_id}",
            headers=self.headers,
            timeout=10
        )
        data = response.json()
        return {
            "status": data.get("status"),
            "result_url": data.get("result_url"),
            "error": data.get("error"),
        }

    def list_voices(self) -> dict:
        return VOICES

    def estimate_cost(self, text_length: int) -> float:
        words = text_length / 5
        duration = words / 130 * 60
        return round(0.10 * (duration / 30), 3)