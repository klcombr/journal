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
| `JOURNAL_DELETE_KEEP_DAYS` | `30` | tombstone retention |

## API

See `docs/specs/api.md`. Interactive docs at `/docs` when running.
