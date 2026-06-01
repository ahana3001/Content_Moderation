from typing import Dict, List, Literal

from pydantic import BaseModel, Field


Decision = Literal["allow", "review", "block"]
Surface = Literal["chat", "comment", "livestream", "signup"]


class ModerationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    user_id: str | None = None
    surface: Surface = "chat"
    locale: str | None = "en"


class ModerationResponse(BaseModel):
    decision: Decision
    max_score: float
    matched_categories: List[str]
    scores: Dict[str, float]
    reasons: List[str]
    normalized_text: str
