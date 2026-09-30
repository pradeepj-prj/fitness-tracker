# Next Agent Handoff

This folder is the standalone FastAPI calorie tracker app.

## First Things To Know

- The app is for Vidhi only in the UI, but the backend still preserves profile-aware APIs for
  compatibility with the migrated data.
- Do not commit `.env`, `calorie_tracker.db`, `.venv`, cache files, or generated egg-info.
- The actual tracker data is in `calorie_tracker.db`. Treat it as private health data.
- The agent's behavior depends on `app/agent_context/01-agent-operating-rules.md` and
  `app/agent_context/02-calorie-reference-library.md`. Do not remove these from the app.
- Images uploaded in chat are sent to OpenAI for the current request only and are not stored.
- Conversation text is stored in SQLite. The active prompt only loads recent messages plus
  summarized older context.

## Local Setup On Personal Machine

```bash
cd standalone
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
```

Run locally:

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## Environment

`.env` is intentionally not committed, but it may be present in a private handoff zip.

Required values:

```bash
DATABASE_PATH=calorie_tracker.db
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.6-terra
AUTH_USERNAME=Vidhi
AUTH_PASSWORD=...
SESSION_SECRET=...
SESSION_DAYS=30
SESSION_COOKIE_SECURE=false
AGENT_CONTEXT_MESSAGE_LIMIT=24
AGENT_TRANSCRIPT_RETENTION_LIMIT=200
```

For production, use:

```bash
DATABASE_PATH=/data/calorie_tracker.db
SESSION_COOKIE_SECURE=true
```

## GitHub Push From Personal Machine

If this folder arrives with `.git`, verify ignored files first:

```bash
git status --short --ignored
git check-ignore -v .env calorie_tracker.db .venv/bin/python
```

Then push:

```bash
git remote set-url origin https://github.com/pradeepj-prj/fitness-tracker.git
git push -u origin main
```

If `.git` is not present:

```bash
git init -b main
git add -A
git commit -m "Initial standalone calorie tracker app"
git remote add origin https://github.com/pradeepj-prj/fitness-tracker.git
git push -u origin main
```

Before pushing, ensure these are not staged:

```bash
git status --short
```

Do not push:

- `.env`
- `calorie_tracker.db`
- `.venv/`
- `.pytest_cache/`
- `__pycache__/`
- `calorie_tracker.egg-info/`

## Deployment Recommendation

Use Render paid Web Service with a persistent disk.

Set env vars:

```bash
DATABASE_PATH=/data/calorie_tracker.db
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.6-terra
AUTH_USERNAME=Vidhi
AUTH_PASSWORD=...
SESSION_SECRET=...
SESSION_COOKIE_SECURE=true
AGENT_CONTEXT_MESSAGE_LIMIT=24
AGENT_TRANSCRIPT_RETENTION_LIMIT=200
```

Attach a persistent disk mounted at `/data`, then upload the SQLite DB as:

```text
/data/calorie_tracker.db
```

Health check path:

```text
/health
```

## Current Features

- `/chat/`: mobile-friendly chat UI.
- `/dashboard/`: dashboard with link back to chat.
- `New Chat`: starts a fresh conversation without loading previous chat transcript.
- Enter sends; Shift+Enter inserts a newline.
- App-level username/password login.
- OpenAI-backed agent with typed DB tools.
- No image storage.

## Verification

```bash
.venv/bin/python -m pytest
```

Current expected test count at handoff: 23 passing.

