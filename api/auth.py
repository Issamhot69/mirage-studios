"""
Mirage Studios — Auth Module
JWT Authentication pour l'API Mirage Studios.
"""

import os
import hmac
import hashlib
import base64
import json
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, current_app


def _sign(payload: dict, secret: str) -> str:
    """Génère un token JWT simplifié (HS256)."""
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig_input = f"{header}.{body}"
    sig = hmac.new(secret.encode(), sig_input.encode(), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{sig_input}.{sig_b64}"


def _verify(token: str, secret: str) -> dict | None:
    """Vérifie et décode un token JWT."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_body = f"{parts[0]}.{parts[1]}"
        expected_sig = hmac.new(secret.encode(), header_body.encode(), hashlib.sha256).digest()
        expected_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        if not hmac.compare_digest(expected_b64, parts[2]):
            return None
        padding = 4 - len(parts[1]) % 4
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * padding))
        if payload.get("exp") and datetime.utcnow().timestamp() > payload["exp"]:
            return None
        return payload
    except Exception:
        return None


def generate_token(user_id: str, role: str = "user", expires_hours: int = 24) -> str:
    """Génère un token d'accès pour un utilisateur."""
    secret = os.environ.get("SECRET_KEY", "mirage-dev-key")
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.utcnow().timestamp(),
        "exp": (datetime.utcnow() + timedelta(hours=expires_hours)).timestamp(),
    }
    return _sign(payload, secret)


def require_auth(f):
    """Décorateur : protège une route par JWT."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token manquant"}), 401
        token = auth_header[7:]
        secret = current_app.config.get("SECRET_KEY", "mirage-dev-key")
        payload = _verify(token, secret)
        if not payload:
            return jsonify({"error": "Token invalide ou expiré"}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated


def require_role(role: str):
    """Décorateur : vérifie le rôle de l'utilisateur."""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            if request.user.get("role") != role:
                return jsonify({"error": "Permissions insuffisantes"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def init_auth(app):
    """Initialise le module d'authentification."""
    @app.route("/api/auth/token", methods=["POST"])
    def get_token():
        data = request.get_json()
        if not data or "api_key" not in data:
            return jsonify({"error": "api_key requis"}), 400
        valid_keys = app.config.get("API_KEYS", {"demo-key": "user", "admin-key": "admin"})
        role = valid_keys.get(data["api_key"])
        if not role:
            return jsonify({"error": "Clé API invalide"}), 401
        token = generate_token(user_id=data["api_key"][:8], role=role)
        return jsonify({"token": token, "expires_in": 86400, "role": role})

    @app.route("/api/auth/verify", methods=["GET"])
    @require_auth
    def verify_token():
        return jsonify({"valid": True, "user": request.user})

    print("[Auth] Module JWT initialisé.")
