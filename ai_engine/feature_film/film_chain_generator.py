"""
Mirage Studios — Film Chain Generator
Génération automatique d'un long métrage en 6 prompts enchaînés.
Chaque prompt connaît le contexte du précédent.
"""

import os
import json
import time
import anthropic
from dataclasses import dataclass, field
from typing import Optional

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "sk-ant-VOTRE_CLE_ICI")


@dataclass
class FilmProject:
    title_ar: str
    title_fr: str
    genre: str
    duration_minutes: int
    language: str
    logline: str
    hero1: str
    hero2: str
    world1: str
    world2: str
    tone: str


@dataclass
class FilmScript:
    project: FilmProject
    synopsis: str = ""
    act1: str = ""
    act2a: str = ""
    act2b: str = ""
    act3: str = ""
    dialogues: str = ""
    status: dict = field(default_factory=dict)

    def is_complete(self) -> bool:
        return all([self.synopsis, self.act1, self.act2a, self.act2b, self.act3, self.dialogues])

    def progress_percent(self) -> int:
        parts = [self.synopsis, self.act1, self.act2a, self.act2b, self.act3, self.dialogues]
        done = sum(1 for p in parts if p)
        return int(done / len(parts) * 100)

    def export_full_script(self) -> str:
        """Assemble le scénario complet."""
        return f"""
{'='*60}
{self.project.title_ar}
{self.project.title_fr.upper()}
{'='*60}
Langue : {self.project.language} | Durée : {self.project.duration_minutes} min
Genre : {self.project.genre} | Ton : {self.project.tone}
{'='*60}

SYNOPSIS
{'-'*40}
{self.synopsis}

ACTE I — الفصل الأول
{'-'*40}
{self.act1}

ACTE II — PARTIE 1 — الفصل الثاني (١)
{'-'*40}
{self.act2a}

ACTE II — PARTIE 2 — الفصل الثاني (٢)
{'-'*40}
{self.act2b}

ACTE III — الفصل الثالث
{'-'*40}
{self.act3}

DIALOGUES CLÉS — الحوارات الرئيسية
{'-'*40}
{self.dialogues}

{'='*60}
FIN — النهاية
{'='*60}
"""


