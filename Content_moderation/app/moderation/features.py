import re
from collections import Counter

from app.moderation.types import FeatureSignals


CATEGORY_KEYWORDS = {
    "toxicity": {
        "idiot",
        "stupid",
        "moron",
        "trash",
        "disgusting",
        "loser",
    },
    "hate": {
        "vermin",
        "subhuman",
        "dirty",
        "animals",
    },
    "harassment": {
        "kill yourself",
        "nobody wants you",
        "go away",
        "worthless",
        "should disappear",
    },
    "sexual": {
        "nude",
        "explicit",
        "sexual",
        "porn",
    },
    "self_harm": {
        "suicide",
        "self harm",
        "cut myself",
        "end my life",
    },
    "violence": {
        "kill",
        "shoot",
        "bomb",
        "murder",
        "stab",
    },
    "spam": {
        "buy now",
        "free money",
        "click here",
        "telegram",
        "whatsapp",
        "guaranteed profit",
    },
}


def normalize_text(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text.strip().lower())
    return collapsed


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def count_keyword_hits(normalized_text: str) -> dict[str, int]:
    hits: dict[str, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits[category] = sum(1 for keyword in keywords if keyword in normalized_text)
    return hits


def extract_features(text: str) -> FeatureSignals:
    normalized = normalize_text(text)
    tokens = tokenize(text)
    uppercase_chars = sum(1 for char in text if char.isupper())
    alpha_chars = sum(1 for char in text if char.isalpha())
    uppercase_ratio = uppercase_chars / alpha_chars if alpha_chars else 0.0
    repeated_char_sequences = len(re.findall(r"(.)\1{3,}", text.lower()))
    link_count = len(re.findall(r"https?://|www\.", text.lower()))
    keyword_hits = count_keyword_hits(normalized)

    return FeatureSignals(
        normalized_text=normalized,
        tokens=tokens,
        exclamation_count=text.count("!"),
        uppercase_ratio=uppercase_ratio,
        repeated_char_sequences=repeated_char_sequences,
        link_count=link_count,
        keyword_hits=keyword_hits,
    )


def token_frequency(tokens: list[str]) -> Counter[str]:
    return Counter(tokens)
