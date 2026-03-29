"""
Mirage Studios — Tests API
Tests d'intégration pour les endpoints REST Flask.
"""

import unittest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

# Mock Flask app pour les tests
os.environ.setdefault("SECRET_KEY", "test-secret-key")

try:
    from app import create_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


@unittest.skipUnless(FLASK_AVAILABLE, "Flask non disponible")
class TestHealthEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_health_ok(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "ok")

    def test_health_has_version(self):
        res = self.client.get("/health")
        data = json.loads(res.data)
        self.assertIn("version", data)


@unittest.skipUnless(FLASK_AVAILABLE, "Flask non disponible")
class TestScriptEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_generate_script_success(self):
        payload = {"genre": "fantastique", "duration_minutes": 90, "tone": "epic"}
        res = self.client.post("/api/script/generate",
                               data=json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("script", data)

    def test_generate_script_missing_fields(self):
        payload = {"genre": "fantastique"}
        res = self.client.post("/api/script/generate",
                               data=json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_classify_genre(self):
        payload = {"text": "Un sorcier et son dragon dans un royaume enchanté."}
        res = self.client.post("/api/script/classify",
                               data=json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("genre", data)
        self.assertIn("confidence", data)
        self.assertIn("all_scores", data)

    def test_classify_no_text(self):
        res = self.client.post("/api/script/classify",
                               data=json.dumps({}),
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)


@unittest.skipUnless(FLASK_AVAILABLE, "Flask non disponible")
class TestPredictionEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_get_prediction(self):
        res = self.client.get("/api/prediction/p001")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("roi_estimate", data)
        self.assertIn("box_office_mid", data)

    def test_prediction_values_positive(self):
        res = self.client.get("/api/prediction/test_project")
        data = json.loads(res.data)
        self.assertGreater(data["box_office_mid"], 0)


@unittest.skipUnless(FLASK_AVAILABLE, "Flask non disponible")
class TestProjectsEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_list_projects(self):
        res = self.client.get("/api/projects/")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("projects", data)
        self.assertIsInstance(data["projects"], list)

    def test_get_project_existing(self):
        res = self.client.get("/api/projects/p001")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["id"], "p001")

    def test_get_project_not_found(self):
        res = self.client.get("/api/projects/nonexistent")
        self.assertEqual(res.status_code, 404)


@unittest.skipUnless(FLASK_AVAILABLE, "Flask non disponible")
class TestAuthEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["API_KEYS"] = {"test-key": "user", "admin-key": "admin"}
        self.client = self.app.test_client()

    def test_get_token_valid_key(self):
        res = self.client.post("/api/auth/token",
                               data=json.dumps({"api_key": "test-key"}),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("token", data)

    def test_get_token_invalid_key(self):
        res = self.client.post("/api/auth/token",
                               data=json.dumps({"api_key": "invalid-key"}),
                               content_type="application/json")
        self.assertEqual(res.status_code, 401)

    def test_verify_without_token(self):
        res = self.client.get("/api/auth/verify")
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