class FilmChainGenerator:
    """Génère un long métrage complet en 6 prompts enchaînés."""

    STEP_NAMES = {
        1: "📖 Synopsis général",
        2: "🎬 Acte I — Exposition",
        3: "⚡ Acte II Partie 1 — Confrontation",
        4: "🔥 Acte II Partie 2 — Escalade",
        5: "🏆 Acte III — Résolution",
        6: "💬 Dialogues clés",
    }

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"

    def generate_full_film(self, project: FilmProject,
                           on_progress=None) -> FilmScript:
        """Lance la génération complète en 6 étapes."""
        script = FilmScript(project=project)
        print(f"\n🎬 Génération : {project.title_ar} — {project.title_fr}")
        print(f"{'='*50}")

        # PROMPT 1 — Synopsis
        print(f"\n[1/6] {self.STEP_NAMES[1]}...")
        script.synopsis = self._prompt1_synopsis(project)
        script.status["synopsis"] = "done"
        if on_progress: on_progress(1, 6, script.synopsis[:100])
        print(f"✅ Synopsis généré ({len(script.synopsis)} caractères)")
        time.sleep(1)

        # PROMPT 2 — Acte I
        print(f"\n[2/6] {self.STEP_NAMES[2]}...")
        script.act1 = self._prompt2_act1(project, script.synopsis)
        script.status["act1"] = "done"
        if on_progress: on_progress(2, 6, script.act1[:100])
        print(f"✅ Acte I généré ({len(script.act1)} caractères)")
        time.sleep(1)

        # PROMPT 3 — Acte II Partie 1
        print(f"\n[3/6] {self.STEP_NAMES[3]}...")
        script.act2a = self._prompt3_act2a(project, script.synopsis, script.act1)
        script.status["act2a"] = "done"
        if on_progress: on_progress(3, 6, script.act2a[:100])
        print(f"✅ Acte II/1 généré ({len(script.act2a)} caractères)")
        time.sleep(1)

        # PROMPT 4 — Acte II Partie 2
        print(f"\n[4/6] {self.STEP_NAMES[4]}...")
        script.act2b = self._prompt4_act2b(project, script.synopsis, script.act2a)
        script.status["act2b"] = "done"
        if on_progress: on_progress(4, 6, script.act2b[:100])
        print(f"✅ Acte II/2 généré ({len(script.act2b)} caractères)")
        time.sleep(1)

        # PROMPT 5 — Acte III
        print(f"\n[5/6] {self.STEP_NAMES[5]}...")
        script.act3 = self._prompt5_act3(project, script.synopsis, script.act2b)
        script.status["act3"] = "done"
        if on_progress: on_progress(5, 6, script.act3[:100])
        print(f"✅ Acte III généré ({len(script.act3)} caractères)")
        time.sleep(1)

        # PROMPT 6 — Dialogues
        print(f"\n[6/6] {self.STEP_NAMES[6]}...")
        script.dialogues = self._prompt6_dialogues(project, script)
        script.status["dialogues"] = "done"
        if on_progress: on_progress(6, 6, script.dialogues[:100])
        print(f"✅ Dialogues générés ({len(script.dialogues)} caractères)")

        print(f"\n{'='*50}")
        print(f"🎉 FILM COMPLET — {script.progress_percent()}%")
        print(f"📄 Total : {len(script.export_full_script())} caractères")
        return script

    # ── LES 6 PROMPTS ────────────────────────────────────────

    def _prompt1_synopsis(self, p: FilmProject) -> str:
        """PROMPT 1 : Synopsis général."""
        prompt = f"""
Tu es un scénariste professionnel de cinéma de renommée mondiale.

Écris un synopsis cinématographique complet en {self._lang_name(p.language)} pour :

FILM : {p.title_ar} / {p.title_fr}
GENRE : {p.genre}
DURÉE : {p.duration_minutes} minutes
TON : {p.tone}
HISTOIRE : {p.logline}
HÉROS 1 : {p.hero1}
HÉROS 2 : {p.hero2}
MONDE 1 : {p.world1}
MONDE 2 : {p.world2}

Le synopsis doit :
- Présenter les deux mondes et leur conflit
- Introduire les deux héros et leurs motivations
- Décrire l'arc émotionnel complet
- Inclure le climax et la résolution
- Être professionnel, poétique et vendable à un studio

Format : 3 paragraphes — Présentation / Développement / Résolution
"""
        return self._call_claude(prompt, 1200)

    def _prompt2_act1(self, p: FilmProject, synopsis: str) -> str:
        """PROMPT 2 : Acte I détaillé."""
        prompt = f"""
Tu es un scénariste professionnel.

CONTEXTE DU FILM :
{synopsis[:500]}

Maintenant écris l'ACTE I complet en {self._lang_name(p.language)} pour "{p.title_fr}" :

Durée Acte I : 45 minutes (25% du film)
Héros : {p.hero1} vs {p.hero2}

L'Acte I doit contenir ces 6 moments clés :
1. OUVERTURE ÉPIQUE (5 min) — Flashback de la guerre ancestrale
2. INTRODUCTION HÉROS 1 (8 min) — {p.hero1} dans son monde
3. INTRODUCTION HÉROS 2 (8 min) — {p.hero2} dans son monde
4. ÉTABLISSEMENT DU CONFLIT (8 min) — La guerre s'intensifie
5. INCIDENT DÉCLENCHEUR (10 min) — L'artefact de paix est volé
6. FIN ACTE I (6 min) — Les deux héros reçoivent la même mission

Pour chaque moment : description de la scène, émotions, visuels clés.
"""
        return self._call_claude(prompt, 1500)

    def _prompt3_act2a(self, p: FilmProject, synopsis: str, act1: str) -> str:
        """PROMPT 3 : Acte II première moitié."""
        prompt = f"""
Tu es un scénariste professionnel.

SYNOPSIS : {synopsis[:300]}
FIN ACTE I : {act1[-300:]}

Écris l'ACTE II — PARTIE 1 en {self._lang_name(p.language)} pour "{p.title_fr}" :

Durée : 45 minutes
Cette partie couvre la RENCONTRE et la COOPÉRATION FORCÉE.

5 moments obligatoires :
1. PREMIÈRE CONFRONTATION (10 min) — {p.hero1} et {p.hero2} se rencontrent en ennemis
2. TRÊVE FORCÉE (8 min) — Blessés, ils doivent coopérer
3. MÉFIANCE ET DÉCOUVERTE (12 min) — Chacun découvre l'autre
4. VISITE DU MONDE OPPOSÉ (10 min) — Émerveillement et préjugés brisés
5. PREMIERS LIENS (5 min) — Une amitié/confiance fragile naît

Inclure : dialogues représentatifs, descriptions visuelles, tension émotionnelle.
"""
        return self._call_claude(prompt, 1500)

    def _prompt4_act2b(self, p: FilmProject, synopsis: str, act2a: str) -> str:
        """PROMPT 4 : Acte II deuxième moitié."""
        prompt = f"""
Tu es un scénariste professionnel.

SYNOPSIS : {synopsis[:300]}
FIN ACTE II/1 : {act2a[-300:]}

Écris l'ACTE II — PARTIE 2 en {self._lang_name(p.language)} pour "{p.title_fr}" :

Durée : 45 minutes
Cette partie couvre la RÉVÉLATION et la TRAHISON.

5 moments obligatoires :
1. ENQUÊTE COMMUNE (10 min) — Les héros cherchent le voleur ensemble
2. RÉVÉLATION CHOC (12 min) — Le vrai traître est découvert (côté inattendu)
3. COMPLICATION (8 min) — La vérité complique tout
4. POINT DE NON-RETOUR (10 min) — Une décision irréversible est prise
5. TRAHISON APPARENTE (5 min) — Tout s'effondre — les armées encerclent les héros

Maximiser la tension émotionnelle et les retournements de situation.
"""
        return self._call_claude(prompt, 1500)

    def _prompt5_act3(self, p: FilmProject, synopsis: str, act2b: str) -> str:
        """PROMPT 5 : Acte III — Résolution."""
        prompt = f"""
Tu es un scénariste professionnel.

SYNOPSIS : {synopsis[:300]}
FIN ACTE II : {act2b[-300:]}

Écris l'ACTE III COMPLET en {self._lang_name(p.language)} pour "{p.title_fr}" :

Durée : 45 minutes
Ton : {p.tone} — Le climax émotionnel le plus fort du film.

5 moments obligatoires :
1. BATAILLE FINALE (15 min) — Guerre totale entre les deux armées
2. INTERVENTION DES HÉROS (8 min) — {p.hero1} et {p.hero2} s'interposent ensemble
3. SACRIFICE (7 min) — Un sacrifice émotionnel fort — fusionnent leur magie
4. RÉVÉLATION FINALE (8 min) — Les deux mondes viennent de la même source
5. ÉPILOGUE (7 min) — L'aube d'un nouveau monde — espoir et réconciliation

Le climax doit être visuellement épique ET émotionnellement dévastateur.
Terminer sur une note d'espoir profond.
"""
        return self._call_claude(prompt, 1500)

    def _prompt6_dialogues(self, p: FilmProject, script: FilmScript) -> str:
        """PROMPT 6 : Dialogues clés."""
        prompt = f"""
Tu es un scénariste professionnel spécialisé dans les dialogues.

FILM : {p.title_ar} / {p.title_fr}
HÉROS 1 : {p.hero1}
HÉROS 2 : {p.hero2}
TON : {p.tone}

Écris les 6 DIALOGUES CLÉS du film en {self._lang_name(p.language)} :

1. PREMIÈRE CONFRONTATION — {p.hero1} vs {p.hero2} (8 répliques)
2. TRÊVE FORCÉE — Méfiance et découverte (10 répliques)
3. SCÈNE D'ÉMERVEILLEMENT — Dans le monde opposé (8 répliques)
4. RÉVÉLATION DU TRAÎTRE — Choc et réaction (10 répliques)
5. AVANT LA BATAILLE FINALE — Discours des héros (6 répliques)
6. ÉPILOGUE — Réconciliation des deux peuples (8 répliques)

Format professionnel FDX :
PERSONNAGE
  (indication de jeu)
  Réplique du dialogue.

Les dialogues doivent être poétiques, émotionnels et mémorables.
"""
        return self._call_claude(prompt, 2000)

    # ── UTILITAIRES ───────────────────────────────────────────

    def _call_claude(self, prompt: str, max_tokens: int) -> str:
        """Appel Claude API avec gestion d'erreur."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"⚠️  Erreur Claude API : {e}")
            return f"[MODE DÉMO] Contenu pour ce segment — Erreur : {str(e)[:100]}"

    def _lang_name(self, code: str) -> str:
        names = {"ar": "arabe", "fr": "français", "en": "anglais",
                 "es": "espagnol", "de": "allemand"}
        return names.get(code, "français")

    def save_script(self, script: FilmScript, path: str = "data/scripts/"):
        """Sauvegarde le scénario complet."""
        os.makedirs(path, exist_ok=True)
        filename = f"{path}{script.project.title_fr.replace(' ', '_').replace('/', '_')}_script.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script.export_full_script())
        print(f"💾 Scénario sauvegardé : {filename}")
        return filename


# ── LANCEMENT ─────────────────────────────────────────────
if __name__ == "__main__":
    from film_config import FILM_CONFIG, HERO_LIGHT, HERO_DARKNESS, WORLD_OF_LIGHT, WORLD_OF_DARKNESS

    project = FilmProject(
        title_ar=FILM_CONFIG["title_ar"],
        title_fr=FILM_CONFIG["title_fr"],
        genre=FILM_CONFIG["genre"],
        duration_minutes=FILM_CONFIG["duration_minutes"],
        language=FILM_CONFIG["language_primary"],
        logline="Une guerre entre le Monde de Lumière et le Monde des Ténèbres — deux héros ennemis forcés de coopérer découvrent que leurs mondes partagent la même origine.",
        hero1=f"{HERO_LIGHT['name_ar']} ({HERO_LIGHT['name_fr']}) — {HERO_LIGHT['role']}",
        hero2=f"{HERO_DARKNESS['name_ar']} ({HERO_DARKNESS['name_fr']}) — {HERO_DARKNESS['role']}",
        world1=f"{WORLD_OF_LIGHT['name_ar']} — {WORLD_OF_LIGHT['description'][:100]}",
        world2=f"{WORLD_OF_DARKNESS['name_ar']} — {WORLD_OF_DARKNESS['description'][:100]}",
        tone=FILM_CONFIG.get("tone", "émotionnel et profond"),
    )

    generator = FilmChainGenerator()
    script = generator.generate_full_film(project)

    if script.is_complete():
        generator.save_script(script)
        print("\n✅ Scénario complet prêt !")
    else:
        print(f"\n⚠️  Génération partielle : {script.progress_percent()}%")