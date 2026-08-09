"""JWT auth helpers."""

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

SECRET = os.environ.get("JOURNAL_SECRET") or secrets.token_hex(32)
ALGO = "HS256"
TOKEN_TTL = timedelta(days=30)
AUDIENCE = "journal"
# ASVS v5.0 (May 2025): PBKDF2-HMAC-SHA-256 requires >= 600,000 iterations.
PBKDF2_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS)
    return f"pbkdf2-sha256${PBKDF2_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iterations, salt, expected = stored.split("$", 3)
    except ValueError:
        return False
    if scheme != "pbkdf2-sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
    return hmac.compare_digest(digest.hex(), expected)


def make_token(user_id: int, username: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "username": username,
        "aud": AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": now + TOKEN_TTL,
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def decode_token(token: str):
    try:
        return jwt.decode(
            token, SECRET, algorithms=[ALGO], audience=AUDIENCE, options={"require": ["exp", "nbf"]}
        )
    except jwt.PyJWTError:
        return None
