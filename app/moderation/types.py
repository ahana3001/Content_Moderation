from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class FeatureSignals:
    normalized_text: str
    tokens: List[str]
    exclamation_count: int
    uppercase_ratio: float
    repeated_char_sequences: int
    link_count: int
    keyword_hits: Dict[str, int]


@dataclass(frozen=True)
class ModerationResult:
    decision: str
    max_score: float
    matched_categories: List[str]
    scores: Dict[str, float]
    reasons: List[str]
    normalized_text: str
