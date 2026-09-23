from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings


def _fernet() -> Fernet:
    settings = get_settings()
    raw = settings.encryption_key.strip()

    if raw:
        key = raw.encode("utf-8")
        if len(key) != 44:
            digest = hashlib.sha256(raw.encode("utf-8")).digest()
            key = base64.urlsafe_b64encode(digest)
        return Fernet(key)

    if not settings.jwt_secret:
        raise RuntimeError("ENCRYPTION_KEY or JWT_SECRET is required to encrypt tokens")

    digest = hashlib.sha256(settings.jwt_secret.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_token(plain: str | None) -> str | None:
    if not plain:
        return None
    return _fernet().encrypt(plain.encode("utf-8")).decode("utf-8")


def decrypt_token(stored: str | None) -> str | None:
    if not stored:
        return None

    try:
        return _fernet().decrypt(stored.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        # Legacy plaintext tokens written before encryption shipped.
        return stored
