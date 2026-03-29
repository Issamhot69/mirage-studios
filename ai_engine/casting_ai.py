"""
Mirage Studios — Casting IA
Génération de noms virtuels d'acteurs, producteurs et équipe technique.
Supporte plusieurs cultures : arabe, français, anglais, espagnol, etc.
"""

import os
import random
import json
from dataclasses import dataclass, field
from typing import List, Optional
import anthropic

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── BANQUES DE NOMS PAR CULTURE ───────────────────────────

NAMES_DB = {
    "arabe": {
        "prenom_m": ["يوسف", "خالد", "عمر", "أحمد", "محمد", "سامي", "ياسين", "طارق", "نادر", "رامي"],
        "prenom_f": ["سارة", "ليلى", "نور", "ريم", "هند", "دينا", "رنا", "مي", "لمى", "شيماء"],
        "nom": ["العمري", "الزهراني", "البكري", "الحسيني", "المنصور", "الطاهر", "بن علي", "القاسم", "الرشيد", "النجار"],
        "latin": ["Youssef", "Khalid", "Omar", "Ahmed", "Sami", "Sara", "Layla", "Nour", "Reem", "Hind"]
    },
    "francais": {
        "prenom_m": ["Lucas", "Thomas", "Hugo", "Maxime", "Antoine", "Pierre", "Jules", "Théo", "Arthur", "Louis"],
        "prenom_f": ["Léa", "Emma", "Chloé", "Inès", "Camille", "Manon", "Jade", "Zoé", "Clara", "Alice"],
        "nom": ["Martin", "Bernard", "Dubois", "Laurent", "Moreau", "Simon", "Michel", "Lefebvre", "Leroy", "Roux"]
    },
    "anglais": {
        "prenom_m": ["James", "Oliver", "William", "Noah", "Ethan", "Alexander", "Michael", "Daniel", "Ryan", "Jack"],
        "prenom_f": ["Sophia", "Emma", "Olivia", "Ava", "Isabella", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn"],
        "nom": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
    },
    "marocain": {
        "prenom_m": ["Amine", "Yassine", "Mehdi", "Hamza", "Ayoub", "Karim", "Rachid", "Saad", "Bilal", "Zakaria"],
        "prenom_f": ["Fatima", "Khadija", "Meryem", "Zineb", "Hajar", "Imane", "Soukaina", "Salma", "Ghita", "Loubna"],
        "nom": ["Benjelloun", "Alaoui", "Chraibi", "Tahiri", "Berrada", "Fassi", "Kettani", "Benali", "Tazi", "Skalli"]
    },
    "espagnol": {
        "prenom_m": ["Carlos", "Alejandro", "Miguel", "Diego", "Pablo", "Javier", "Luis", "Rodrigo", "Sergio", "Adrián"],
        "prenom_f": ["Sofia", "Isabella", "Valentina", "Camila", "Lucia", "Elena", "Ana", "Carmen", "Rosa", "Pilar"],
        "nom": ["García", "Martínez", "López", "Sánchez", "González", "Rodríguez", "Fernández", "Torres", "Ramírez", "Flores"]
    }
}

ROLES = {
    "acteur_principal": {"fr": "Acteur Principal", "ar": "الممثل الرئيسي", "en": "Lead Actor"},
    "actrice_principale": {"fr": "Actrice Principale", "ar": "الممثلة الرئيسية", "en": "Lead Actress"},
    "acteur_secondaire": {"fr": "Acteur Secondaire", "ar": "ممثل ثانوي", "en": "Supporting Actor"},
    "realisateur": {"fr": "Réalisateur", "ar": "المخرج", "en": "Director"},
    "producteur": {"fr": "Producteur", "ar": "المنتج", "en": "Producer"},
    "producteur_executif": {"fr": "Producteur Exécutif", "ar": "المنتج التنفيذي", "en": "Executive Producer"},
    "scenariste": {"fr": "Scénariste", "ar": "كاتب السيناريو", "en": "Screenwriter"},
    "directeur_photo": {"fr": "Directeur de la Photographie", "ar": "مدير التصوير", "en": "Director of Photography"},
    "compositeur": {"fr": "Compositeur", "ar": "الملحن", "en": "Composer"},
    "monteur": {"fr": "Monteur", "ar": "المونتير", "en": "Editor"},
    "chef_decorateur": {"fr": "Chef Décorateur", "ar": "مصمم الديكور", "en": "Production Designer"},
    "costumier": {"fr": "Costumier", "ar": "مصمم الأزياء", "en": "Costume Designer"},
}


@dataclass
class CastMember:
    name: str
    name_ar: Optional[str]
    role: str
    role_ar: str
    role_en: str
    culture: str
    age: int
    bio: str
    bio_ar: Optional[str] = None
    awards: List[str] = field(default_factory=list)
    avatar_style: str = "professional"


@dataclass
class FilmCasting:
    film_title: str
    film_title_ar: str
    cast: List[CastMember]
    crew: List[CastMember]
    production_companies: List[str]
    distribution: str
    language: str = "fr"


class CastingAI:
    """Générateur de casting virtuel professionnel."""

    def __init__(self):
        self.client = None
        if ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate_name(self, culture: str, gender: str = "m") -> dict:
        """Génère un nom complet selon la culture."""
        db = NAMES_DB.get(culture, NAMES_DB["francais"])
        if gender == "f":
            prenom = random.choice(db.get("prenom_f", db["prenom_m"]))
        else:
            prenom = random.choice(db["prenom_m"])
        nom = random.choice(db["nom"])

        result = {"name": f"{prenom} {nom}", "culture": culture}
        if culture == "arabe" and "latin" in db:
            result["name_latin"] = f"{random.choice(db['latin'])} {nom}"
        return result

    def generate_full_casting(self, film_config: dict) -> FilmCasting:
        """Génère un casting complet pour un film."""
        genre = film_config.get("genre", "fantastique")
        culture = film_config.get("culture", "marocain")
        lang = film_config.get("language", "fr")
        title = film_config.get("title", "Projet Mirage")
        title_ar = film_config.get("title_ar", "مشروع ميراج")

        cast = []
        crew = []

        # Acteurs principaux
        hero1 = self.generate_name(culture, "m")
        cast.append(CastMember(
            name=hero1["name"],
            name_ar=hero1.get("name_latin"),
            role=ROLES["acteur_principal"]["fr"],
            role_ar=ROLES["acteur_principal"]["ar"],
            role_en=ROLES["acteur_principal"]["en"],
            culture=culture,
            age=random.randint(25, 40),
            bio=self._generate_bio(hero1["name"], "acteur_principal", genre, lang),
            awards=self._random_awards(genre),
        ))

        hero2 = self.generate_name(culture, "f")
        cast.append(CastMember(
            name=hero2["name"],
            name_ar=hero2.get("name_latin"),
            role=ROLES["actrice_principale"]["fr"],
            role_ar=ROLES["actrice_principale"]["ar"],
            role_en=ROLES["actrice_principale"]["en"],
            culture=culture,
            age=random.randint(22, 38),
            bio=self._generate_bio(hero2["name"], "actrice_principale", genre, lang),
            awards=self._random_awards(genre),
        ))

        # Acteurs secondaires (3)
        for _ in range(3):
            gender = random.choice(["m", "f"])
            member = self.generate_name(culture, gender)
            role_key = "acteur_secondaire"
            cast.append(CastMember(
                name=member["name"],
                name_ar=member.get("name_latin"),
                role=ROLES[role_key]["fr"],
                role_ar=ROLES[role_key]["ar"],
                role_en=ROLES[role_key]["en"],
                culture=culture,
                age=random.randint(20, 55),
                bio=self._generate_bio(member["name"], role_key, genre, lang),
            ))

        # Équipe technique
        crew_roles = [
            ("realisateur", "m"),
            ("producteur", "m"),
            ("producteur_executif", "f"),
            ("scenariste", "f"),
            ("directeur_photo", "m"),
            ("compositeur", "m"),
            ("monteur", "f"),
        ]

        for role_key, gender in crew_roles:
            member = self.generate_name(culture, gender)
            crew.append(CastMember(
                name=member["name"],
                name_ar=member.get("name_latin"),
                role=ROLES[role_key]["fr"],
                role_ar=ROLES[role_key]["ar"],
                role_en=ROLES[role_key]["en"],
                culture=culture,
                age=random.randint(30, 60),
                bio=self._generate_bio(member["name"], role_key, genre, lang),
                awards=self._random_awards(genre) if role_key in ["realisateur", "compositeur"] else [],
            ))

        return FilmCasting(
            film_title=title,
            film_title_ar=title_ar,
            cast=cast,
            crew=crew,
            production_companies=self._generate_production_companies(culture),
            distribution=self._generate_distribution(culture),
            language=lang,
        )

    def _generate_bio(self, name: str, role: str, genre: str, lang: str) -> str:
        """Génère une biographie courte et réaliste."""
        bios = {
            "acteur_principal": [
                f"{name} est un acteur reconnu pour ses rôles intenses et sa présence magnétique à l'écran.",
                f"Révélé au grand public dans des productions indépendantes, {name} s'impose comme l'une des figures montantes du cinéma.",
                f"{name} a été formé aux arts dramatiques avant de se lancer dans une carrière internationale remarquable.",
            ],
            "actrice_principale": [
                f"{name} incarne avec subtilité des personnages complexes, alliant force et vulnérabilité.",
                f"Après plusieurs récompenses dans des festivals internationaux, {name} est aujourd'hui une référence du cinéma d'auteur.",
                f"{name} apporte une profondeur émotionnelle rare à chacun de ses rôles.",
            ],
            "realisateur": [
                f"{name} est un réalisateur visionnaire dont le style cinématographique mêle poésie visuelle et narration percutante.",
                f"Reconnu pour sa maîtrise du cadre et sa direction d'acteurs exigeante, {name} signe ici son projet le plus ambitieux.",
            ],
            "producteur": [
                f"{name} produit des œuvres engagées qui trouvent un écho international.",
                f"Fort d'une expérience de plus de 15 ans dans l'industrie, {name} accompagne les projets les plus audacieux.",
            ],
            "compositeur": [
                f"{name} compose des musiques de film qui transcendent les images et créent une atmosphère unique.",
                f"Reconnu pour ses thèmes orchestraux puissants, {name} collabore avec les plus grands réalisateurs.",
            ],
        }
        options = bios.get(role, [f"{name} est un professionnel reconnu dans son domaine."])
        return random.choice(options)

    def _random_awards(self, genre: str) -> List[str]:
        """Génère des récompenses fictives réalistes."""
        festivals = [
            "Festival de Cannes", "Festival de Venise", "Festival de Berlin",
            "Arab Film Festival", "Festival du Caire", "Festival de Marrakech",
            "Sundance Film Festival", "Festival de Toronto"
        ]
        awards = [
            "Meilleure interprétation", "Prix du jury", "Prix de la mise en scène",
            "Prix du meilleur film", "Prix du public", "Nomination officielle"
        ]
        if random.random() > 0.5:
            festival = random.choice(festivals)
            award = random.choice(awards)
            year = random.randint(2018, 2024)
            return [f"{award} — {festival} {year}"]
        return []

    def _generate_production_companies(self, culture: str) -> List[str]:
        companies = {
            "marocain": ["Mirage Films Maroc", "Atlas Productions", "Maghreb Cinéma"],
            "arabe": ["Gulf Cinema Productions", "Arab Screen", "Al-Arabiya Films"],
            "francais": ["Mirage Studios France", "Lumière Productions", "Studio Cinéart"],
            "anglais": ["Mirage Pictures", "Horizon Films", "Silver Screen Productions"],
        }
        return companies.get(culture, ["Mirage Studios International"])[:2]

    def _generate_distribution(self, culture: str) -> str:
        distributors = {
            "marocain": "Distribution : Maroc, France, Monde Arabe — Mirage Distribution",
            "arabe": "Distribution : Monde Arabe, Europe — Arab Screen Distribution",
            "francais": "Distribution : France, Europe, International — Mirage Distribution",
            "anglais": "Distribution : USA, UK, International — Mirage Global",
        }
        return distributors.get(culture, "Distribution internationale — Mirage Studios")

    def generate_with_claude(self, film_config: dict) -> dict:
        """Génère un casting enrichi via Claude AI."""
        if not self.client:
            casting = self.generate_full_casting(film_config)
            return self._casting_to_dict(casting)

        prompt = f"""
Tu es un agent de casting cinématographique professionnel.

Génère un casting complet et réaliste pour ce film :
- Titre : {film_config.get('title', 'Projet')}
- Genre : {film_config.get('genre', 'fantastique')}
- Culture : {film_config.get('culture', 'marocain')}
- Langue : {film_config.get('language', 'fr')}

Génère exactement ce JSON (noms fictifs mais réalistes) :
{{
  "cast": [
    {{"name": "...", "role": "Acteur Principal", "age": 30, "bio": "...", "awards": []}},
    {{"name": "...", "role": "Actrice Principale", "age": 28, "bio": "...", "awards": []}},
    {{"name": "...", "role": "Acteur Secondaire", "age": 35, "bio": "..."}}
  ],
  "crew": [
    {{"name": "...", "role": "Réalisateur", "bio": "..."}},
    {{"name": "...", "role": "Producteur", "bio": "..."}},
    {{"name": "...", "role": "Scénariste", "bio": "..."}},
    {{"name": "...", "role": "Compositeur", "bio": "..."}}
  ],
  "production": "Nom de la société de production",
  "distribution": "Distribution internationale"
}}

Réponds UNIQUEMENT avec le JSON, sans texte supplémentaire.
"""
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            text = message.content[0].text.strip()
            return json.loads(text)
        except Exception as e:
            print(f"[Casting] Fallback local : {e}")
            casting = self.generate_full_casting(film_config)
            return self._casting_to_dict(casting)

    def _casting_to_dict(self, casting: FilmCasting) -> dict:
        return {
            "film_title": casting.film_title,
            "film_title_ar": casting.film_title_ar,
            "cast": [
                {
                    "name": m.name,
                    "role": m.role,
                    "role_ar": m.role_ar,
                    "age": m.age,
                    "bio": m.bio,
                    "awards": m.awards,
                }
                for m in casting.cast
            ],
            "crew": [
                {
                    "name": m.name,
                    "role": m.role,
                    "role_ar": m.role_ar,
                    "bio": m.bio,
                    "awards": m.awards,
                }
                for m in casting.crew
            ],
            "production": casting.production_companies,
            "distribution": casting.distribution,
        }


if __name__ == "__main__":
    agent = CastingAI()
    config = {
        "title": "Lumière et Ténèbres",
        "title_ar": "نور وظلام",
        "genre": "fantastique",
        "culture": "marocain",
        "language": "fr"
    }
    result = agent.generate_full_casting(config)
    print(f"\n🎬 CASTING — {result.film_title}")
    print(f"\n👥 ACTEURS :")
    for m in result.cast:
        print(f"  {m.role}: {m.name} ({m.age} ans)")
        if m.awards:
            print(f"    🏆 {m.awards[0]}")
    print(f"\n🎥 ÉQUIPE TECHNIQUE :")
    for m in result.crew:
        print(f"  {m.role}: {m.name}")
    print(f"\n🏢 Production : {result.production_companies}")
    print(f"📦 {result.distribution}")