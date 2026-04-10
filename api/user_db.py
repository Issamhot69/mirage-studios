"""
Mirage Studios — User Database avec système de crédits
"""

import sqlite3
import hashlib
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'users.db')

# Plans disponibles
PLANS = {
    "free":    {"credits": 10,   "price": 0,    "label": "Free"},
    "starter": {"credits": 100,  "price": 29,   "label": "Starter"},
    "pro":     {"credits": 500,  "price": 99,   "label": "Pro"},
    "studio":  {"credits": 2000, "price": 299,  "label": "Studio"},
}

# Coût en crédits par action
CREDIT_COSTS = {
    "video_5s":     10,
    "video_10s":    20,
    "scenario":     5,
    "avatar":       15,
    "music_30s":    3,
    "casting":      2,
}


@dataclass
class User:
    id: int
    email: str
    name: str
    role: str
    provider: str
    created_at: str
    avatar: Optional[str] = None
    plan: str = "free"
    credits: int = 10


class UserDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
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
                    credits INTEGER DEFAULT 10,
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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS credit_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    credits_used INTEGER NOT NULL,
                    credits_before INTEGER NOT NULL,
                    credits_after INTEGER NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            # Ajouter colonne credits si elle n'existe pas
            try:
                conn.execute("ALTER TABLE users ADD COLUMN credits INTEGER DEFAULT 10")
            except:
                pass
            conn.commit()
        print(f"[UserDB] Base de données initialisée")

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, email: str, name: str, password: str,
                    role: str = "user", provider: str = "email") -> Optional[User]:
        try:
            plan = "free"
            credits = PLANS[plan]["credits"]
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "INSERT INTO users (email, name, password_hash, role, provider, plan, credits) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (email, name, self._hash_password(password), role, provider, plan, credits)
                )
                conn.commit()
                return self.get_user_by_id(cursor.lastrowid)
        except sqlite3.IntegrityError:
            return None

    def authenticate(self, email: str, password: str) -> Optional[User]:
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
        user = self.get_user_by_email(email)
        if user:
            return user
        credits = PLANS["free"]["credits"]
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO users (email, name, password_hash, provider, avatar, plan, credits) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (email, name, "", "google", avatar, "free", credits)
            )
            conn.commit()
            return self.get_user_by_id(cursor.lastrowid)

    def get_credits(self, user_id: int) -> int:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT credits FROM users WHERE id = ?", (user_id,)).fetchone()
            return row[0] if row else 0

    def use_credits(self, user_id: int, action: str, description: str = "") -> dict:
        cost = CREDIT_COSTS.get(action, 1)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT credits FROM users WHERE id = ?", (user_id,)).fetchone()
            if not row:
                return {"success": False, "error": "Utilisateur introuvable"}
            current = row[0]
            if current < cost:
                return {"success": False, "error": f"Crédits insuffisants ({current}/{cost})", "credits": current}
            new_credits = current - cost
            conn.execute("UPDATE users SET credits = ? WHERE id = ?", (new_credits, user_id))
            conn.execute(
                "INSERT INTO credit_history (user_id, action, credits_used, credits_before, credits_after, description) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, action, cost, current, new_credits, description)
            )
            conn.commit()
            return {"success": True, "credits_used": cost, "credits_remaining": new_credits}

    def add_credits(self, user_id: int, amount: int, description: str = "Recharge") -> dict:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT credits FROM users WHERE id = ?", (user_id,)).fetchone()
            if not row:
                return {"success": False, "error": "Utilisateur introuvable"}
            current = row[0]
            new_credits = current + amount
            conn.execute("UPDATE users SET credits = ? WHERE id = ?", (new_credits, user_id))
            conn.execute(
                "INSERT INTO credit_history (user_id, action, credits_used, credits_before, credits_after, description) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, "add", -amount, current, new_credits, description)
            )
            conn.commit()
            return {"success": True, "credits_added": amount, "credits_total": new_credits}

    def upgrade_plan(self, user_id: int, plan: str) -> dict:
        if plan not in PLANS:
            return {"success": False, "error": "Plan invalide"}
        plan_data = PLANS[plan]
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE users SET plan = ?, credits = credits + ? WHERE id = ?",
                (plan, plan_data["credits"], user_id)
            )
            conn.commit()
        return {"success": True, "plan": plan, "credits_added": plan_data["credits"]}

    def get_credit_history(self, user_id: int, limit: int = 10) -> list:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT action, credits_used, credits_before, credits_after, description, created_at FROM credit_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            return [{"action": r[0], "credits_used": r[1], "before": r[2], "after": r[3], "description": r[4], "date": r[5]} for r in rows]

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
            credits=row[7] if (len(row) > 7 and row[7] is not None) else 10,
            avatar=row[8] if len(row) > 8 else None,
            created_at=row[9] if len(row) > 9 else ""
        )


db = UserDB()

if not db.get_user_by_email("admin@mirage-studios.com"):
    db.create_user("admin@mirage-studios.com", "Admin Mirage", "admin2025", role="admin")
    db.add_credits(1, 9990, "Credits admin initiaux")
    print("[UserDB] Admin cree")