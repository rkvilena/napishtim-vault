"""SQLite database connection and schema management."""

import os
import sqlite3
from pathlib import Path
from typing import Optional

HAS_SQLCIPHER = False


def get_data_dir() -> Path:
    """Get the application data directory."""
    if os.name == "nt":  # Windows
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:  # Linux/macOS
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    data_dir = base / "NapishtimVault"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_db_path() -> Path:
    """Get the database file path."""
    return get_data_dir() / "vault.db"


class Database:
    """SQLite database wrapper."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to database file (default: app data dir)
        """
        self.db_path = db_path or get_db_path()
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Open database connection."""
        self._conn = sqlite3.connect(str(self.db_path))

        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize database schema."""
        cursor = self._conn.cursor()

        # Config table for app settings (master password hash, salt, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value BLOB NOT NULL
            )
        """)

        # Credentials table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                username TEXT NOT NULL,
                password BLOB NOT NULL,
                url TEXT,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # Deletion history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deletion_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                username TEXT NOT NULL,
                deleted_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # Audit log table (creation/edit/deletion history)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                action TEXT NOT NULL,
                occurred_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        self._conn.commit()

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    @property
    def connection(self) -> sqlite3.Connection:
        """Get the active database connection."""
        if not self._conn:
            raise RuntimeError("Database not connected")
        return self._conn

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor."""
        return self.connection.execute(query, params)

    def commit(self) -> None:
        """Commit current transaction."""
        self.connection.commit()

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
