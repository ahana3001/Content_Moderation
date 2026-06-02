from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.moderation.engine import decide_moderation
from app.schemas import ModerationRequest, ModerationResponse


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


app = FastAPI(
    title="Real-Time Content Moderation API",
    version="0.1.0",
    description=(
        "A starter moderation service that scores user text across policy "
        "categories and returns allow/review/block decisions."
    ),
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": "ShieldStream",
            "tagline": "Real-time moderation for safer user conversations",
        },
    )


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/moderate", response_model=ModerationResponse)
def moderate(payload: ModerationRequest) -> ModerationResponse:
    result = decide_moderation(payload.text, payload.surface)
    return ModerationResponse(
        decision=result.decision,
        max_score=result.max_score,
        matched_categories=result.matched_categories,
        scores=result.scores,
        reasons=result.reasons,
        normalized_text=result.normalized_text,
    )
