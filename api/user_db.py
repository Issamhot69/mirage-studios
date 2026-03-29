"""
Mirage Studios — User Database
Gestion des utilisateurs avec SQLite (sans installation supplémentaire).
"""

import sqlite3
import hashlib
import os
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'users.db')


@dataclass
class User:
    id: int
    email: str
    name: str
    role: str           # "user", "producer", "admin"
    provider: str       # "email", "google"
    created_at: str
    avatar: Optional[str] = None
    plan: str = "free"  # "free", "pro", "studio"


class UserDB:
    """Base de données SQLite pour les utilisateurs."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Crée les tables si elles n'existent pas."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    password_hash TEXT,
                    role TEXT DEFAULT 'user',
                    provider TEXT DEFAULT 'email',
                    plan TEXT DEFAULT 'free',
                    avatar TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_login TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    genre TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            conn.commit()
        print(f"[UserDB] Base de données initialisée : {self.db_path}")

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, email: str, name: str, password: str,
                    role: str = "user", provider: str = "email") -> Optional[User]:
        """Crée un nouvel utilisateur."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "INSERT INTO users (email, name, password_hash, role, provider) VALUES (?, ?, ?, ?, ?)",
                    (email, name, self._hash_password(password), role, provider)
                )
                conn.commit()
                return self.get_user_by_id(cursor.lastrowid)
        except sqlite3.IntegrityError:
            return None  # Email déjà utilisé

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur par email/mot de passe."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ? AND password_hash = ? AND is_active = 1",
                (email, self._hash_password(password))
            ).fetchone()
            if row:
                conn.execute("UPDATE users SET last_login = ? WHERE id = ?",
                             (datetime.now().isoformat(), row[0]))
                conn.commit()
                return self._row_to_user(row)
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            return self._row_to_user(row) if row else None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return self._row_to_user(row) if row else None

    def create_or_get_google_user(self, email: str, name: str, avatar: str = None) -> User:
        """Crée ou récupère un utilisateur Google."""
        user = self.get_user_by_email(email)
        if user:
            return user
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO users (email, name, password_hash, provider, avatar) VALUES (?, ?, ?, ?, ?)",
                (email, name, "", "google", avatar)
            )
            conn.commit()
            return self.get_user_by_id(cursor.lastrowid)

    def get_user_projects(self, user_id: int) -> list:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [{"id": r[0], "name": r[2], "genre": r[3], "status": r[4], "created_at": r[5]} for r in rows]

    def _row_to_user(self, row) -> User:
        return User(
            id=row[0], email=row[1], name=row[2],
            role=row[4], provider=row[5], plan=row[6],
            avatar=row[7], created_at=row[8]
        )


# Instance globale
db = UserDB()

# Créer un admin par défaut
if not db.get_user_by_email("admin@mirage-studios.com"):
    db.create_user("admin@mirage-studios.com", "Admin Mirage", "admin2025", role="admin")
    print("[UserDB] Admin créé : admin@mirage-studios.com / admin2025")
