"""KDF utilities for deriving a Fernet key from the master password."""

import base64
import secrets

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

# Fernet requires a 32-byte key (then urlsafe-base64 encoded for storage/use).
KEY_LENGTH = 32
SALT_LENGTH = 16

# Scrypt parameters: keep moderate to remain responsive on desktop.
SCRYPT_N = 2**15
SCRYPT_R = 8
SCRYPT_P = 1


def generate_salt() -> bytes:
    """Generate a cryptographically secure random salt."""
    return secrets.token_bytes(SALT_LENGTH)


def derive_key_raw(password: str, salt: bytes) -> bytes:
    """Derive a 32-byte raw key using Scrypt."""
    kdf = Scrypt(
        salt=salt,
        length=KEY_LENGTH,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
    )
    return kdf.derive(password.encode("utf-8"))


def derive_fernet_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet key (urlsafe base64-encoded) from the password."""
    raw = derive_key_raw(password, salt)
    return base64.urlsafe_b64encode(raw)


def wipe_bytes(data: bytearray) -> None:
    """Overwrite a bytearray with zeros for memory hygiene."""
    for i in range(len(data)):
        data[i] = 0
