"""
Mirage Studios — Gestion des clés API
Permet aux développeurs de créer et gérer leurs clés API.
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import sys
import sqlite3
import secrets
import hashlib
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

apikeys_bp = Blueprint('apikeys', __name__, url_prefix='/api/keys')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'users.db')


def init_apikeys_db():
    """Crée la table des clés API."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                key_prefix TEXT NOT NULL,
                name TEXT NOT NULL,
                project TEXT DEFAULT '',
                credits INTEGER DEFAULT 100,
                requests_count INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_used TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()


def generate_api_key() -> tuple:
    """Génère une clé API unique."""
    raw = secrets.token_hex(32)
    key = f"mk_{raw}"
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    key_prefix = key[:12]
    return key, key_hash, key_prefix


def validate_api_key(key: str) -> dict:
    """Valide une clé API et retourne les infos."""
    if not key or not key.startswith("mk_"):
        return {"valid": False, "error": "Format de clé invalide"}

    key_hash = hashlib.sha256(key.encode()).hexdigest()

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT id, user_id, name, credits, is_active FROM api_keys WHERE key_hash = ?",
            (key_hash,)
        ).fetchone()

        if not row:
            return {"valid": False, "error": "Clé API introuvable"}

        if not row[4]:
            return {"valid": False, "error": "Clé API désactivée"}

        if row[3] <= 0:
            return {"valid": False, "error": "Crédits insuffisants"}

        # Mettre à jour last_used et requests_count
        conn.execute(
            "UPDATE api_keys SET last_used = ?, requests_count = requests_count + 1 WHERE id = ?",
            (datetime.now().isoformat(), row[0])
        )
        conn.commit()

        return {
            "valid": True,
            "key_id": row[0],
            "user_id": row[1],
            "name": row[2],
            "credits": row[3],
        }


def get_user_from_token(token: str) -> dict:
    """Récupère l'utilisateur depuis le token JWT."""
    try:
        import base64
        import json
        payload_b64 = token.split('.')[0]
        padding = 4 - len(payload_b64) % 4
        payload = json.loads(base64.b64decode(payload_b64 + '=' * padding))
        return payload
    except:
        return None


# Initialiser la DB
init_apikeys_db()


@apikeys_bp.route('/create', methods=['POST', 'OPTIONS'])
@cross_origin()
def create_key():
    """Crée une nouvelle clé API."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return jsonify({"error": "Token requis"}), 401

    user = get_user_from_token(auth[7:])
    if not user:
        return jsonify({"error": "Token invalide"}), 401

    data = request.get_json() or {}
    name = data.get('name', 'Ma clé API')
    project = data.get('project', '')
    credits = int(data.get('credits', 100))

    key, key_hash, key_prefix = generate_api_key()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO api_keys (user_id, key_hash, key_prefix, name, project, credits) VALUES (?, ?, ?, ?, ?, ?)",
            (user['id'], key_hash, key_prefix, name, project, credits)
        )
        conn.commit()

    return jsonify({
        "success": True,
        "api_key": key,
        "key_prefix": key_prefix,
        "name": name,
        "project": project,
        "credits": credits,
        "message": "⚠️ Sauvegardez cette clé maintenant — elle ne sera plus affichée !",
        "usage": {
            "header": f"Authorization: Bearer {key}",
            "example": f"curl -H 'Authorization: Bearer {key}' https://focused-adaptation-production-689e.up.railway.app/api/video/generate"
        }
    }), 201


@apikeys_bp.route('/list', methods=['GET'])
@cross_origin()
def list_keys():
    """Liste les clés API de l'utilisateur."""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return jsonify({"error": "Token requis"}), 401

    user = get_user_from_token(auth[7:])
    if not user:
        return jsonify({"error": "Token invalide"}), 401

    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, key_prefix, name, project, credits, requests_count, is_active, created_at, last_used FROM api_keys WHERE user_id = ? ORDER BY created_at DESC",
            (user['id'],)
        ).fetchall()

    keys = [
        {
            "id": r[0],
            "key_prefix": r[1] + "...",
            "name": r[2],
            "project": r[3],
            "credits": r[4],
            "requests_count": r[5],
            "is_active": bool(r[6]),
            "created_at": r[7],
            "last_used": r[8],
        }
        for r in rows
    ]

    return jsonify({"keys": keys, "total": len(keys)})


@apikeys_bp.route('/validate', methods=['POST', 'OPTIONS'])
@cross_origin()
def validate_key():
    """Valide une clé API (endpoint public)."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json() or {}
    key = data.get('api_key', '')

    if not key:
        auth = request.headers.get('Authorization', '')
        if auth.startswith('Bearer mk_'):
            key = auth[7:]

    result = validate_api_key(key)
    return jsonify(result)


@apikeys_bp.route('/revoke/<int:key_id>', methods=['DELETE', 'OPTIONS'])
@cross_origin()
def revoke_key(key_id):
    """Révoque une clé API."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return jsonify({"error": "Token requis"}), 401

    user = get_user_from_token(auth[7:])
    if not user:
        return jsonify({"error": "Token invalide"}), 401

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE api_keys SET is_active = 0 WHERE id = ? AND user_id = ?",
            (key_id, user['id'])
        )
        conn.commit()

    return jsonify({"success": True, "message": "Clé révoquée"})


@apikeys_bp.route('/usage/<int:key_id>', methods=['GET'])
@cross_origin()
def key_usage(key_id):
    """Statistiques d'utilisation d'une clé."""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return jsonify({"error": "Token requis"}), 401

    user = get_user_from_token(auth[7:])
    if not user:
        return jsonify({"error": "Token invalide"}), 401

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT key_prefix, name, project, credits, requests_count, created_at, last_used FROM api_keys WHERE id = ? AND user_id = ?",
            (key_id, user['id'])
        ).fetchone()

    if not row:
        return jsonify({"error": "Clé introuvable"}), 404

    return jsonify({
        "key_prefix": row[0] + "...",
        "name": row[1],
        "project": row[2],
        "credits_remaining": row[3],
        "total_requests": row[4],
        "created_at": row[5],
        "last_used": row[6],
    })