# journal

A personal journal that follows you everywhere. Write short timestamped
entries, track the days you logged, and sync across terminal, desktop, browser
and phone.

> **Website:** <https://klcombr.github.io/journal/>

## The platform

| App | Where | What |
| --- | ----- | ---- |
| [Web app](apps/web/) | browser | full editor with realtime sync |
| [Android](apps/android/) | phone | APK — same web app in a shell |
| [Desktop GUI](apps/gui/) | Linux/Win/mac | Tkinter client |
| [CLI](journal/) | terminal | the original tool |
| [Sync server](apps/server/) | your host | FastAPI + JWT + WebSocket |

## Quick start (CLI)

```bash
pip install -e .

journal add "learned how Actions cron works"
journal list -n 5
journal count
journal count --days
```

## Sync (any client)

```bash
# 1. run the server (see apps/server/)
uvicorn journal_server.app:app --port 8000

# 2. register + sync the CLI
journal sync --register --base http://127.0.0.1:8000

# 3. from now on, sync both ways
journal sync --base http://127.0.0.1:8000
```

Entries are keyed by a stable client-generated UUID, and conflicts resolve
last-write-wins by `updated_at`. The on-disk file stays plain markdown —
backward compatible with every existing entry.

## Documentation

- [Product spec](docs/specs/product.md)
- [API spec](docs/specs/api.md)
- [Sync protocol](docs/specs/sync.md)
- [Guide](docs/guide.md)
- [Architecture](docs/architecture.md)
- [Examples](examples/workflow.md)
- [Changelog](docs/changelog.md)

## Security

- Passwords: PBKDF2-HMAC-SHA-256, 600k iterations, per-user random salt
  (ASVS v5.0 compliant).
- Auth: JWT (HS256) with `aud`, `nbf`, `exp` — validated on every request.
- Rate limiting on login/register (anti credential-stuffing).
- Deletes are tombstones; entries never silently lost on conflict.

## License

[MIT](LICENSE)
