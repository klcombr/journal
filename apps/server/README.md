# journal-server

The sync backend for journal. FastAPI + SQLite + JWT auth + WebSocket realtime.

## Run locally

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn journal_server.app:app --host 127.0.0.1 --port 8000
```

Or with Docker:

```bash
docker build -t journal-server .
docker run -p 8000:8000 -v journal-data:/data journal-server
```

## Environment

| Var | Default | Purpose |
| --- | --- | --- |
| `JOURNAL_DB` | `./journal.db` | SQLite file path |
| `JOURNAL_SECRET` | random per boot | JWT signing secret |
| `JOURNAL_CORS_ORIGINS` | `*` | comma-separated allowed origins (set to your web app origin in prod) |

## Deploy on Render (free)

The repo ships a `render.yaml` blueprint — Render detects it automatically.

1. Push this repo to GitHub.
2. Open <https://dashboard.render.com> → **New** → **Blueprint**.
3. Connect the `klcombr/journal` repo and apply.
4. Render builds the Dockerfile, creates a free service, generates a
   `JOURNAL_SECRET`, and mounts a 1&nbsp;GB disk at `/data`.

The free plan **sleeps after ~15 min of inactivity**; the first request after
waking takes ~50&nbsp;s. `JOURNAL_CORS_ORIGINS` is pre-set to
`https://klcombr.github.io` for the hosted web app.

Point any client at the service URL:

```bash
journal sync --register --base https://journal-server.onrender.com
```

> Tip: set a fixed `JOURNAL_SECRET` so existing tokens survive redeploys.

## API

See `docs/specs/api.md`. Interactive docs at `/docs` when running.
