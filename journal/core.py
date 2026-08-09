import json
import os
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_FILE = "journal.md"

CRED_FILE = "~/.config/journal/credentials.json"


def _cred_path() -> Path:
    return Path(CRED_FILE).expanduser()


def _stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def entry_line(text: str, when: datetime | None = None) -> str:
    when = when or datetime.now().astimezone()
    stamp = when.isoformat(timespec="seconds")
    return f"- {stamp} {text}"


def _parse_line(line: str) -> dict | None:
    """Parse `- <timestamp> <body>` into {id, body, created_at, updated_at}."""
    line = line.strip()
    if not line.startswith("- "):
        return None
    rest = line[2:]
    parts = rest.split(" ", 1)
    if len(parts) != 2:
        return None
    ts, body = parts
    return {
        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, ts + "|" + body)),
        "body": body,
        "created_at": ts,
        "updated_at": ts,
    }


def append_entry(path, text: str, when: datetime | None = None) -> str:
    line = entry_line(text, when)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return line


def read_entries(path):
    p = Path(path)
    if not p.exists():
        return []
    return [l for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("- ")]


def read_entries_parsed(path) -> list[dict]:
    out = []
    for line in read_entries(path):
        e = _parse_line(line)
        if e:
            out.append(e)
    return out


def day_count(path) -> int:
    days = set()
    for line in read_entries(path):
        parts = line.split()
        if len(parts) >= 2:
            days.add(parts[1][:10])
    return len(days)


# --------------------------------------------------------------------------
# Sync client (talk to journal-server)
# --------------------------------------------------------------------------
class SyncError(Exception):
    pass


class _Client:
    def __init__(self, base: str, token: str):
        self.base = base.rstrip("/")
        self.token = token

    def _request(self, method: str, path: str, body=None):
        req = urllib.request.Request(self.base + path, method=method)
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {self.token}")
        data = json.dumps(body).encode() if body is not None else None
        try:
            with urllib.request.urlopen(req, data=data, timeout=15) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            detail = ""
            try:
                detail = json.loads(e.read())["detail"]
            except Exception:
                pass
            raise SyncError(f"HTTP {e.code}: {detail or e.reason}") from None


def login_or_register(base: str, username: str, password: str, register: bool = False):
    client = _Client(base, "")
    path = "/api/auth/register" if register else "/api/auth/login"
    try:
        resp = client._request("POST", path, {"username": username, "password": password})
    except SyncError as e:
        # Try the other endpoint if the intent was unclear.
        if "409" in str(e) or "invalid" in str(e):
            alt = "/api/auth/login" if register else "/api/auth/register"
            resp = _Client(base, "")._request("POST", alt, {"username": username, "password": password})
        else:
            raise
    return resp["token"]


def save_credentials(base: str, username: str, token: str):
    path = _cred_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except Exception:
            pass
    existing[base] = {"username": username, "token": token}
    path.write_text(json.dumps(existing, indent=2))
    os.chmod(path, 0o600)


def load_credentials(base: str):
    path = _cred_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except Exception:
        return None
    return data.get(base)


def sync_push(pull: bool, push: bool, path: str, base: str, token: str) -> list[str]:
    """Merge local file with server. Returns a list of human messages."""
    client = _Client(base, token)
    local = {e["id"]: e for e in read_entries_parsed(path)}
    remote_list = client._request("GET", "/api/entries")
    remote = {e["id"]: e for e in remote_list if not e["deleted"]}
    msgs: list[str] = []

    if pull:
        # Apply server entries that the local file doesn't have or are newer.
        local_by_ts = {(e["created_at"], e["body"]) for e in local.values()}
        applied = 0
        for e in remote.values():
            if e["id"] not in local or e["updated_at"] > local[e["id"]]["updated_at"]:
                if (e["created_at"], e["body"]) not in local_by_ts:
                    _append_parsed(path, e)
                    applied += 1
        if applied:
            msgs.append(f"pulled {applied} entries from server")

    if push:
        pushed = 0
        for e in local.values():
            if e["id"] not in remote or e["updated_at"] > remote[e["id"]]["updated_at"]:
                client._request("POST", "/api/entries", {**e, "deleted": False})
                pushed += 1
        if pushed:
            msgs.append(f"pushed {pushed} entries to server")

    if not msgs:
        msgs.append("already in sync")
    return msgs


def _append_parsed(path: str, entry: dict):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(f"- {entry['created_at']} {entry['body']}\n")
