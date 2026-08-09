# journal — API Specification v2

Base URL: `https://<host>` (local dev: `http://127.0.0.1:8000`)

All JSON. Auth via `Authorization: Bearer <token>`.

## Auth

### `POST /api/auth/register`
```json
{ "username": "alice", "password": "hunter2" }
```
→ `201 { "token": "jwt", "username": "alice" }`

### `POST /api/auth/login`
```json
{ "username": "alice", "password": "hunter2" }
```
→ `200 { "token": "jwt", "username": "alice" }`

Errors: `400` invalid payload, `401` wrong credentials, `409` username taken.

## Entries

### `GET /api/entries`
List all entries for the authenticated user (including soft-deleted ones
with `deleted: true` so clients can reconcile).

→ `200 [ { id, body, created_at, updated_at, deleted } ]`

### `POST /api/entries`
```json
{ "id": "uuid-v4", "body": "text", "created_at": "ISO", "updated_at": "ISO" }
```
Create or overwrite (upsert) an entry by `id`. Server rejects payloads whose
`updated_at` is older than the stored entry's (`409 Conflict`).

→ `201 { id, body, created_at, updated_at, deleted }`

### `PUT /api/entries/{id}`
```json
{ "body": "new text", "updated_at": "ISO" }
```
Update `body` (and optional `deleted`) of an existing entry. `id` and
`created_at` are kept from the stored row.

→ `200 { id, body, created_at, updated_at, deleted }` · `404` if missing

### `DELETE /api/entries/{id}`
Soft-delete (tombstone) — the entry stays in the list with `deleted: true`.

→ `200 { id, deleted: true, updated_at }`

### `GET /api/health`
→ `200 { "status": "ok", "version": "2.0.0" }`

## Realtime — WebSocket

### `WS /ws`
The token is sent as the **first client message** — never in the URL — so it
cannot leak into access/proxy logs:

```json
{ "token": "<jwt>" }
```

Server replies `{ "type": "auth_ok" }`, then replays the entry list:
```json
{ "type": "snapshot", "entries": [ ... ] }
```

Server then pushes events to every connected client of that user:

```json
{ "type": "entry", "action": "created" | "updated" | "deleted", "entry": { ... } }
```

## Sync strategy (client side)

1. Pull: `GET /api/entries` → build local map `id -> entry`.
2. Merge: for each local entry, if `local.updated_at > server.updated_at`,
   `POST /api/entries` (upsert).
3. Tombstones: if server says `deleted: true` and local doesn't have newer,
   mark local as deleted.
4. Conflicts: server `409` means server is newer — adopt server copy.

## Error shape
```json
{ "detail": "human readable message" }
```
