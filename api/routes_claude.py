from flask import Blueprint, request, jsonify
import os
import sys

CLAUDE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ai_engine', 'claude_integration')
sys.path.insert(0, os.path.abspath(CLAUDE_PATH))

claude_bp = Blueprint('claude', __name__, url_prefix='/api/claude')


@claude_bp.route('/synopsis', methods=['POST'])
def generate_synopsis():
    data = request.get_json()
    if not data or 'logline' not in data:
        return jsonify({"error": "Champ 'logline' requis"}), 400
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "sk-ant-VOTRE_CLE_ICI":
        return jsonify({"demo": True, "synopsis": f"[DEMO] Synopsis pour : {data.get('logline', '')}"}), 200
    try:
        from claude_generator import ClaudeScriptGenerator, ScriptRequest
        gen = ClaudeScriptGenerator()
        req = ScriptRequest(
            genre=data.get('genre', 'fantastique'),
            duration_minutes=int(data.get('duration_minutes', 90)),
            language=data.get('language', 'fr'),
            tone=data.get('tone', 'epique'),
            logline=data['logline'],
            hero_name=data.get('hero_name'),
            world_description=data.get('world_description'),
        )
        synopsis = gen.generate_synopsis(req)
        return jsonify({"success": True, "synopsis": synopsis})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@claude_bp.route('/scene', methods=['POST'])
def generate_scene():
    data = request.get_json()
    if not data or 'description' not in data:
        return jsonify({"error": "Champ 'description' requis"}), 400
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "sk-ant-VOTRE_CLE_ICI":
        return jsonify({"demo": True, "scene": f"[DEMO] Scene pour : {data['description'][:50]}"}), 200
    try:
        from claude_generator import ClaudeScriptGenerator
        gen = ClaudeScriptGenerator()
        scene = gen.generate_scene(data['description'], data.get('language', 'fr'))
        return jsonify({"success": True, "scene": scene})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@claude_bp.route('/dialogue', methods=['POST'])
def generate_dialogue():
    data = request.get_json()
    required = ['character1', 'character2', 'context']
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Champs manquants : {missing}"}), 400
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "sk-ant-VOTRE_CLE_ICI":
        return jsonify({"demo": True, "dialogue": f"[DEMO] Dialogue entre {data['character1']} et {data['character2']}"}), 200
    try:
        from claude_generator import ClaudeScriptGenerator
        gen = ClaudeScriptGenerator()
        dialogue = gen.generate_dialogue(
            data['character1'], data['character2'],
            data['context'], data.get('language', 'fr')
        )
        return jsonify({"success": True, "dialogue": dialogue})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@claude_bp.route('/ad-script', methods=['POST'])
def generate_ad_script():
    data = request.get_json()
    required = ['brand', 'product']
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Champs manquants : {missing}"}), 400
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "sk-ant-VOTRE_CLE_ICI":
        return jsonify({"demo": True, "script": f"[DEMO] Script pub pour {data['brand']}"}), 200
    try:
        from claude_generator import ClaudeScriptGenerator
        gen = ClaudeScriptGenerator()
        script = gen.generate_ad_script(
            data['brand'], data['product'],
            int(data.get('duration_seconds', 30)),
            data.get('language', 'fr')
        )
        return jsonify({"success": True, "script": script})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@claude_bp.route('/titles', methods=['POST'])
def generate_titles():
    data = request.get_json()
    if not data or 'logline' not in data:
        return jsonify({"error": "Champ 'logline' requis"}), 400
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "sk-ant-VOTRE_CLE_ICI":
        return jsonify({"demo": True, "titres": [{"ar": "نور وظلام", "fr": "Lumiere et Tenebres", "en": "Light and Darkness"}]}), 200
    try:
        from claude_generator import ClaudeScriptGenerator
        gen = ClaudeScriptGenerator()
        titles = gen.generate_film_title(data['logline'], data.get('language', 'ar'))
        return jsonify({"success": True, **titles})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@claude_bp.route('/status', methods=['GET'])
def claude_status():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    configured = bool(api_key and api_key != "sk-ant-VOTRE_CLE_ICI")
    return jsonify({
        "configured": configured,
        "model": "claude-sonnet-4-20250514",
        "status": "ready" if configured else "missing_key",
        "message": "Claude API prete !" if configured else "Ajoute ta cle ANTHROPIC_API_KEY"
    })