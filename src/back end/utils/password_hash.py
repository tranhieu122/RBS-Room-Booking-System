"""Password hashing helpers.

Uses PBKDF2-HMAC-SHA256 (100 000 iterations) with a random salt.
Stored format: ``pbkdf2:<iterations>:<hex_salt>:<hex_hash>``

Legacy SHA-256 hashes (plain 64-char hex) are still accepted during
verification so that existing accounts continue to work.  After a
successful legacy verification the caller can re-hash the password
with ``hash_password()`` to upgrade the stored hash.
"""
from __future__ import annotations
import hashlib
import os
import hmac

_ITERATIONS = 100_000
_ALGO       = "sha256"


# ── Public API ────────────────────────────────────────────────────────────────

def hash_password(raw_text: str) -> str:
    """Return a PBKDF2-hashed string (safe for storage)."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac(_ALGO, raw_text.encode("utf-8"),
                             salt, _ITERATIONS)
    return f"pbkdf2:{_ITERATIONS}:{salt.hex()}:{dk.hex()}"


def verify_password(raw_text: str, hashed_value: str) -> bool:
    """Verify *raw_text* against a stored hash.

    Accepts both the new ``pbkdf2:…`` format and legacy plain SHA-256.
    """
    if hashed_value.startswith("pbkdf2:"):
        return _verify_pbkdf2(raw_text, hashed_value)
    # Legacy: plain SHA-256 hex digest (64 chars)
    return hmac.compare_digest(sha256_hash(raw_text), hashed_value)


# ── Backward-compatible legacy helper ─────────────────────────────────────────

def sha256_hash(raw_text: str) -> str:
    """Plain SHA-256 — kept only for seed data and legacy verification."""
    return hashlib.sha256(raw_text.encode("utf-8")).hexdigest()


# ── Internal ──────────────────────────────────────────────────────────────────

def _verify_pbkdf2(raw_text: str, stored: str) -> bool:
    try:
        _, iters_s, salt_hex, hash_hex = stored.split(":")
        iters = int(iters_s)
        if iters < 10_000 or iters > 10_000_000:
            return False  # Reject implausible iteration count
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac(_ALGO, raw_text.encode("utf-8"),
                                 salt, iters)
        return hmac.compare_digest(dk.hex(), hash_hex)
    except (ValueError, TypeError):
        return False
