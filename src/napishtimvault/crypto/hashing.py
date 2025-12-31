"""Master password verification helpers.

With the sqlite3 + Fernet design, we avoid storing a separate password hash.
Instead, we store an encrypted verifier token and test whether it decrypts.
"""

from cryptography.fernet import Fernet, InvalidToken

_VERIFIER_PLAINTEXT = b"napishtimvault::verifier"


def make_verifier_token(fernet_key: bytes) -> bytes:
    """Create an encrypted verifier token to store in the DB."""
    return Fernet(fernet_key).encrypt(_VERIFIER_PLAINTEXT)


def verify_verifier_token(fernet_key: bytes, token: bytes) -> bool:
    """Return True if token decrypts with the provided key."""
    try:
        plain = Fernet(fernet_key).decrypt(token)
        return plain == _VERIFIER_PLAINTEXT
    except InvalidToken:
        return False
