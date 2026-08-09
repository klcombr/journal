# Architecture

## Overview

```
          ┌────────────┐   REST + WebSocket   ┌────────────────┐
          │  web app   │ ───────────────────► │                │
          │ (apps/web) │ ◄─────────────────── │                │
          └────────────┘                      │                │
          ┌────────────┐   REST + WS          │   sync server  │  SQLite
          │  android   │ ───────────────────► │  (apps/server) │──────►
          │ (WebView)  │ ◄─────────────────── │  FastAPI+JWT   │  journal.db
          └────────────┘                      │                │
          ┌────────────┐   REST               │                │
          │  desktop   │ ───────────────────► │                │
          │ (apps/gui) │ ◄─────────────────── │                │
          └────────────┘                      └────────────────┘
          ┌────────────┐   REST
          │  CLI       │ ───────────────────► (same server)
          │ (journal/) │
          └────────────┘
```

Every client talks to the same API. The server is the single source of truth;
each client keeps a local copy (a markdown file for CLI/GUI, `localStorage`
for the web) and reconciles via the sync protocol.

## Modules

### `journal.core` (shared logic)

Pure functions for the markdown format: `entry_line`, `append_entry`,
`read_entries`, `day_count`, plus a deterministic `uuid5` id per entry
(derived from timestamp + body) so local and remote entries map 1:1.

### `journal.cli`

`argparse` entrypoint with `add`, `list`, `count` and `sync` subcommands.
`sync` reuses the sync client in `core` (`login_or_register`,
`save_credentials`, `sync_push`).

### `apps/server/journal_server`

- `db.py` — SQLite (WAL), `users` + `entries` tables.
- `auth.py` — PBKDF2 password hashing (600k iters), JWT issue/verify.
- `ratelimit.py` — sliding-window limiter for login/register.
- `app.py` — REST routes + WebSocket realtime broadcast.
- `schemas.py` — request/response validation.

### `apps/web`

Static single-file client (HTML+CSS+JS). Talks to the server directly;
WebSocket keeps it live. Hosted on GitHub Pages.

### `apps/gui`

Tkinter client. Local markdown file + login/sync against the server. No
external dependencies.

### `apps/android`

Gradle project. `MainActivity` is a WebView pointed at the hosted web app.
Compiles to a small APK with the Android Gradle Plugin 8.7.3 / SDK 35.

## Realtime

The server keeps per-user sets of connected WebSockets. On `POST /api/entries`
or `DELETE /api/entries/{id}`, it broadcasts an event to every connection of
that user. Endpoints run sync in a threadpool, so broadcasts are dispatched
with `run_coroutine_threadsafe` onto the event loop.

## Sync protocol (summary)

See `docs/specs/sync.md`. In short: pull `GET /api/entries`, upsert local
entries that are newer, adopt server copies that are newer, treat `deleted`
as tombstones, and use WebSocket events for live propagation.

## Security decisions

- Passwords hashed with PBKDF2-HMAC-SHA-256, 600,000 iterations, random
  16-byte salt — per OWASP ASVS v5.0.
- JWTs carry `aud`, `nbf`, `exp`; every request validates all three.
- WebSocket token is sent as the first message — never in the URL, so it
  doesn't leak into proxy/access logs.
- Login and register are rate limited per client IP.
- Same error message for unknown user / wrong password (anti-enumeration).
- SQL is parameterized everywhere (injection-safe).

## Design rules

1. Entries are append-only on disk; edits are handled via sync.
2. `core.py` stays dependency-free (stdlib only).
3. The server never stores the plaintext password.
4. `tests/fixtures/journal-test.md` remains the canonical sample of the
   on-disk format.
