# ◈ Mirage Studios — Technologie IA

> Pipeline complet de production cinématographique automatisée par intelligence artificielle.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

---

## Vue d'ensemble

Mirage Studios est une plateforme Python qui automatise les quatre piliers de la production cinématographique via l'IA :

| Module | Technologie | Fonction |
|--------|-------------|----------|
| **Script AI** | Claude API + NLP | Génération & analyse de scénarios |
| **VFX Generator** | Stable Diffusion + Python | Effets visuels automatisés |
| **Voice Dubbing** | ElevenLabs + DeepL | Doublage multilingue (9 langues) |
| **Prediction ML** | scikit-learn | Analyse du potentiel commercial |

---

## Installation rapide

```bash
# Cloner le projet
git clone https://github.com/mirage-studios/mirage-ai.git
cd mirage_studios

# Environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate

# Dépendances
pip install -r requirements.txt

# Configuration
cp config.json.example config.json
# Éditer config.json avec vos clés API

# Lancer l'API
python api/app.py
```

---

## Structure du projet

```
mirage_studios/
├── ai_engine/              # Moteurs IA
│   ├── script_generator/   # Scénarios (ScriptAI, GenreClassifier, DialogueEngine)
│   ├── vfx_generator/      # Effets visuels (VFXPipeline, StableDiffusion, SceneRenderer)
│   ├── voice_dubbing/      # Doublage (TTSEngine, MultilingualTranslator)
│   └── prediction/         # Prédiction (SuccessPredictor, AudienceAnalyzer)
├── genres/                 # Modules spécialisés par genre
│   ├── fantastique/        # Système de magie, mondes
│   ├── historique/         # Recherche d'époque, timelines
│   ├── thriller/           # Arc de tension
│   ├── drame/              # Arc émotionnel
│   └── comedie/            # Structure comique
├── web/                    # Interface utilisateur
│   ├── index.html          # Page d'accueil
│   ├── style.css           # Design system sombre
│   ├── templates/          # Dashboard, vue projet
│   └── static/main.js      # Interactions UI
├── data/                   # Données de référence
│   ├── scripts/            # Scénarios exemples
│   ├── movies_db/          # Base de données films (12 références)
│   └── models/             # Modèles ML locaux
├── api/                    # API REST Flask
│   ├── app.py              # Application principale
│   ├── routes.py           # Endpoints (script, vfx, dubbing, prediction)
│   └── auth.py             # JWT Authentication
├── tests/                  # Tests unitaires & intégration
├── requirements.txt
└── config.json
```

---

## Utilisation rapide

### Générer un scénario

```python
from ai_engine.script_generator.script_ai import ScriptAI, ScriptConfig

ai = ScriptAI(model="claude-sonnet-4-20250514")
script = ai.generate_script(ScriptConfig(
    genre="fantastique",
    duration_minutes=90,
    tone="epic",
    language="fr"
))
```

### Classifier un genre

```python
from ai_engine.script_generator.genre_classifier import GenreClassifier

clf = GenreClassifier()
genre, confidence = clf.classify("Un sorcier découvre un artefact magique.")
# → ("fantastique", 0.50)
```

### Prédire le succès commercial

```python
from ai_engine.prediction.success_predictor import SuccessPredictor, ProjectFeatures

predictor = SuccessPredictor()
result = predictor.predict("Mon Film", ProjectFeatures(
    genre="fantastique", budget_millions=80.0,
    director_score=7.5, cast_score=8.0,
    has_franchise=True, release_season="summer",
    target_demographic="18-40",
    marketing_budget_ratio=0.35, runtime_minutes=128
))
# result.box_office_mid → 280.0 M€
# result.roi_estimate   → +250%
```

### Pipeline VFX

```python
from ai_engine.vfx_generator.vfx_pipeline import VFXPipeline, VFXShot, VFXType

pipeline = VFXPipeline("Mon Projet")
pipeline.add_shot(VFXShot("S01", "Scène d'ouverture", VFXType.BACKGROUND, 120))
pipeline.process_all()
```

---

## API REST

Démarrer le serveur : `python api/app.py`

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `GET /health` | GET | Santé du service |
| `POST /api/script/generate` | POST | Générer un scénario |
| `POST /api/script/classify` | POST | Classifier un genre |
| `GET /api/prediction/{id}` | GET | Prédiction commerciale |
| `GET /api/projects/` | GET | Liste des projets |
| `POST /api/auth/token` | POST | Obtenir un JWT |

---

## Tests

```bash
# Tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=ai_engine --cov-report=html

# Tests IA seulement
python tests/test_ai.py

# Tests API seulement
python tests/test_api.py
```

---

## Configuration

Éditer `config.json` :

```json
{
  "AI_MODELS": {
    "script": "claude-sonnet-4-20250514",
    "tts": "elevenlabs-v3"
  },
  "VFX": {
    "default_resolution": [1920, 1080],
    "fps": 24
  }
}
```

Variables d'environnement :

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export ELEVENLABS_API_KEY="..."
export DEEPL_API_KEY="..."
export SECRET_KEY="votre-secret-jwt"
```

---

## Genres supportés

- 🧙 **Fantastique** — Système de magie, world-building, créatures
- 🕵️ **Thriller** — Arc de tension, paranoïa, compte à rebours
- 🎭 **Drame** — Arc émotionnel, développement personnages
- 😄 **Comédie** — Structure gags, running gags, callbacks
- ⚔️ **Historique** — Recherche d'époque, timelines, costumes

---

## Roadmap

- [ ] Module d'animation IA (Q2 2025)
- [ ] Lip-sync automatique (Q3 2025)
- [ ] Export Final Draft natif (Q3 2025)
- [ ] Interface collaborative multi-utilisateurs (Q4 2025)
- [ ] Support 8K VFX (2026)

---

## Licence

MIT — Mirage Studios © 2025
