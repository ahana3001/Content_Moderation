# Real-Time Content Moderation

This project is a small, deployable moderation app for checking user text before it is shown to others. It comes with a simple web dashboard, an API, and a rule-based starter engine that you can replace with a stronger ML model later.

## What You Get

- A friendly web app at `/`
- A moderation API at `/moderate`
- Swagger docs at `/docs`
- A Docker setup that is ready for deployment

The app checks text against a few common risk areas:

- `toxicity`
- `hate`
- `harassment`
- `sexual`
- `self_harm`
- `violence`
- `spam`

Each category gets a score from `0.0` to `1.0`, and the app returns one of three decisions:

- `allow`
- `review`
- `block`

## Why It Is Built This Way

Big moderation systems usually do not depend on a single yes-or-no model. They use several signals together, then map the result to a policy action.

This starter follows that same pattern in a lightweight way so you can:

- test moderation flows quickly
- swap in a real classifier later
- tune thresholds without changing the API

## Project Structure

```text
app/
  main.py
  schemas.py
  config.py
  moderation/
    engine.py
    features.py
    policies.py
    types.py
tests/
  test_engine.py
requirements.txt
```

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

- `http://127.0.0.1:8000/` for the web app
- `http://127.0.0.1:8000/docs` for the API docs

## How To Use The Web App

1. Open the homepage.
2. Paste content into the text area.
3. Choose the surface such as `chat`, `comment`, `livestream`, or `signup`.
4. Click `Analyze Content`.
5. Review the decision, reasons, matched categories, and per-category scores.

You can also use the example buttons to try a safe message, a toxic one, a threat, or a spam message without typing anything from scratch.

## Example API Request

```bash
curl -X POST http://127.0.0.1:8000/moderate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "You are disgusting and should disappear",
    "user_id": "user-123",
    "surface": "chat"
  }'
```

## Example API Response

```json
{
  "decision": "review",
  "max_score": 0.79,
  "matched_categories": ["toxicity", "harassment"],
  "scores": {
    "toxicity": 0.79,
    "hate": 0.02,
    "harassment": 0.71,
    "sexual": 0.01,
    "self_harm": 0.18,
    "violence": 0.05,
    "spam": 0.0
  },
  "reasons": [
    "Detected abusive phrasing",
    "Multiple high-risk policy categories exceeded review thresholds"
  ]
}
```

## What To Build Next

This starter is intentionally lightweight. If you want to make it production-grade, the next upgrades are usually:

1. Replace local scorers with trained models from Hugging Face, PyTorch, or an internal model service.
2. Add async streaming or Kafka-based moderation queues for high throughput.
3. Store decisions, features, and appeals outcomes for retraining.
4. Tune thresholds separately for comments, DMs, posts, and creator tools.
5. Add image/video moderation services beside the text gateway.

## Important Note

This project does not reproduce Meta's internal moderation stack. It uses a similar systems pattern, not their proprietary models.

## Run In Production

For a simple production-style run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Deploy With Docker

Build the image:

```bash
docker build -t shieldstream-moderation .
```

Run it locally as a production-style container:

```bash
docker run -p 8000:8000 shieldstream-moderation
```

Open:

- `http://127.0.0.1:8000/`

The container reads `PORT` automatically, which makes it friendly for platforms like Render and Railway.

## Deploy To Render

1. Push this project to GitHub.
2. In Render, create a new `Web Service`.
3. Connect the GitHub repository.
4. Choose `Docker` as the runtime.
5. Render will use the included `Dockerfile`.
6. After deploy, open the generated public URL.

Health check path:

- `/health`

## Deploy To Railway

1. Push this project to GitHub.
2. Create a new Railway project from the repo.
3. Railway will detect the `Dockerfile`.
4. Deploy and open the generated domain.

## Deploy To Any VM

If you want to deploy on an Ubuntu server or cloud VM:

```bash
docker build -t shieldstream-moderation .
docker run -d --restart unless-stopped -p 80:8000 shieldstream-moderation
```

For production hosting, you can also put it behind Nginx or a load balancer and route `/` to the FastAPI container.
