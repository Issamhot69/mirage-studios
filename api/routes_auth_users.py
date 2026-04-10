"""
Mirage Studios — Routes d'authentification
Login, Register, Google OAuth, Logout.
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

auth_users_bp = Blueprint('auth_users', __name__, url_prefix='/api/users')


def get_db():
    from user_db import db
    return db


def generate_token(user_id: int, email: str, role: str) -> str:
    import hmac, hashlib, base64, time
    payload = json.dumps({"id": user_id, "email": email, "role": role, "exp": time.time() + 86400})
    secret = os.environ.get("SECRET_KEY", "mirage-dev-key")
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token = base64.b64encode(payload.encode()).decode() + "." + sig
    return token


@auth_users_bp.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin()
def register():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data:
        return jsonify({"error": "Données requises"}), 400

    required = ['email', 'name', 'password']
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Champs manquants : {missing}"}), 400

    if len(data['password']) < 6:
        return jsonify({"error": "Mot de passe trop court (min 6 caractères)"}), 400

    db = get_db()
    user = db.create_user(
        email=data['email'].lower().strip(),
        name=data['name'].strip(),
        password=data['password']
    )

    if not user:
        return jsonify({"error": "Email déjà utilisé"}), 409

    token = generate_token(user.id, user.email, user.role)
    return jsonify({
        "success": True,
        "message": "Compte créé avec succès !",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "plan": user.plan,
            "avatar": user.avatar,
            "credits": user.credits,
        }
    }), 201


@auth_users_bp.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin()
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    db = get_db()
    user = db.authenticate(data['email'].lower().strip(), data['password'])

    if not user:
        return jsonify({"error": "Email ou mot de passe incorrect"}), 401

    token = generate_token(user.id, user.email, user.role)
    return jsonify({
        "success": True,
        "message": f"Bienvenue {user.name} !",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "plan": user.plan,
            "avatar": user.avatar,
        }
    })


@auth_users_bp.route('/google', methods=['POST', 'OPTIONS'])
@cross_origin()
def google_login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({"error": "Données Google manquantes"}), 400

    db = get_db()
    user = db.create_or_get_google_user(
        email=data['email'],
        name=data.get('name', data['email'].split('@')[0]),
        avatar=data.get('avatar')
    )

    token = generate_token(user.id, user.email, user.role)
    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "plan": user.plan,
            "avatar": user.avatar,
        }
    })


@auth_users_bp.route('/me', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_me():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return jsonify({"error": "Token manquant"}), 401

    try:
        import base64
        token = auth[7:]
        payload_b64 = token.split('.')[0]
        padding = 4 - len(payload_b64) % 4
        payload = json.loads(base64.b64decode(payload_b64 + '=' * padding))
        db = get_db()
        user = db.get_user_by_id(payload['id'])
        if not user:
            return jsonify({"error": "Utilisateur introuvable"}), 404
        projects = db.get_user_projects(user.id)
        return jsonify({
            "user": {"id": user.id, "email": user.email, "name": user.name,
                     "role": user.role, "plan": user.plan, "avatar": user.avatar},
            "projects": projects,
            "stats": {"total_projects": len(projects)}
        })
    except Exception as e:
        return jsonify({"error": "Token invalide"}), 401


@auth_users_bp.route('/logout', methods=['POST', 'OPTIONS'])
@cross_origin()
def logout():
    return jsonify({"success": True, "message": "Déconnecté avec succès"})