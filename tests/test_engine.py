from fastapi.testclient import TestClient

from app.main import app
from app.moderation.engine import decide_moderation


client = TestClient(app)


def test_homepage_loads() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "ShieldStream" in response.text


def test_allows_benign_text() -> None:
    result = decide_moderation("Hello, thanks for joining the stream today.")
    assert result.decision == "allow"
    assert result.max_score < 0.45


def test_reviews_abusive_text() -> None:
    result = decide_moderation("You are disgusting and worthless.")
    assert result.decision == "review"
    assert "toxicity" in result.matched_categories or "harassment" in result.matched_categories


def test_blocks_violent_text_on_strict_surface() -> None:
    result = decide_moderation("I will kill you", surface="signup")
    assert result.decision == "block"
    assert result.scores["violence"] >= 0.65


def test_reviews_spam_message() -> None:
    result = decide_moderation("Free money click here www.scam.test buy now buy now")
    assert result.decision in {"review", "block"}
    assert result.scores["spam"] >= 0.45
