# Modèles IA — Mirage Studios

## Modèles en production

| Modèle | Version | Usage | Taille | Performance |
|--------|---------|-------|--------|-------------|
| claude-sonnet-4 | 20250514 | Génération scénarios | API | ★★★★★ |
| stable-diffusion-xl | 1.0 | Génération images VFX | 6.9GB | ★★★★☆ |
| elevenlabs-multilingual | v3 | TTS doublage | API | ★★★★★ |
| mirage-genre-classifier | v2 | Classification genre | 45MB | ★★★★☆ |
| mirage-success-predictor | v2.1 | Prédiction commerciale | 120MB | ★★★★☆ |
| deepl-translator | API | Traduction dialogues | API | ★★★★★ |

---

## Modèles en développement

| Modèle | Statut | ETA |
|--------|--------|-----|
| mirage-lip-sync-v1 | Beta | Q3 2025 |
| scene-composer-xl | Alpha | Q4 2025 |
| emotion-tts-v2 | En cours | Q2 2025 |

---

## Chemins de stockage

```
data/models/
├── genre_classifier_v2.pkl      # scikit-learn pipeline
├── success_predictor_v2.1.pkl   # Random Forest + features
├── sd_xl_base_1.0/              # Stable Diffusion weights
│   ├── model_index.json
│   └── unet/
└── embeddings/
    └── cinema_corpus_v1.npy     # Embeddings scénarios
```

---

## Entraînement des modèles custom

### Genre Classifier
- Corpus : 12 000 synopsis (IMDB, Allocine, TMDB)
- Features : TF-IDF + embeddings sémantiques
- Accuracy : 87% sur validation set

### Success Predictor
- Dataset : 8 500 films (2000–2024)
- Features : 23 variables (budget, casting, genre, saison...)
- MAE box-office : ±15% (médiane)
- Données source : Box Office Mojo, The Numbers

---

## Notes de mise à jour

- **v2.1 Success Predictor** (Mars 2025) : Ajout variable `sequel_number`, amélioration ROI estimation (+8% précision)
- **v2 Genre Classifier** (Janvier 2025) : Support genre "animation", refactoring pipeline
