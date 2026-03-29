"""
Mirage Studios — Audience Analyzer
Analyse des audiences cibles et segmentation marketing.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class AudienceSegment:
    name: str
    age_range: str
    size_millions: float
    affinity_score: float      # 0-10 pour ce genre
    platform_preference: str   # "cinema", "streaming", "both"
    price_sensitivity: float   # 0-10


@dataclass
class AudienceReport:
    primary_segment: AudienceSegment
    secondary_segments: List[AudienceSegment]
    total_addressable_market: float
    recommended_platforms: List[str]
    marketing_channels: Dict[str, float]


class AudienceAnalyzer:
    SEGMENTS = {
        "18-25": AudienceSegment("Gen Z Cinema", "18-25", 12.5, 8.0, "streaming", 7.5),
        "25-40": AudienceSegment("Millennials", "25-40", 18.0, 7.0, "both", 5.0),
        "family": AudienceSegment("Familles", "all", 22.0, 6.5, "cinema", 6.0),
        "40+": AudienceSegment("Adultes +40", "40+", 15.0, 5.0, "cinema", 4.0),
    }

    def analyze(self, genre: str, demographic: str, budget: float) -> AudienceReport:
        primary = self.SEGMENTS.get(demographic, self.SEGMENTS["25-40"])
        secondary = [s for k, s in self.SEGMENTS.items() if k != demographic][:2]
        tam = primary.size_millions + sum(s.size_millions * 0.3 for s in secondary)
        channels = {
            "Social Media (TikTok/Instagram)": 0.30,
            "YouTube Trailer": 0.20,
            "TV / CTV": 0.25,
            "Influenceurs": 0.15,
            "Affichage": 0.10,
        }
        return AudienceReport(
            primary_segment=primary,
            secondary_segments=secondary,
            total_addressable_market=round(tam, 1),
            recommended_platforms=(
                ["Netflix", "Prime Video", "Canal+"]
                if primary.platform_preference == "streaming"
                else ["Cinéma", "Disney+"]
            ),
            marketing_channels=channels,
        )


if __name__ == "__main__":
    analyzer = AudienceAnalyzer()
    report = analyzer.analyze("fantastique", "18-25", 80.0)
    print(f"Segment principal : {report.primary_segment.name}")
    print(f"TAM : {report.total_addressable_market}M spectateurs potentiels")
    print("Canaux marketing :")
    for canal, pct in report.marketing_channels.items():
        print(f"  {canal}: {int(pct*100)}%")
