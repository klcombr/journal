# journal-server

The sync backend for journal. FastAPI + SQLite + JWT auth + WebSocket realtime.

## Run locally

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn journal_server.app:app --host 127.0.0.1 --port 8000
```

Or with Docker (SQLite volume at `/srv`):

```bash
docker build -t journal-server .
docker run -p 8000:8000 -v journal-data:/srv journal-server
```

## Environment

| Var | Default | Purpose |
| --- | --- | --- |
| `JOURNAL_DB` | `./journal.db` | SQLite file path (when no Postgres URL) |
| `JOURNAL_SECRET` | random per boot | JWT signing secret |
| `JOURNAL_CORS_ORIGINS` | `*` | comma-separated allowed origins (set to your web app origin in prod) |
| `DATABASE_URL` / `JOURNAL_DATABASE_URL` | — | PostgreSQL URL (`postgres://`…); enables Postgres mode (Supabase/Render) |

## Storage backends

Two backends, selected automatically:

- **SQLite** — used when no Postgres URL is set. Zero setup; fine locally.
- **PostgreSQL (Supabase/Render)** — enabled when `DATABASE_URL` or
  `JOURNAL_DATABASE_URL` starts with `postgres`/`postgresql`. The schema is
  created on startup. This is the way to persist on Render's **free** tier,
  which does not allow persistent disks.

## Deploy on Render (free)

The repo ships a `render.yaml` blueprint — Render detects it automatically.

1. Push this repo to GitHub.
2. Open <https://dashboard.render.com> → **New** → **Blueprint**.
3. Connect the `klcombr/journal` repo and apply.
4. Render builds the Dockerfile and creates a free service with a generated
   `JOURNAL_SECRET`.

### Persist data on the free tier (Supabase)

1. Create a free Postgres database at <https://supabase.com>.
2. Copy its **connection string** (Project Settings → Database → URI, the
   `postgresql://…` one, port 5432 — not the pooler).
3. In Render: service `journal-server` → **Environment** → add
   `DATABASE_URL` with that string → save (triggers a redeploy).
4. On startup the server creates the tables and your entries now survive
   redeploys.

> Without `DATABASE_URL` on the free plan, data lives on an ephemeral disk
> and is lost on redeploy — fine for trying the service out.

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
