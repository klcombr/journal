"""In-memory rate limiting for authentication endpoints.

Implements a sliding window per (key, endpoint). Used to slow down
credential stuffing / brute force without introducing a dependency.
Not distributed — for a single-node deployment this is sufficient;
behind multiple workers use a shared store (Redis) instead.
"""

import threading
import time
from collections import defaultdict, deque

_lock = threading.Lock()
_hits: dict[str, deque] = defaultdict(deque)

LOGIN_MAX = 5          # allowed attempts
LOGIN_WINDOW = 60.0    # per window (seconds)
REGISTER_MAX = 3
REGISTER_WINDOW = 300.0


def _prune(now: float):
    for key in list(_hits):
        dq = _hits[key]
        while dq and now - dq[0] > LOGIN_WINDOW:
            dq.popleft()
        if not dq:
            del _hits[key]


def _check(key: str, max_attempts: int, window: float) -> bool:
    now = time.monotonic()
    with _lock:
        _prune(now)
        dq = _hits[key]
        dq.append(now)
        return len(dq) <= max_attempts


def allow_login(key: str) -> bool:
    return _check(f"login:{key}", LOGIN_MAX, LOGIN_WINDOW)


def allow_register(key: str) -> bool:
    return _check(f"register:{key}", REGISTER_MAX, REGISTER_WINDOW)
