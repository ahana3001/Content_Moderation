from app.config import DEFAULT_THRESHOLDS, PolicyThresholds


def thresholds_for_surface(surface: str) -> PolicyThresholds:
    return getattr(DEFAULT_THRESHOLDS, surface, DEFAULT_THRESHOLDS.chat)
