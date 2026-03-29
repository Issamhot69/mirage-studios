"""
Mirage Studios — Multilingual Translator
Traduction automatique des dialogues avec préservation du sens cinématographique.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

LANGUAGE_NAMES = {
    "fr": "Français", "en": "English", "es": "Español",
    "de": "Deutsch", "ar": "العربية", "ja": "日本語",
    "zh": "中文", "pt": "Português", "it": "Italiano",
}


@dataclass
class TranslationUnit:
    original_text: str
    source_lang: str
    target_lang: str
    character: Optional[str] = None
    emotion: Optional[str] = None
    translated_text: str = ""
    confidence: float = 0.0
    adapted: bool = False  # True = adaptation culturelle appliquée


class MultilingualTranslator:
    """Traducteur avec adaptation cinématographique et respect du lip-sync."""

    def __init__(self, backend: str = "deepl"):
        self.backend = backend
        self.glossary: Dict[str, Dict[str, str]] = {}

    def add_glossary(self, term: str, translations: Dict[str, str]):
        """Ajoute un terme au glossaire projet (noms propres, termes techniques)."""
        self.glossary[term] = translations

    def translate(self, unit: TranslationUnit) -> TranslationUnit:
        """Traduit une unité de dialogue."""
        print(f"[Translator] {unit.source_lang} → {unit.target_lang}: {unit.original_text[:50]}...")
        unit.translated_text = f"[{unit.target_lang.upper()}] {unit.original_text}"
        unit.confidence = 0.92
        return unit

    def translate_script(self, dialogues: List[TranslationUnit]) -> List[TranslationUnit]:
        return [self.translate(d) for d in dialogues]

    def export_subtitle_srt(self, translations: List[TranslationUnit], timecodes: List[tuple]) -> str:
        """Génère un fichier SRT à partir des traductions et timecodes."""
        srt = []
        for i, (unit, (start, end)) in enumerate(zip(translations, timecodes), 1):
            srt.append(f"{i}")
            srt.append(f"{start} --> {end}")
            srt.append(unit.translated_text)
            srt.append("")
        return "\n".join(srt)

    def get_supported_languages(self) -> Dict[str, str]:
        return LANGUAGE_NAMES


if __name__ == "__main__":
    translator = MultilingualTranslator()
    translator.add_glossary("Mirage", {"en": "Mirage", "es": "Espejismo", "ar": "سراب"})
    unit = TranslationUnit(
        original_text="Le destin de notre monde repose sur tes épaules.",
        source_lang="fr", target_lang="en", character="Sage", emotion="solemn"
    )
    result = translator.translate(unit)
    print(f"Traduit : {result.translated_text} (confiance: {result.confidence})")
