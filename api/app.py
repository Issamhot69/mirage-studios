import sys
sys.path.insert(0, r'C:\mirage_studios\ai_engine\claude_integration')
sys.path.insert(0, r'C:\mirage_studios\ai_engine\voice_dubbing')
sys.path.insert(0, r'C:\mirage_studios\ai_engine')
sys.path.insert(0, r'C:\mirage_studios\api')

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from routes import register_routes
from routes_claude import claude_bp
from routes_auth_users import auth_users_bp
from routes_replicate import replicate_bp
from routes_music import music_bp
from routes_casting import casting_bp
from routes_avatar import avatar_bp
from routes_payment import payment_bp
from auth import init_auth
import json
import os
import uuid


def create_app(config_path: str = "config.json") -> Flask:
    app = Flask(__name__, template_folder="../web/templates", static_folder="../web/static")

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    if os.path.exists(config_path):
        with open(config_path) as f:
            cfg = json.load(f)
        app.config.update(cfg)

    app.config.setdefault("SECRET_KEY", os.environ.get("SECRET_KEY", "mirage-dev-key"))
    app.config.setdefault("DEBUG", os.environ.get("DEBUG", "false").lower() == "true")
    app.config.setdefault("VERSION", "2.0.0")

    # Claude API
    claude_key = app.config.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")
    if claude_key and claude_key != "sk-ant-VOTRE_CLE_ICI":
        os.environ["ANTHROPIC_API_KEY"] = claude_key
        print(f"[Claude] OK Cle API configuree")
    else:
        print(f"[Claude] Mode demo")

    # Replicate
    replicate_token = app.config.get("REPLICATE_API_TOKEN") or os.environ.get("REPLICATE_API_TOKEN", "")
    if replicate_token:
        os.environ["REPLICATE_API_TOKEN"] = replicate_token
        print(f"[Replicate] OK Token configure")
    else:
        print(f"[Replicate] Token manquant")

    # D-ID
    did_key = app.config.get("DID_API_KEY") or os.environ.get("DID_API_KEY", "")
    if did_key:
        os.environ["DID_API_KEY"] = did_key
        print(f"[D-ID] OK Cle API configuree")
    else:
        print(f"[D-ID] Mode demo")

    # Stripe
    stripe_secret = app.config.get("STRIPE_SECRET_KEY") or os.environ.get("STRIPE_SECRET_KEY", "")
    stripe_public = app.config.get("STRIPE_PUBLIC_KEY") or os.environ.get("STRIPE_PUBLIC_KEY", "")
    if stripe_secret:
        os.environ["STRIPE_SECRET_KEY"] = stripe_secret
        os.environ["STRIPE_PUBLIC_KEY"] = stripe_public
        print(f"[Stripe] OK Paiement configure")
    else:
        print(f"[Stripe] Mode demo")

    CORS(app, origins=app.config.get("ALLOWED_ORIGINS", [
        "http://localhost:3001",
        "http://localhost:5001",
        "http://localhost:5500"
    ]))

    init_auth(app)
    register_routes(app)

    app.register_blueprint(claude_bp)
    print(f"[Claude] Routes IA - /api/claude/*")

    app.register_blueprint(auth_users_bp)
    print(f"[Auth Users] Routes login - /api/users/*")

    app.register_blueprint(replicate_bp)
    print(f"[Replicate] Routes video - /api/video/*")

    app.register_blueprint(music_bp)
    print(f"[Music] Routes musique - /api/music/*")

    app.register_blueprint(casting_bp)
    print(f"[Casting] Routes casting - /api/casting/*")

    app.register_blueprint(avatar_bp)
    print(f"[Avatar] Routes avatar - /api/avatar/*")

    app.register_blueprint(payment_bp)
    print(f"[Stripe] Routes paiement - /api/payment/*")

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/api/upload/photo', methods=['POST'])
    def upload_photo():
        if 'photo' not in request.files:
            return jsonify({"error": "Aucune photo envoyee"}), 400
        file = request.files['photo']
        if file.filename == '':
            return jsonify({"error": "Fichier vide"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "Format non supporte. JPG, PNG ou WEBP"}), 400
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        photo_url = f"http://localhost:5001/api/upload/serve/{filename}"
        print(f"[Upload] Photo sauvegardee : {filename}")
        return jsonify({
            "success": True,
            "filename": filename,
            "photo_url": photo_url,
            "message": "Photo uploadee avec succes !"
        })

    @app.route('/api/upload/serve/<filename>', methods=['GET'])
    def serve_photo(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route("/health")
    def health():
        return {
            "status": "ok",
            "version": app.config["VERSION"],
            "service": "mirage-studios-api",
            "claude_api": "ready" if os.environ.get("ANTHROPIC_API_KEY") else "missing",
            "replicate": "ready" if os.environ.get("REPLICATE_API_TOKEN") else "missing",
            "did_avatar": "ready" if os.environ.get("DID_API_KEY") else "missing",
            "stripe": "ready" if os.environ.get("STRIPE_SECRET_KEY") else "missing",
            "casting": "ready",
            "music": "ready",
            "upload": "ready",
        }

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5001))
    print(f"[Mirage API] Running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])