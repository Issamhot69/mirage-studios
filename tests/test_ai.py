"""
Mirage Studios — Tests IA
Tests unitaires pour les modules Script AI, Genre Classifier et Prediction.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai_engine'))

from script_generator.script_ai import ScriptAI, ScriptConfig
from script_generator.genre_classifier import GenreClassifier
from script_generator.dialogue_engine import DialogueEngine, Character
from prediction.success_predictor import SuccessPredictor, ProjectFeatures
from prediction.audience_analyzer import AudienceAnalyzer


class TestScriptAI(unittest.TestCase):
    def setUp(self):
        self.ai = ScriptAI()

    def test_generate_script_fantastique(self):
        cfg = ScriptConfig(genre="fantastique", duration_minutes=90, tone="epic")
        result = self.ai.generate_script(cfg)
        self.assertEqual(result["genre"], "fantastique")
        self.assertEqual(result["duration"], 90)
        self.assertIn("acts", result)
        self.assertEqual(len(result["acts"]), 3)

    def test_generate_script_thriller(self):
        cfg = ScriptConfig(genre="thriller", duration_minutes=110, tone="dark")
        result = self.ai.generate_script(cfg)
        self.assertEqual(result["genre"], "thriller")

    def test_acts_duration(self):
        cfg = ScriptConfig(genre="drame", duration_minutes=90, tone="sad")
        result = self.ai.generate_script(cfg)
        for act in result["acts"]:
            self.assertEqual(act["duration"], 30)

    def test_build_prompt_contains_duration(self):
        cfg = ScriptConfig(genre="comedie", duration_minutes=85, tone="comedy")
        prompt = self.ai._build_prompt(cfg)
        self.assertIn("85", prompt)


class TestGenreClassifier(unittest.TestCase):
    def setUp(self):
        self.clf = GenreClassifier()

    def test_classify_fantastique(self):
        text = "Un sorcier découvre un artefact magique dans un royaume lointain."
        genre, conf = self.clf.classify(text)
        self.assertEqual(genre, "fantastique")
        self.assertGreater(conf, 0)

    def test_classify_thriller(self):
        text = "Le suspect fuit l'enquêteur à travers le complot."
        genre, conf = self.clf.classify(text)
        self.assertEqual(genre, "thriller")

    def test_classify_all_returns_all_genres(self):
        text = "Une histoire quelconque."
        scores = self.clf.classify_all(text)
        self.assertEqual(set(scores.keys()), {"fantastique", "thriller", "drame", "comedie", "historique"})

    def test_all_scores_between_0_and_1(self):
        text = "Dragon magie guerre famille farce révolution suspect."
        scores = self.clf.classify_all(text)
        for score in scores.values():
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 1)


class TestDialogueEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DialogueEngine()
        self.engine.add_character(Character("Aelion", "hero", "poetic"))
        self.engine.add_character(Character("Morvar", "villain", "terse"))

    def test_generate_exchange_count(self):
        exchange = self.engine.generate_exchange("Combat final", turns=4)
        self.assertEqual(len(exchange), 4)

    def test_characters_alternate(self):
        exchange = self.engine.generate_exchange("Scène test", turns=4)
        self.assertEqual(exchange[0].character, "Aelion")
        self.assertEqual(exchange[1].character, "Morvar")

    def test_export_format_not_empty(self):
        self.engine.generate_exchange("Contexte")
        output = self.engine.export_script_format()
        self.assertGreater(len(output), 0)
        self.assertIn("AELION", output)


class TestSuccessPredictor(unittest.TestCase):
    def setUp(self):
        self.predictor = SuccessPredictor()
        self.features = ProjectFeatures(
            genre="fantastique", budget_millions=80.0, director_score=7.5,
            cast_score=8.0, has_franchise=True, target_demographic="18-40",
            release_season="summer", marketing_budget_ratio=0.35, runtime_minutes=128
        )

    def test_prediction_returns_result(self):
        result = self.predictor.predict("Test Film", self.features)
        self.assertEqual(result.project_name, "Test Film")
        self.assertGreater(result.box_office_mid, 0)

    def test_box_office_range_coherent(self):
        result = self.predictor.predict("Film A", self.features)
        self.assertLess(result.box_office_low, result.box_office_mid)
        self.assertLess(result.box_office_mid, result.box_office_high)

    def test_risk_level_values(self):
        result = self.predictor.predict("Film B", self.features)
        self.assertIn(result.risk_level, ["low", "medium", "high"])

    def test_franchise_bonus(self):
        with_franchise = ProjectFeatures(
            genre="action", budget_millions=50.0, director_score=6.0, cast_score=7.0,
            has_franchise=True, target_demographic="25-40", release_season="summer",
            marketing_budget_ratio=0.3, runtime_minutes=110
        )
        without_franchise = ProjectFeatures(**{**with_franchise.__dict__, "has_franchise": False})
        r1 = self.predictor.predict("F1", with_franchise)
        r2 = self.predictor.predict("F2", without_franchise)
        self.assertGreater(r1.box_office_mid, r2.box_office_mid)


class TestAudienceAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = AudienceAnalyzer()

    def test_analyze_returns_report(self):
        report = self.analyzer.analyze("fantastique", "18-25", 80.0)
        self.assertIsNotNone(report.primary_segment)
        self.assertGreater(report.total_addressable_market, 0)

    def test_marketing_channels_sum_to_one(self):
        report = self.analyzer.analyze("thriller", "25-40", 50.0)
        total = sum(report.marketing_channels.values())
        self.assertAlmostEqual(total, 1.0, places=5)

    def test_secondary_segments_different_from_primary(self):
        report = self.analyzer.analyze("comedie", "family", 30.0)
        primary_name = report.primary_segment.name
        for seg in report.secondary_segments:
            self.assertNotEqual(seg.name, primary_name)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [TestScriptAI, TestGenreClassifier, TestDialogueEngine, TestSuccessPredictor, TestAudienceAnalyzer]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    exit(0 if result.wasSuccessful() else 1)
