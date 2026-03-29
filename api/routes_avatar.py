"""
Mirage Studios — Routes Avatar IA
Endpoints Flask pour la génération d'avatars parlants via D-ID.
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ai_engine'))

avatar_bp = Blueprint('avatar', __name__, url_prefix='/api/avatar')


def get_generator():
    from avatar_generator import AvatarGenerator
    return AvatarGenerator()


@avatar_bp.route('/status', methods=['GET'])
@cross_origin()
def avatar_status():
    """Vérifie si D-ID est configuré."""
    api_key = os.environ.get("DID_API_KEY", "")
    configured = bool(api_key and len(api_key) > 10)
    return jsonify({
        "configured": configured,
        "service": "D-ID API",
        "status": "ready" if configured else "missing_key",
        "message": "D-ID prêt !" if configured else "Ajoute DID_API_KEY dans config.json",
        "cost_per_video": "$0.10",
        "languages": ["fr", "ar", "en", "es", "de"],
    })


@avatar_bp.route('/create', methods=['POST', 'OPTIONS'])
@cross_origin()
def create_avatar():
    """Crée un avatar parlant depuis une photo."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data:
        return jsonify({"error": "Données requises"}), 400

    required = ['image_url', 'text']
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Champs manquants : {missing}"}), 400

    api_key = os.environ.get("DID_API_KEY", "")
    if not api_key:
        return jsonify({
            "demo": True,
            "talk_id": "demo_avatar",
            "message": "Mode démo — ajoute DID_API_KEY dans config.json",
            "estimated_cost": "$0.10",
        }), 200

    try:
        from avatar_generator import AvatarGenerator, AvatarRequest
        gen = AvatarGenerator()
        req = AvatarRequest(
            image_url=data['image_url'],
            text=data['text'],
            language=data.get('language', 'fr'),
            gender=data.get('gender', 'male'),
        )
        result = gen.create_async(req)
        return jsonify({
            "success": True,
            "talk_id": result.get("talk_id"),
            "status": result.get("status", "created"),
            "check_url": f"/api/avatar/check/{result.get('talk_id')}",
            "estimated_cost": "$0.10",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@avatar_bp.route('/check/<talk_id>', methods=['GET'])
@cross_origin()
def check_avatar(talk_id):
    """Vérifie le statut d'un avatar."""
    if talk_id.startswith("demo_"):
        return jsonify({
            "status": "done",
            "demo": True,
            "result_url": "https://example.com/demo_avatar.mp4"
        })

    try:
        from avatar_generator import AvatarGenerator
        gen = AvatarGenerator()
        status = gen.get_status(talk_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@avatar_bp.route('/voices', methods=['GET'])
@cross_origin()
def list_voices():
    """Liste les voix disponibles par langue."""
    from avatar_generator import VOICES
    return jsonify({
        "voices": VOICES,
        "languages": list(VOICES.keys()),
    })


@avatar_bp.route('/estimate', methods=['POST'])
@cross_origin()
def estimate_cost():
    """Estime le coût d'une création avatar."""
    data = request.get_json() or {}
    text = data.get('text', '')
    words = len(text.split())
    duration = round(words / 130 * 60, 1)
    cost = round(0.10 * (duration / 30), 3)
    return jsonify({
        "text_length": len(text),
        "words": words,
        "estimated_duration_seconds": duration,
        "estimated_cost_usd": cost,
    })