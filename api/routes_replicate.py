"""
Mirage Studios — Routes Video Generator
Generation video via Kling AI (kie.ai API).
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import json
import requests
import time

replicate_bp = Blueprint('replicate', __name__, url_prefix='/api/video')

KLING_BASE_URL = "https://api.kie.ai"


def get_headers():
    api_key = os.environ.get("KLING_API_KEY", "")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


@replicate_bp.route('/status', methods=['GET'])
@cross_origin()
def video_status():
    api_key = os.environ.get("KLING_API_KEY", "")
    configured = bool(api_key and len(api_key) > 10)
    return jsonify({
        "configured": configured,
        "service": "Kling AI (kie.ai)",
        "status": "ready" if configured else "missing_key",
        "models": ["kling2.6", "kling2.1", "kling2.1master"],
        "cost_per_5s": "$0.14",
        "max_resolution": "1080p",
    })


@replicate_bp.route('/generate', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_video():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Champ 'prompt' requis"}), 400

    api_key = os.environ.get("KLING_API_KEY", "")
    if not api_key:
        return jsonify({
            "demo": True,
            "message": "Mode demo",
            "prediction_id": "demo_" + str(int(time.time())),
            "estimated_cost": "$0.14",
        })

    try:
        payload = {
            "model": "kling-2.6/text-to-video",
            "input": {
                "prompt": data['prompt'],
                "duration": "5",
                "aspect_ratio": "16:9",
                "sound": False,
            }
        }

        print(f"[Kling] Generation video : {data['prompt'][:60]}...")
        response = requests.post(
            f"{KLING_BASE_URL}/api/v1/jobs/createTask",
            headers=get_headers(),
            json=payload,
            timeout=30
        )

        print(f"[Kling] Status code: {response.status_code}")
        print(f"[Kling] Response: {response.text[:300]}")

        result = response.json()
        print(f"[Kling] Full result: {result}")

        task_id = None
        if result and result.get("data"):
            task_id = result["data"].get("taskId")

        print(f"[Kling] Task ID: {task_id}")

        return jsonify({
            "success": True,
            "prediction_id": task_id,
            "status": "processing",
            "estimated_cost": "$0.14",
            "check_url": f"/api/video/check/{task_id}",
        })

    except Exception as e:
        print(f"[Kling] Erreur : {e}")
        return jsonify({"error": str(e)}), 500


@replicate_bp.route('/check/<task_id>', methods=['GET'])
@cross_origin()
def check_video(task_id):
    if task_id.startswith("demo_"):
        return jsonify({
            "status": "succeeded",
            "demo": True,
            "video_url": "https://example.com/demo_video.mp4"
        })

    api_key = os.environ.get("KLING_API_KEY", "")
    if not api_key:
        return jsonify({"error": "KLING_API_KEY manquant"}), 500

    try:
        response = requests.get(
            f"{KLING_BASE_URL}/api/v1/jobs/recordInfo?taskId={task_id}",
            headers=get_headers(),
            timeout=10
        )
        print(f"[Kling Check] Response: {response.text[:500]}")
        data = response.json()
        task_data = data.get("data", {})
        status = task_data.get("state", "processing")
        video_url = None

        if status in ["succeed", "success"]:
            result_json = task_data.get("resultJson", "{}")
            result_data = json.loads(result_json) if result_json else {}
            urls = result_data.get("resultUrls", [])
            if urls:
                video_url = urls[0]

        return jsonify({
            "status": "succeeded" if status in ["succeed", "success"] else status,
            "video_url": video_url,
            "task_id": task_id,
            "raw_status": status,
        })

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@replicate_bp.route('/models', methods=['GET'])
@cross_origin()
def list_models():
    return jsonify({
        "models": [
            {"id": "kling2.6", "name": "Kling 2.6", "quality": "⭐⭐⭐⭐⭐", "cost": "$0.14/5s"},
            {"id": "kling2.1", "name": "Kling 2.1 Standard", "quality": "⭐⭐⭐⭐", "cost": "$0.14/5s"},
            {"id": "kling2.1master", "name": "Kling 2.1 Master", "quality": "⭐⭐⭐⭐⭐", "cost": "$0.80/5s"},
        ]
    })