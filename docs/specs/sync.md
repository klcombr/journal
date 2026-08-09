# journal — Sync Protocol

Defines how a client (CLI, GUI, Web, Android) stays consistent with the
server and with other clients.

## Principles

1. **Entries are immutable-ish.** A body edit is allowed but rare; the sync
   layer must not lose a newer edit to an older write.
2. **Last write wins** by `updated_at` (ISO 8601, UTC, microseconds).
3. **Client generates IDs.** Every entry carries a client-generated UUID v4
   so the same entry is recognisable on every device without server round
   trips.
4. **Deletes are tombstones.** `deleted: true` is kept for 30 days by the
   server before physical removal.

## The handshake

```
Client                           Server
  │ GET /api/entries               │
  │  ────────────────────────────► │
  │ ◄──────────────────────────── 200 [entries]
  │                                │
  │ for each local entry newer:    │
  │   POST /api/entries            │
  │  ────────────────────────────► │
  │ ◄──────────────────────────── 201 / 409
  │                                │
  │ WS /ws?token=...               │
  │  ────────────────────────────► │
  │ ◄──────────────────────────── snapshot {entries}
  │ ◄──────────────────────────── event {created|updated|deleted}
```

## Merge rules (per entry id)

| Local | Server | Result |
| ----- | ------ | ------ |
| newer (`updated_at` >) | older | push local (upsert) |
| older | newer | adopt server |
| equal | equal | identical — no-op |
| deleted locally, server older | — | push tombstone |
| server tombstone, local older | — | adopt tombstone |

## Clock notes

- All timestamps are UTC. Clients convert for display only.
- If the client clock is behind, sync still converges because ties compare
  equal and the server's stored value wins on `409`.

## Payloads

```json
// upsert
{ "id": "9f0e...", "body": "note", "created_at": "2026-08-08T09:27:47.123456Z", "updated_at": "2026-08-08T09:27:47.123456Z" }

// tombstone push
{ "id": "9f0e...", "body": "", "deleted": true, "updated_at": "..." }

// realtime event
{ "type": "entry", "action": "deleted", "entry": { "id": "...", "deleted": true, "updated_at": "..." } }
```

## Guarantees

- A single writer (one device at a time per user in practice) → zero
  conflicts.
- Multiple writers → last writer wins; the server never silently drops a
  newer `updated_at`.
- Deleted entries stop showing up in any client within one sync.
