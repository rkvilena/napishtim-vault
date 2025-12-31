"""Fernet authenticated encryption."""

import base64
from typing import Union

from cryptography.fernet import Fernet


def _normalize_fernet_key(key: bytes) -> bytes:
    """
    Fernet expects a urlsafe-base64-encoded 32-byte key.

    We accept either:
    - raw 32 bytes (will be base64-encoded)
    - a Fernet key (base64 bytes, typically length 44)
    """
    if len(key) == 32:
        return base64.urlsafe_b64encode(key)
    return key


def encrypt(plaintext: str, key: bytes) -> bytes:
    """Encrypt a string and return a Fernet token (bytes)."""
    f = Fernet(_normalize_fernet_key(key))
    return f.encrypt(plaintext.encode("utf-8"))


def decrypt(ciphertext: bytes, key: bytes) -> str:
    """Decrypt a Fernet token and return the plaintext string."""
    f = Fernet(_normalize_fernet_key(key))
    return f.decrypt(ciphertext).decode("utf-8")


def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    """Encrypt bytes and return a Fernet token (bytes)."""
    f = Fernet(_normalize_fernet_key(key))
    return f.encrypt(data)


def decrypt_bytes(ciphertext: bytes, key: bytes) -> bytes:
    """Decrypt a Fernet token and return plaintext bytes."""
    f = Fernet(_normalize_fernet_key(key))
    return f.decrypt(ciphertext)
