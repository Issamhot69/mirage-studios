"""
Mirage Studios — Routes Replicate Video
Endpoints Flask pour la génération vidéo via Replicate.
"""

from flask import Blueprint, request, jsonify
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ai_engine', 'video_generator'))

replicate_bp = Blueprint('replicate', __name__, url_prefix='/api/video')


def get_generator():
    from replicate_generator import ReplicateVideoGenerator
    return ReplicateVideoGenerator()


@replicate_bp.route('/status', methods=['GET'])
def video_status():
    """Vérifie si Replicate est configuré."""
    token = os.environ.get("REPLICATE_API_TOKEN", "")
    configured = bool(token and len(token) > 10)
    return jsonify({
        "configured": configured,
        "status": "ready" if configured else "missing_token",
        "message": "Replicate prêt !" if configured else "Ajoute REPLICATE_API_TOKEN dans config.json",
        "models": ["wan2.1", "wan2.2", "cogvideox"],
        "cost_per_5s": "$0.05"
    })


@replicate_bp.route('/generate', methods=['POST'])
def generate_video():
    """Lance la génération d'une vidéo."""
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Champ 'prompt' requis"}), 400

    token = os.environ.get("REPLICATE_API_TOKEN", "")
    if not token:
        return jsonify({
            "demo": True,
            "message": "Mode démo — ajoute REPLICATE_API_TOKEN",
            "prediction_id": "demo_preview",
            "estimated_cost": "$0.05",
            "prompt": data['prompt']
        }), 200

    try:
        from replicate_generator import ReplicateVideoGenerator, VideoRequest
        gen = ReplicateVideoGenerator()
        req = VideoRequest(
            prompt=data['prompt'],
            duration_seconds=int(data.get('duration_seconds', 5)),
            width=int(data.get('width', 1280)),
            height=int(data.get('height', 720)),
            model=data.get('model', 'wan2.1'),
            negative_prompt=data.get('negative_prompt', 'blurry, low quality'),
        )
        # Génération asynchrone
        result = gen.generate_async(req)
        cost = gen.estimate_cost(req.duration_seconds)
        return jsonify({
            "success": True,
            "prediction_id": result.get("prediction_id"),
            "status": result.get("status", "starting"),
            "estimated_cost": f"${cost}",
            "check_url": f"/api/video/check/{result.get('prediction_id')}",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@replicate_bp.route('/check/<prediction_id>', methods=['GET'])
def check_video(prediction_id):
    """Vérifie le statut d'une génération."""
    token = os.environ.get("REPLICATE_API_TOKEN", "")
    if not token:
        return jsonify({
            "status": "succeeded",
            "demo": True,
            "video_url": "https://example.com/demo_video.mp4",
            "message": "Mode démo — vraie vidéo disponible avec le token"
        })

    try:
        from replicate_generator import ReplicateVideoGenerator
        gen = ReplicateVideoGenerator()
        status = gen.get_status(prediction_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@replicate_bp.route('/estimate', methods=['POST'])
def estimate_cost():
    """Estime le coût d'une génération."""
    data = request.get_json() or {}
    duration = int(data.get('duration_seconds', 5))
    quality = data.get('quality', 'standard')
    costs = {"draft": 0.025, "standard": 0.05, "hd": 0.10, "4k": 0.20}
    cost_per_5s = costs.get(quality, 0.05)
    total = round(cost_per_5s * (duration / 5), 3)
    return jsonify({
        "duration_seconds": duration,
        "quality": quality,
        "cost_usd": total,
        "cost_per_minute": round(total * (60 / duration), 2),
    })


@replicate_bp.route('/models', methods=['GET'])
def list_models():
    """Liste les modèles vidéo disponibles."""
    return jsonify({
        "models": [
            {"id": "wan2.1", "name": "Wan 2.1", "quality": "⭐⭐⭐⭐", "cost": "$0.05/5s"},
            {"id": "wan2.2", "name": "Wan 2.2", "quality": "⭐⭐⭐⭐⭐", "cost": "$0.08/5s"},
            {"id": "cogvideox", "name": "CogVideoX", "quality": "⭐⭐⭐⭐", "cost": "$0.06/5s"},
        ]
    })
