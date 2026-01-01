"""Repository classes for data access."""

from typing import Optional, List

from ..crypto import decrypt, encrypt
from ..models import Credential, AuditEvent
from .db import Database


class ConfigRepository:
    """Repository for application configuration."""

    def __init__(self, db: Database):
        self.db = db

    def get(self, key: str) -> Optional[bytes]:
        """Get a config value by key."""
        cursor = self.db.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else None

    def set(self, key: str, value: bytes) -> None:
        """Set a config value."""
        self.db.execute(
            "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value)
        )
        self.db.commit()

    def delete(self, key: str) -> None:
        """Delete a config value."""
        self.db.execute("DELETE FROM config WHERE key = ?", (key,))
        self.db.commit()

    def get_kdf_salt(self) -> Optional[bytes]:
        """Get the salt used for key derivation."""
        return self.get("kdf_salt")

    def set_kdf_salt(self, salt: bytes) -> None:
        """Store the key derivation salt."""
        self.set("kdf_salt", salt)

    def get_verifier_token(self) -> Optional[bytes]:
        """Get the encrypted verifier token used to validate master password."""
        return self.get("verifier_token")

    def set_verifier_token(self, token: bytes) -> None:
        """Store encrypted verifier token."""
        self.set("verifier_token", token)

    def is_initialized(self) -> bool:
        """Check if the vault has been initialized with a master password."""
        return self.get_kdf_salt() is not None and self.get_verifier_token() is not None


class CredentialRepository:
    """Repository for credential CRUD operations."""

    def __init__(self, db: Database, fernet_key: bytes):
        self.db = db
        self._key = fernet_key

    def _encrypt_password(self, value: str) -> bytes:
        return encrypt(value, self._key)

    def _decrypt_password(self, value: bytes) -> str:
        return decrypt(value, self._key)

    def create(self, credential: Credential) -> int:
        """
        Create a new credential.

        Returns:
            The ID of the created credential
        """
        conn = self.db.connection
        conn.execute("BEGIN")
        try:
            cursor = conn.execute(
                """
                INSERT INTO credentials (title, username, password, url, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    credential.title,
                    credential.username,
                    self._encrypt_password(credential.password),
                    credential.url,
                    credential.notes,
                ),
            )

            conn.execute(
                "INSERT INTO audit_log (title, action) VALUES (?, ?)",
                (credential.title, "created"),
            )

            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise

    def get(self, credential_id: int) -> Optional[Credential]:
        """Get a credential by ID."""
        cursor = self.db.execute(
            """
            SELECT id, title, username, password, url, notes, created_at, updated_at
            FROM credentials WHERE id = ?
            """,
            (credential_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        return Credential(
            id=row["id"],
            title=row["title"],
            username=row["username"],
            password=self._decrypt_password(row["password"]),
            url=row["url"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def get_all(self) -> List[Credential]:
        """Get all credentials."""
        cursor = self.db.execute(
            """
            SELECT id, title, username, password, url, notes, created_at, updated_at
            FROM credentials ORDER BY title
            """
        )

        credentials = []
        for row in cursor.fetchall():
            credentials.append(
                Credential(
                    id=row["id"],
                    title=row["title"],
                    username=row["username"],
                    password=self._decrypt_password(row["password"]),
                    url=row["url"],
                    notes=row["notes"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            )
        return credentials

    def update(self, credential: Credential) -> bool:
        """
        Update an existing credential.

        Returns:
            True if updated, False if not found
        """
        conn = self.db.connection
        conn.execute("BEGIN")
        try:
            cursor = conn.execute(
                """
                UPDATE credentials
                SET title = ?, username = ?, password = ?, url = ?, notes = ?,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (
                    credential.title,
                    credential.username,
                    self._encrypt_password(credential.password),
                    credential.url,
                    credential.notes,
                    credential.id,
                ),
            )

            if cursor.rowcount > 0:
                conn.execute(
                    "INSERT INTO audit_log (title, action) VALUES (?, ?)",
                    (credential.title, "edited"),
                )

            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise

    def delete(self, credential_id: int) -> bool:
        """
        Delete a credential.

        Returns:
            True if deleted, False if not found
        """
        # Fetch minimal info for history before deleting.
        row = self.db.execute(
            "SELECT title FROM credentials WHERE id = ?",
            (credential_id,),
        ).fetchone()
        if not row:
            return False

        conn = self.db.connection
        conn.execute("BEGIN")
        try:
            conn.execute(
                "INSERT INTO audit_log (title, action) VALUES (?, ?)",
                (row["title"], "deleted"),
            )
            cursor = conn.execute(
                "DELETE FROM credentials WHERE id = ?", (credential_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise

    def get_audit_events(self, limit: int = 200) -> List[AuditEvent]:
        """Return recent audit log events (most recent first)."""
        cursor = self.db.execute(
            """
            SELECT title, action, occurred_at
            FROM audit_log
            ORDER BY occurred_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )

        events: List[AuditEvent] = []
        for row in cursor.fetchall():
            events.append(
                AuditEvent(
                    title=row["title"],
                    action=row["action"],
                    occurred_at=row["occurred_at"],
                )
            )
        return events

    def search(self, query: str) -> List[Credential]:
        """
        Search credentials by title or username.

        Username is stored in plaintext specifically to support searching.
        """
        like = f"%{query}%"
        cursor = self.db.execute(
            """
            SELECT id, title, username, password, url, notes, created_at, updated_at
            FROM credentials
            WHERE title LIKE ? OR username LIKE ?
            ORDER BY title
            """,
            (like, like),
        )

        results: List[Credential] = []
        for row in cursor.fetchall():
            results.append(
                Credential(
                    id=row["id"],
                    title=row["title"],
                    username=row["username"],
                    password=self._decrypt_password(row["password"]),
                    url=row["url"],
                    notes=row["notes"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            )
        return results
