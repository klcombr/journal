"""FastAPI application: auth, entries, WebSocket realtime broadcast."""

import asyncio
import json
import os
import threading
from datetime import datetime, timedelta, timezone

from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware

from .auth import decode_token, hash_password, make_token, verify_password
from .db import get_db, init_db
from .ratelimit import allow_login, allow_register
from .schemas import AuthIn, AuthOut, EntryIn, EntryOut, EntryUpdate

app = FastAPI(title="journal-server", version="2.0.0")

# CORS: default to same-origin; set JOURNAL_CORS_ORIGINS to a comma-separated
# allowlist in production (e.g. https://klcombr.github.io).
_cors_origins = [
    o.strip()
    for o in os.environ.get("JOURNAL_CORS_ORIGINS", "").split(",")
    if o.strip()
] or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _client_ip(request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _current_user(authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if not payload:
        raise HTTPException(401, "invalid or expired token")
    return int(payload["sub"]), payload.get("username", "")


def _row_to_out(row) -> dict:
    return {
        "id": row["id"],
        "body": row["body"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "deleted": bool(row["deleted"]),
    }


# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------
@app.on_event("startup")
def startup():
    init_db()


@app.post("/api/auth/register", status_code=201)
def register(body: AuthIn, request: Request):
    if not allow_register(_client_ip(request)):
        raise HTTPException(429, "too many registration attempts, try again later")
    with get_db() as db:
        cur = db.execute("SELECT id FROM users WHERE username = ?", (body.username,))
        if cur.fetchone():
            raise HTTPException(409, "username already taken")
        db.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (body.username, hash_password(body.password), _now()),
        )
        user_id = db.execute(
            "SELECT id FROM users WHERE username = ?", (body.username,)
        ).fetchone()["id"]
    return AuthOut(token=make_token(user_id, body.username), username=body.username)


@app.post("/api/auth/login")
def login(body: AuthIn, request: Request):
    if not allow_login(_client_ip(request)):
        raise HTTPException(429, "too many login attempts, try again later")
    with get_db() as db:
        row = db.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (body.username,),
        ).fetchone()
    # Same message for unknown user and wrong password (anti-enumeration).
    if not row or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(401, "invalid username or password")
    return AuthOut(token=make_token(row["id"], row["username"]), username=row["username"])


# --------------------------------------------------------------------------
# Entries
# --------------------------------------------------------------------------
@app.get("/api/entries")
def list_entries(user=Depends(_current_user)):
    user_id, _ = user
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM entries WHERE user_id = ? ORDER BY created_at", (user_id,)
        ).fetchall()
    return [_row_to_out(r) for r in rows]


@app.post("/api/entries", status_code=201)
def upsert_entry(body: EntryIn, user=Depends(_current_user)):
    user_id, _ = user
    with get_db() as db:
        existing = db.execute(
            "SELECT updated_at FROM entries WHERE id = ? AND user_id = ?",
            (body.id, user_id),
        ).fetchone()
        if existing and body.updated_at < existing["updated_at"]:
            raise HTTPException(409, "server copy is newer")
        db.execute(
            """
            INSERT INTO entries (id, user_id, body, created_at, updated_at, deleted)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id, user_id) DO UPDATE SET
                body = excluded.body,
                updated_at = excluded.updated_at,
                deleted = excluded.deleted
            """,
            (body.id, user_id, body.body, body.created_at, body.updated_at, int(body.deleted)),
        )
        row = db.execute(
            "SELECT * FROM entries WHERE id = ? AND user_id = ?", (body.id, user_id)
        ).fetchone()
    _broadcast(user_id, "created", _row_to_out(row))
    return _row_to_out(row)


@app.put("/api/entries/{entry_id}")
def update_entry(entry_id: str, body: EntryUpdate, user=Depends(_current_user)):
    user_id, _ = user
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id)
        ).fetchone()
        if not row:
            raise HTTPException(404, "entry not found")
        db.execute(
            "UPDATE entries SET body = ?, updated_at = ?, deleted = ? WHERE id = ? AND user_id = ?",
            (body.body, body.updated_at, int(body.deleted), entry_id, user_id),
        )
        row = db.execute(
            "SELECT * FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id)
        ).fetchone()
    _broadcast(user_id, "updated", _row_to_out(row))
    return _row_to_out(row)


@app.delete("/api/entries/{entry_id}")
def delete_entry(entry_id: str, user=Depends(_current_user)):
    user_id, _ = user
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id)
        ).fetchone()
        if not row:
            raise HTTPException(404, "entry not found")
        now = _now()
        db.execute(
            "UPDATE entries SET deleted = 1, updated_at = ? WHERE id = ? AND user_id = ?",
            (now, entry_id, user_id),
        )
        row = db.execute(
            "SELECT * FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id)
        ).fetchone()
    _broadcast(user_id, "deleted", _row_to_out(row))
    return _row_to_out(row)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


# --------------------------------------------------------------------------
# Realtime
# --------------------------------------------------------------------------
_connections: dict[int, set] = {}
_conn_lock = threading.Lock()
_loop: asyncio.AbstractEventLoop | None = None


def _connections_for(user_id: int) -> set:
    with _conn_lock:
        return _connections.setdefault(user_id, set())


def _broadcast(user_id: int, action: str, entry: dict):
    payload = json.dumps({"type": "entry", "action": action, "entry": entry})
    for ws in list(_connections_for(user_id)):
        try:
            # Endpoints run sync in a threadpool; schedule the coroutine on the
            # event loop thread safely.
            if _loop is not None:
                asyncio.run_coroutine_threadsafe(ws.send_text(payload), _loop)
        except Exception:
            pass


@app.websocket("/ws")
async def ws_realtime(ws: WebSocket):
    global _loop
    if _loop is None:
        _loop = asyncio.get_running_loop()
    # The token is sent as the FIRST client message, never in the URL, so it
    # does not leak into access logs / proxy logs.
    await ws.accept()
    try:
        raw = await ws.receive_text()
    except WebSocketDisconnect:
        return
    try:
        msg = json.loads(raw)
        token = msg.get("token", "")
    except (json.JSONDecodeError, AttributeError):
        token = ""
    payload = decode_token(token)
    if not payload:
        await ws.send_text(json.dumps({"type": "error", "reason": "unauthorized"}))
        await ws.close(code=4001)
        return
    user_id = int(payload["sub"])
    await ws.send_text(json.dumps({"type": "auth_ok"}))
    _connections_for(user_id).add(ws)
    try:
        with get_db() as db:
            rows = db.execute(
                "SELECT * FROM entries WHERE user_id = ? ORDER BY created_at", (user_id,)
            ).fetchall()
        await ws.send_text(
            json.dumps({"type": "snapshot", "entries": [_row_to_out(r) for r in rows]})
        )
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        _connections_for(user_id).discard(ws)
