# Fitness Calorie Tracker Standalone

Standalone FastAPI version of the migrated calorie tracker.

## What It Runs

- `/chat/` - Pebble chat UI for conversational logging.
- `/dashboard/` - existing calorie/weight dashboard.
- `/agent/chat` - server-side OpenAI-backed agent endpoint.
- Existing tracker API routes: `/entries`, `/weights`, `/settings`, `/deficit`.

Images uploaded in chat are sent to the model for the current request only. They are not stored.
Conversation text is stored with a capped transcript and rolling summary. Tracker data remains
permanent in SQLite.

## Local Setup

```bash
pyenv local 3.12.13
python -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
cp .env.example .env
```

Set at least:

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5-mini
DATABASE_PATH=calorie_tracker.db
AUTH_USERNAME=tracker
AUTH_PASSWORD=choose-a-long-password
SESSION_SECRET=generate-a-long-random-secret
```

Run:

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Deploy

Use a normal web-service host with persistent disk, not Netlify.

Required environment:

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5-mini
DATABASE_PATH=/data/calorie_tracker.db
AUTH_USERNAME=tracker
AUTH_PASSWORD=choose-a-long-password
SESSION_SECRET=generate-a-long-random-secret
SESSION_COOKIE_SECURE=true
AGENT_CONTEXT_MESSAGE_LIMIT=24
AGENT_TRANSCRIPT_RETENTION_LIMIT=200
```

Mount persistent storage at `/data`. This repository intentionally does not commit
`calorie_tracker.db`. For production, upload the current SQLite file to the persistent disk as
`/data/calorie_tracker.db` before using the app. If the file is missing, the service can start
with an empty database.

If `AUTH_PASSWORD` is blank, the app runs without login protection. Do not deploy that way.
`/health` remains public for uptime checks; chat, dashboard, and API routes require login.

## Deploy on Render

This repo includes `render.yaml` for a Render Blueprint Docker deploy with a persistent disk mounted at `/data`.

1. Push this repo to GitHub.
2. In Render, choose **New +** -> **Blueprint** and select this repository.
3. Enter required secret values when prompted:
   - `OPENAI_API_KEY`
   - `AUTH_PASSWORD`
4. Deploy. Render will create the persistent disk and store SQLite at `/data/calorie_tracker.db`.
5. If you need existing local data in production, upload `calorie_tracker.db` to the Render disk as `/data/calorie_tracker.db` before relying on the hosted app.

## Verify

```bash
curl -s https://YOUR_HOST/health
curl -s "https://YOUR_HOST/settings?profile=vidhi"
curl -s "https://YOUR_HOST/weights/latest?profile=vidhi"
```

Run tests:

```bash
.venv/bin/python -m pytest
```
