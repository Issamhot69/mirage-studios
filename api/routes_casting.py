"""
Mirage Studios — Routes Casting IA
Endpoints Flask pour la génération de casting virtuel.
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ai_engine'))

casting_bp = Blueprint('casting', __name__, url_prefix='/api/casting')


def get_agent():
    from casting_ai import CastingAI
    return CastingAI()


@casting_bp.route('/generate', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_casting():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data:
        return jsonify({"error": "Données requises"}), 400

    try:
        agent = get_agent()
        use_claude = bool(os.environ.get("ANTHROPIC_API_KEY"))

        if use_claude:
            result = agent.generate_with_claude(data)
        else:
            casting = agent.generate_full_casting(data)
            result = agent._casting_to_dict(casting)

        return jsonify({"success": True, "casting": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@casting_bp.route('/name', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_name():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json() or {}
    culture = data.get('culture', 'marocain')
    gender = data.get('gender', 'm')

    try:
        agent = get_agent()
        name = agent.generate_name(culture, gender)
        return jsonify({"success": True, "name": name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@casting_bp.route('/cultures', methods=['GET'])
@cross_origin()
def list_cultures():
    return jsonify({
        "cultures": [
            {"id": "marocain", "label": "Marocain", "label_ar": "مغربي"},
            {"id": "arabe", "label": "Arabe", "label_ar": "عربي"},
            {"id": "francais", "label": "Français", "label_ar": "فرنسي"},
            {"id": "anglais", "label": "Anglais", "label_ar": "إنجليزي"},
            {"id": "espagnol", "label": "Espagnol", "label_ar": "إسباني"},
        ]
    })


@casting_bp.route('/roles', methods=['GET'])
@cross_origin()
def list_roles():
    from casting_ai import ROLES
    return jsonify({"roles": ROLES})