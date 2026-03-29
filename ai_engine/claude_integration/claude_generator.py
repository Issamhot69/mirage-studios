"""
Mirage Studios — Claude API Integration
Génération de vrais scénarios, dialogues et synopsis via Claude.
"""

import os
import json
import anthropic
from dataclasses import dataclass
from typing import Optional

# ── CONFIGURATION ─────────────────────────────────────────
# Ajoute ta clé ici ou dans la variable d'environnement
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "sk-ant-VOTRE_CLE_ICI")

@dataclass
class ScriptRequest:
    genre: str
    duration_minutes: int
    language: str          # "ar", "fr", "en"
    tone: str
    logline: str           # Description courte de l'histoire
    hero_name: Optional[str] = None
    world_description: Optional[str] = None


class ClaudeScriptGenerator:
    """Génère de vrais scénarios via Claude API."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    def generate_synopsis(self, request: ScriptRequest) -> str:
        """Génère un synopsis complet dans la langue choisie."""
        lang_instruction = {
            "ar": "اكتب باللغة العربية الفصحى",
            "fr": "Écris en français",
            "en": "Write in English",
        }.get(request.language, "Write in French")

        prompt = f"""
{lang_instruction}.

Tu es un scénariste professionnel de cinéma.

Génère un synopsis complet pour ce film :
- Genre : {request.genre}
- Durée : {request.duration_minutes} minutes
- Ton : {request.tone}
- Histoire : {request.logline}
{f"- Héros : {request.hero_name}" if request.hero_name else ""}
{f"- Univers : {request.world_description}" if request.world_description else ""}

Le synopsis doit inclure :
1. La présentation du monde et des personnages
2. L'élément déclencheur
3. Le développement et les obstacles
4. Le climax
5. La résolution

Sois créatif, émotionnel et professionnel.
"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def generate_scene(self, scene_description: str, language: str = "fr") -> str:
        """Génère une scène complète avec dialogues."""
        lang_instruction = {
            "ar": "اكتب باللغة العربية",
            "fr": "Écris en français",
            "en": "Write in English",
        }.get(language, "Write in French")

        prompt = f"""
{lang_instruction}.

Tu es un scénariste professionnel. Écris une scène de cinéma complète au format industrie pour :

{scene_description}

La scène doit inclure :
- L'en-tête de scène (INT/EXT, lieu, moment)
- Les descriptions d'action
- Les dialogues naturels et émotionnels
- Les indications de jeu entre parenthèses

Format professionnel FDX. Maximum 1 page.
"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def generate_dialogue(self, character1: str, character2: str,
                          context: str, language: str = "fr") -> str:
        """Génère un dialogue entre deux personnages."""
        lang_instruction = {
            "ar": "اكتب الحوار باللغة العربية",
            "fr": "Écris le dialogue en français",
            "en": "Write the dialogue in English",
        }.get(language, "Write in French")

        prompt = f"""
{lang_instruction}.

Écris un dialogue cinématographique entre :
- {character1}
- {character2}

Contexte : {context}

Le dialogue doit être :
- Naturel et émotionnel
- Révélateur des personnages
- Avancer l'histoire
- Entre 10 et 20 répliques

Format scénario professionnel.
"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def generate_film_title(self, logline: str, language: str = "ar") -> dict:
        """Génère des titres créatifs pour un film."""
        prompt = f"""
Tu es un directeur créatif de cinéma.

Génère 5 titres créatifs pour ce film : {logline}

Donne les titres en arabe, français et anglais.
Format JSON :
{{
  "titres": [
    {{"ar": "...", "fr": "...", "en": "..."}},
    ...
  ]
}}

Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire.
"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        try:
            return json.loads(message.content[0].text)
        except Exception:
            return {"titres": [{"ar": "نور وظلام", "fr": "Lumière et Ténèbres", "en": "Light and Darkness"}]}

    def generate_ad_script(self, brand: str, product: str,
                           duration_seconds: int, language: str = "fr") -> str:
        """Génère un script publicitaire professionnel."""
        lang_instruction = {
            "ar": "اكتب باللغة العربية",
            "fr": "Écris en français",
            "en": "Write in English",
        }.get(language, "Write in French")

        prompt = f"""
{lang_instruction}.

Tu es un directeur créatif publicitaire. Écris un script de publicité pour :

- Marque : {brand}
- Produit/Service : {product}
- Durée : {duration_seconds} secondes

Le script doit inclure :
- Scènes numérotées avec durée
- Voix off / dialogues
- Descriptions visuelles
- Call to action final

Style : professionnel, émotionnel, mémorable.
"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text


# ── TEST RAPIDE ───────────────────────────────────────────
if __name__ == "__main__":
    generator = ClaudeScriptGenerator()

    print("🤖 Test Claude API — Mirage Studios")
    print("=" * 50)

    # Test synopsis
    request = ScriptRequest(
        genre="Fantastique épique",
        duration_minutes=180,
        language="ar",
        tone="émotionnel et profond",
        logline="Une guerre entre le Monde de Lumière et le Monde des Ténèbres, deux héros ennemis forcés de coopérer",
        hero_name="ضياء et ظلال",
        world_description="Deux mondes magiques opposés mais d'une même origine"
    )

    print("\n📝 Génération du synopsis...")
    synopsis = generator.generate_synopsis(request)
    print(synopsis)
    print("\n✅ Claude API fonctionne !")