"""
Mirage Studios — Routes Scenario IA
Generation de scenarios complets via Claude AI.
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import anthropic

scenario_bp = Blueprint('scenario', __name__, url_prefix='/api/scenario')


def get_claude():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


@scenario_bp.route('/status', methods=['GET'])
@cross_origin()
def status():
    configured = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return jsonify({
        "configured": configured,
        "status": "ready" if configured else "missing_key",
        "model": "claude-sonnet-4-20250514",
        "languages": ["fr", "ar", "en", "es"],
        "features": ["synopsis", "acts", "dialogues", "scenes", "casting"]
    })


@scenario_bp.route('/synopsis', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_synopsis():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Titre requis"}), 400

    client = get_claude()
    if not client:
        return jsonify({"error": "Claude API non configuree"}), 500

    title = data.get('title', '')
    genre = data.get('genre', 'drame')
    language = data.get('language', 'fr')
    theme = data.get('theme', '')

    lang_map = {"fr": "français", "ar": "arabe", "en": "anglais", "es": "espagnol"}
    lang_name = lang_map.get(language, "français")

    prompt = f"""Tu es un scénariste professionnel de cinéma.

Génère un synopsis complet pour ce film en {lang_name} :
- Titre : {title}
- Genre : {genre}
- Thème : {theme if theme else 'libre'}

Le synopsis doit inclure :
1. Présentation des personnages principaux (3-4 personnages)
2. Situation initiale
3. Élément déclencheur
4. Développement et conflits
5. Climax
6. Résolution

Écris un synopsis professionnel de 300-400 mots en {lang_name}."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        synopsis = message.content[0].text
        return jsonify({
            "success": True,
            "title": title,
            "genre": genre,
            "language": language,
            "synopsis": synopsis,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scenario_bp.route('/full', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_full_scenario():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Titre requis"}), 400

    client = get_claude()
    if not client:
        return jsonify({"error": "Claude API non configuree"}), 500

    title = data.get('title', '')
    genre = data.get('genre', 'drame')
    language = data.get('language', 'fr')
    synopsis = data.get('synopsis', '')
    scenes_count = int(data.get('scenes_count', 10))

    lang_map = {"fr": "français", "ar": "arabe", "en": "anglais", "es": "espagnol"}
    lang_name = lang_map.get(language, "français")

    prompt = f"""Tu es un scénariste professionnel de cinéma.

Génère un scénario complet en {lang_name} pour :
- Titre : {title}
- Genre : {genre}
- Synopsis : {synopsis[:500] if synopsis else 'À développer librement'}
- Nombre de scènes : {scenes_count}

Pour chaque scène génère :
- Numéro et titre de la scène
- Description visuelle (lieu, ambiance, heure)
- Actions des personnages
- Dialogues complets
- Indication de réalisation (plan, mouvement de caméra)

Format JSON strict :
{{
  "title": "{title}",
  "genre": "{genre}",
  "language": "{language}",
  "characters": [
    {{"name": "...", "role": "...", "description": "..."}}
  ],
  "scenes": [
    {{
      "number": 1,
      "title": "...",
      "location": "...",
      "time": "...",
      "description": "...",
      "dialogues": [
        {{"character": "...", "text": "..."}}
      ],
      "camera": "..."
    }}
  ]
}}

Réponds UNIQUEMENT avec le JSON valide."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = message.content[0].text.strip()

        import json
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        scenario = json.loads(text)
        return jsonify({
            "success": True,
            "scenario": scenario,
        })
    except Exception as e:
        return jsonify({"error": str(e), "raw": text if 'text' in locals() else ""}), 500


@scenario_bp.route('/scene', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_scene():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data:
        return jsonify({"error": "Données requises"}), 400

    client = get_claude()
    if not client:
        return jsonify({"error": "Claude API non configuree"}), 500

    scene_number = data.get('scene_number', 1)
    title = data.get('title', '')
    genre = data.get('genre', 'drame')
    language = data.get('language', 'fr')
    description = data.get('description', '')

    lang_map = {"fr": "français", "ar": "arabe", "en": "anglais"}
    lang_name = lang_map.get(language, "français")

    prompt = f"""Génère une scène cinématographique professionnelle en {lang_name} :

Film : {title} ({genre})
Scène {scene_number} : {description}

Inclure :
- Description visuelle détaillée
- Dialogues naturels et expressifs
- Indications de mise en scène
- Ambiance sonore et musicale

Écris la scène complète de 200-300 mots."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        scene = message.content[0].text
        return jsonify({
            "success": True,
            "scene_number": scene_number,
            "title": title,
            "scene": scene,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scenario_bp.route('/dialogue', methods=['POST', 'OPTIONS'])
@cross_origin()
def generate_dialogue():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data:
        return jsonify({"error": "Données requises"}), 400

    client = get_claude()
    if not client:
        return jsonify({"error": "Claude API non configuree"}), 500

    characters = data.get('characters', [])
    situation = data.get('situation', '')
    language = data.get('language', 'fr')
    tone = data.get('tone', 'dramatique')

    lang_map = {"fr": "français", "ar": "arabe", "en": "anglais"}
    lang_name = lang_map.get(language, "français")

    prompt = f"""Génère un dialogue cinématographique en {lang_name} :

Personnages : {', '.join(characters) if characters else 'deux personnages'}
Situation : {situation}
Ton : {tone}

Écris un dialogue naturel et cinématographique de 10-15 répliques.
Format : PERSONNAGE: réplique"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        dialogue = message.content[0].text
        return jsonify({
            "success": True,
            "dialogue": dialogue,
            "language": language,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500