"""
Mirage Studios — Replicate Video Generator
"""

import os
import time
import requests
from dataclasses import dataclass
from typing import Optional

REPLICATE_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")

MODELS = {
    "wan2.1": "wavespeedai/wan-2.1-t2v-480p",
    "wan2.2": "wavespeedai/wan-2.1-t2v-720p",
    "cogvideox": "tencent/cogvideox-5b",
}


@dataclass
class VideoRequest:
    prompt: str
    duration_seconds: int = 5
    width: int = 848
    height: int = 480
    fps: int = 16
    model: str = "wan2.1"
    negative_prompt: str = "blurry, low quality, distorted"
    num_inference_steps: int = 30


@dataclass
class VideoResult:
    success: bool
    video_url: Optional[str] = None
    prediction_id: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None
    cost_estimate: float = 0.05


class ReplicateVideoGenerator:
    BASE_URL = "https://api.replicate.com/v1"

    def __init__(self):
        self.token = REPLICATE_TOKEN
        self.headers = {
            "Authorization": f"Token {self.token}",
            "Content-Type": "application/json",
        }

    def is_configured(self) -> bool:
        return bool(self.token and len(self.token) > 10)

    def generate_async(self, request: VideoRequest) -> dict:
        if not self.is_configured():
            return {
                "error": "Token manquant",
                "demo": True,
                "prediction_id": "demo_" + str(int(time.time()))
            }
        try:
            model_id = MODELS.get(request.model, MODELS["wan2.1"])
            payload = self._build_payload(request)
            response = requests.post(
                f"{self.BASE_URL}/models/{model_id}/predictions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            prediction = response.json()
            print(f"[Replicate] Prédiction lancée : {prediction.get('id')}")
            return {
                "prediction_id": prediction.get("id"),
                "status": prediction.get("status", "starting"),
                "urls": prediction.get("urls", {}),
            }
        except Exception as e:
            print(f"[Replicate] Erreur : {e}")
            return {"error": str(e)}

    def get_status(self, prediction_id: str) -> dict:
        if not prediction_id or prediction_id.startswith("demo_"):
            return {
                "status": "succeeded",
                "output": ["https://example.com/demo_video.mp4"]
            }
        try:
            response = requests.get(
                f"{self.BASE_URL}/predictions/{prediction_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return {
                "status": data.get("status"),
                "output": data.get("output"),
                "error": data.get("error"),
                "metrics": data.get("metrics", {}),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _build_payload(self, request: VideoRequest) -> dict:
        num_frames = request.duration_seconds * request.fps
        return {
            "input": {
                "prompt": request.prompt,
                "negative_prompt": request.negative_prompt,
                "num_frames": num_frames,
                "num_inference_steps": request.num_inference_steps,
                "width": request.width,
                "height": request.height,
            }
        }

    def estimate_cost(self, duration_seconds: int, quality: str = "standard") -> float:
        costs = {"draft": 0.025, "standard": 0.05, "hd": 0.10}
        return round(costs.get(quality, 0.05) * (duration_seconds / 5), 3)


if __name__ == "__main__":
    gen = ReplicateVideoGenerator()
    if not gen.is_configured():
        print("Token Replicate manquant !")
    else:
        print("Replicate configure !")
        req = VideoRequest(
            prompt="Chateau medieval sur une falaise, coucher de soleil dore",
            duration_seconds=5,
            model="wan2.1"
        )
        result = gen.generate_async(req)
        print(result)