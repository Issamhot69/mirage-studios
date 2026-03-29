"""
Mirage Studios — API Routes
Endpoints REST pour tous les modules IA.
"""

from flask import Blueprint, request, jsonify
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai_engine'))

from script_generator.script_ai import ScriptAI, ScriptConfig
from script_generator.genre_classifier import GenreClassifier
from prediction.success_predictor import SuccessPredictor, ProjectFeatures

# ── Blueprints ────────────────────────────────────────────
script_bp = Blueprint('script', __name__, url_prefix='/api/script')
vfx_bp = Blueprint('vfx', __name__, url_prefix='/api/vfx')
dubbing_bp = Blueprint('dubbing', __name__, url_prefix='/api/dubbing')
prediction_bp = Blueprint('prediction', __name__, url_prefix='/api/prediction')
projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

# Module instances
_script_ai = ScriptAI()
_classifier = GenreClassifier()
_predictor = SuccessPredictor()

# ── SCRIPT ────────────────────────────────────────────────
@script_bp.route('/generate', methods=['POST'])
def generate_script():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Données JSON requises"}), 400
    required = ['genre', 'duration_minutes', 'tone']
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Champs manquants : {missing}"}), 400
    config = ScriptConfig(
        genre=data['genre'],
        duration_minutes=int(data['duration_minutes']),
        tone=data['tone'],
        language=data.get('language', 'fr')
    )
    result = _script_ai.generate_script(config)
    return jsonify({"success": True, "script": result})

@script_bp.route('/classify', methods=['POST'])
def classify_genre():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Champ 'text' requis"}), 400
    genre, confidence = _classifier.classify(data['text'])
    all_scores = _classifier.classify_all(data['text'])
    return jsonify({"genre": genre, "confidence": confidence, "all_scores": all_scores})

# ── VFX ───────────────────────────────────────────────────
@vfx_bp.route('/render/<shot_id>', methods=['POST'])
def render_shot(shot_id):
    data = request.get_json() or {}
    return jsonify({
        "success": True,
        "shot_id": shot_id,
        "status": "queued",
        "estimated_seconds": data.get("frames", 120) / 24 * 2,
    })

@vfx_bp.route('/status/<shot_id>', methods=['GET'])
def shot_status(shot_id):
    return jsonify({"shot_id": shot_id, "status": "rendering", "progress": 68})

# ── DUBBING ───────────────────────────────────────────────
@dubbing_bp.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Champ 'text' requis"}), 400
    word_count = len(data['text'].split())
    return jsonify({
        "success": True,
        "duration_seconds": round(word_count / 130 * 60, 1),
        "language": data.get("language", "fr"),
        "voice": data.get("voice", "Narrator_FR"),
        "output": f"audio/synth_{word_count}w.mp3"
    })

@dubbing_bp.route('/languages', methods=['GET'])
def list_languages():
    return jsonify({
        "supported": ["fr", "en", "es", "de", "ar", "ja", "zh", "pt", "it"],
        "count": 9
    })

# ── PREDICTION ────────────────────────────────────────────
@prediction_bp.route('/<project_id>', methods=['GET'])
def get_prediction(project_id):
    features = ProjectFeatures(
        genre="fantastique", budget_millions=80.0, director_score=7.5,
        cast_score=8.0, has_franchise=True, target_demographic="18-40",
        release_season="summer", marketing_budget_ratio=0.35, runtime_minutes=128
    )
    result = _predictor.predict(project_id, features)
    return jsonify(result.__dict__)

@prediction_bp.route('/analyze', methods=['POST'])
def analyze_project():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Données JSON requises"}), 400
    try:
        features = ProjectFeatures(**{k: data[k] for k in ProjectFeatures.__dataclass_fields__ if k in data})
        result = _predictor.predict(data.get("name", "Projet"), features)
        return jsonify(result.__dict__)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ── PROJECTS ──────────────────────────────────────────────
MOCK_PROJECTS = [
    {"id": "p001", "name": "Mirage — L'Éveil", "genre": "fantastique", "status": "active", "progress": 68},
    {"id": "p002", "name": "Signal Zéro", "genre": "thriller", "status": "active", "progress": 45},
    {"id": "p003", "name": "La Dernière Noblesse", "genre": "historique", "status": "review", "progress": 89},
]

@projects_bp.route('/', methods=['GET'])
def list_projects():
    return jsonify({"projects": MOCK_PROJECTS, "total": len(MOCK_PROJECTS)})

@projects_bp.route('/<project_id>', methods=['GET'])
def get_project(project_id):
    project = next((p for p in MOCK_PROJECTS if p['id'] == project_id), None)
    if not project:
        return jsonify({"error": "Projet introuvable"}), 404
    return jsonify(project)


def register_routes(app):
    """Enregistre tous les blueprints dans l'application Flask."""
    for bp in [script_bp, vfx_bp, dubbing_bp, prediction_bp, projects_bp]:
        app.register_blueprint(bp)
    print(f"[API] {len([script_bp, vfx_bp, dubbing_bp, prediction_bp, projects_bp])} blueprints enregistrés.")
