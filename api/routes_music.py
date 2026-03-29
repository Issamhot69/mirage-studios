"""
Mirage Studios — Routes Music Generator
Endpoints Flask pour la génération musicale via MusicGen.
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ai_engine', 'voice_dubbing'))

music_bp = Blueprint('music', __name__, url_prefix='/api/music')


def get_generator():
    from music_generator import MusicGenerator
    return MusicGenerator()


@music_bp.route('/status', methods=['GET'])
@cross_origin()
def music_status():
    """Vérifie si MusicGen est configuré."""
    token = os.environ.get("REPLICATE_API_TOKEN", "")
    configured = bool(token and len(token) > 10)
    return jsonify({
        "configured": configured,
        "model": "MusicGen Large (Meta)",
        "status": "ready" if configured else "missing_token",
        "cost_per_30s": "$0.03",
        "styles": [
            "fantastique", "thriller", "drame", "comedie",
            "historique", "romantique", "action", "arabe",
            "jazz", "electronique", "publicite", "custom"
        ]
    })


@music_bp.route('/generate', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_music():
    """Génère une musique."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data or 'style' not in data:
        return jsonify({"error": "Champ 'style' requis"}), 400

    token = os.environ.get("REPLICATE_API_TOKEN", "")
    if not token:
        return jsonify({
            "demo": True,
            "message": "Mode démo — token Replicate requis",
            "prediction_id": "demo_music",
            "style": data.get('style'),
            "estimated_cost": "$0.03"
        }), 200

    try:
        from music_generator import MusicGenerator, MusicRequest
        gen = MusicGenerator()
        req = MusicRequest(
            style=data['style'],
            duration_seconds=int(data.get('duration_seconds', 30)),
            custom_prompt=data.get('custom_prompt', ''),
            mood=data.get('mood', 'neutral'),
            tempo=data.get('tempo', 'medium'),
            instrumental=data.get('instrumental', True),
            film_title=data.get('film_title', ''),
        )
        result = gen.generate_async(req)
        return jsonify({
            "success": True,
            "prediction_id": result.get("prediction_id"),
            "status": result.get("status", "starting"),
            "prompt": result.get("prompt"),
            "duration": req.duration_seconds,
            "estimated_cost": f"${gen.estimate_cost(req.duration_seconds)}",
            "check_url": f"/api/music/check/{result.get('prediction_id')}",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@music_bp.route('/check/<prediction_id>', methods=['GET'])
@cross_origin()
def check_music(prediction_id):
    """Vérifie le statut d'une génération musicale."""
    if prediction_id.startswith("demo_"):
        return jsonify({
            "status": "succeeded",
            "demo": True,
            "audio_url": "https://example.com/demo_music.mp3"
        })
    try:
        from music_generator import MusicGenerator
        gen = MusicGenerator()
        status = gen.get_status(prediction_id)
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@music_bp.route('/styles', methods=['GET'])
@cross_origin()
def list_styles():
    """Liste tous les styles musicaux disponibles."""
    from music_generator import MUSIC_STYLES
    return jsonify({
        "styles": [
            {"id": k, "description": v[:80], "genre": k}
            for k, v in MUSIC_STYLES.items()
        ],
        "total": len(MUSIC_STYLES)
    })


@music_bp.route('/recommend', methods=['POST'])
@cross_origin()
def recommend_style():
    """Recommande un style musical selon le genre du film."""
    data = request.get_json() or {}
    genre = data.get('genre', 'publicite').lower()
    from music_generator import MusicGenerator, MUSIC_STYLES
    gen = MusicGenerator()
    style = gen.get_styles_for_genre(genre)
    return jsonify({
        "genre": genre,
        "recommended_style": style,
        "style_id": genre if genre in MUSIC_STYLES else "publicite",
        "mood_suggestion": {
            "fantastique": "epic",
            "thriller": "tense",
            "drame": "sad",
            "comedie": "happy",
            "action": "epic",
        }.get(genre, "neutral")
    })


@music_bp.route('/estimate', methods=['POST'])
@cross_origin()
def estimate_cost():
    """Estime le coût d'une génération musicale."""
    data = request.get_json() or {}
    duration = int(data.get('duration_seconds', 30))
    cost = round(0.01 * (duration / 10), 3)
    return jsonify({
        "duration_seconds": duration,
        "cost_usd": cost,
        "cost_per_minute": round(cost * (60 / duration), 3),
    })