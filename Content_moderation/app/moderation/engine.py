from app.moderation.features import extract_features, token_frequency
from app.moderation.policies import thresholds_for_surface
from app.moderation.types import FeatureSignals, ModerationResult


BASE_CATEGORY_BIAS = {
    "toxicity": 0.05,
    "hate": 0.02,
    "harassment": 0.03,
    "sexual": 0.01,
    "self_harm": 0.01,
    "violence": 0.02,
    "spam": 0.0,
}


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 4)))


def _score_toxicity(features: FeatureSignals) -> float:
    score = BASE_CATEGORY_BIAS["toxicity"] + (0.16 * features.keyword_hits["toxicity"])
    if features.uppercase_ratio > 0.45:
        score += 0.1
    if features.exclamation_count >= 3:
        score += 0.08
    return _clamp(score)


def _score_hate(features: FeatureSignals) -> float:
    score = BASE_CATEGORY_BIAS["hate"] + (0.22 * features.keyword_hits["hate"])
    if "all" in features.tokens and features.keyword_hits["hate"] > 0:
        score += 0.1
    return _clamp(score)


def _score_harassment(features: FeatureSignals) -> float:
    score = BASE_CATEGORY_BIAS["harassment"] + (0.24 * features.keyword_hits["harassment"])
    if "you" in features.tokens and features.keyword_hits["toxicity"] > 0:
        score += 0.12
    return _clamp(score)


def _score_sexual(features: FeatureSignals) -> float:
    score = BASE_CATEGORY_BIAS["sexual"] + (0.24 * features.keyword_hits["sexual"])
    return _clamp(score)


def _score_self_harm(features: FeatureSignals) -> float:
    score = BASE_CATEGORY_BIAS["self_harm"] + (0.28 * features.keyword_hits["self_harm"])
    if "i" in features.tokens and features.keyword_hits["self_harm"] > 0:
        score += 0.15
    return _clamp(score)


def _score_violence(features: FeatureSignals) -> float:
    score = BASE_CATEGORY_BIAS["violence"] + (0.22 * features.keyword_hits["violence"])
    if "you" in features.tokens and features.keyword_hits["violence"] > 0:
        score += 0.1
    if "i" in features.tokens and "will" in features.tokens and "you" in features.tokens:
        score += 0.31
    return _clamp(score)


def _score_spam(features: FeatureSignals) -> float:
    score = BASE_CATEGORY_BIAS["spam"] + (0.18 * features.keyword_hits["spam"])
    if features.link_count > 0:
        score += 0.18
    if features.repeated_char_sequences > 0:
        score += 0.08
    token_counts = token_frequency(features.tokens)
    if any(count >= 4 for count in token_counts.values()):
        score += 0.12
    return _clamp(score)


def score_categories(text: str) -> tuple[FeatureSignals, dict[str, float]]:
    features = extract_features(text)
    scores = {
        "toxicity": _score_toxicity(features),
        "hate": _score_hate(features),
        "harassment": _score_harassment(features),
        "sexual": _score_sexual(features),
        "self_harm": _score_self_harm(features),
        "violence": _score_violence(features),
        "spam": _score_spam(features),
    }
    return features, scores


def decide_moderation(text: str, surface: str = "chat") -> ModerationResult:
    features, scores = score_categories(text)
    thresholds = thresholds_for_surface(surface)
    max_score = max(scores.values()) if scores else 0.0
    sorted_scores = sorted(scores.values(), reverse=True)
    combined_risk = sorted_scores[0] + sorted_scores[1] if len(sorted_scores) > 1 else max_score
    soft_match_threshold = 0.2
    matched = [category for category, score in scores.items() if score >= thresholds.allow_below]

    reasons: list[str] = []
    if scores["spam"] >= soft_match_threshold:
        reasons.append("Detected spam-like promotion or link behavior")
    if scores["toxicity"] >= soft_match_threshold or scores["harassment"] >= soft_match_threshold:
        reasons.append("Detected abusive phrasing")
    if scores["self_harm"] >= soft_match_threshold:
        reasons.append("Detected self-harm related language")
    if scores["violence"] >= soft_match_threshold:
        reasons.append("Detected violent threat language")
    if scores["sexual"] >= soft_match_threshold:
        reasons.append("Detected sexual content markers")
    if scores["hate"] >= soft_match_threshold:
        reasons.append("Detected hateful or dehumanizing language")

    if max_score >= thresholds.block_at:
        decision = "block"
        reasons.append("Highest-risk category exceeded block threshold")
    elif max_score >= thresholds.allow_below or combined_risk >= 0.55:
        decision = "review"
        if not matched:
            matched = [
                category
                for category, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)
                if score >= soft_match_threshold
            ][:2]
        reasons.append("Multiple high-risk policy categories exceeded review thresholds")
    else:
        decision = "allow"
        reasons.append("No policy category exceeded moderation thresholds")

    return ModerationResult(
        decision=decision,
        max_score=max_score,
        matched_categories=matched,
        scores=scores,
        reasons=reasons,
        normalized_text=features.normalized_text,
    )
