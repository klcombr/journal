# journal — Product Specification

**Status:** v2.0 (draft)
**Date:** 2026-08-09

## 1. Vision

`journal` is a personal journaling system: write short timestamped entries,
track the days you logged, and keep everything in sync across every device
you own — terminal, desktop, browser and phone.

## 2. Platforms

| Target     | Tech                | Directory       | Notes                             |
| ---------- | ------------------- | --------------- | --------------------------------- |
| CLI        | Python (stdlib)     | `journal/`      | Existing tool, extended with sync |
| Server     | Python FastAPI      | `apps/server/`  | Auth, REST, WebSocket realtime    |
| Web app    | Vanilla JS + HTML   | `apps/web/`     | Runs on the site, talks to server |
| Desktop GUI| Python + Tkinter    | `apps/gui/`     | Local-first with sync             |
| Android    | Kotlin WebView      | `apps/android/` | Thin client over the web app      |

## 3. Core concepts

- **Entry** — a single line `- ISO-TIMESTAMP text` in a markdown file.
- **Journal** — a list of entries. On disk it is always plain markdown.
- **Account** — identifies a user. Unlocks cloud sync across devices.
- **Sync** — reconcile local entries with the server using
  last-write-wins per entry keyed by `updated_at`.

## 4. Features (v2.0)

### 4.1 Core (all platforms)
- Add, list and count entries.
- Timestamps generated automatically (ISO 8601).
- Day tracking (`count` / `count --days`).

### 4.2 Sync & accounts
- Register and login with username + password.
- JWT bearer authentication for all API calls.
- Entries live under `/api/entries` per authenticated user.
- WebSocket `/ws` pushes live updates to connected clients.
- Conflict resolution: last writer wins by `updated_at`; entries have a
  stable client-generated UUID.

### 4.3 Realtime
- When device A adds an entry, every other connected device of the same
  user receives it immediately over WebSocket.

## 5. Data model

### Entry (API shape)
```json
{
  "id": "uuid",
  "body": "learned how Actions cron works",
  "created_at": "2026-08-08T09:27:47Z",
  "updated_at": "2026-08-08T09:27:47Z",
  "deleted": false
}
```

### On-disk markdown (unchanged, backward compatible)
```markdown
- 2026-08-08T09:27:47+00:00 learned how Actions cron works
```

## 6. Non-goals

- No attachments / rich media in v2.0.
- No end-to-end encryption (transport is TLS; server sees plaintext).
- No public feed — journals are private per account.
