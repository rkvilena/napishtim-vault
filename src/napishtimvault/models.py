"""Data models for NapishtimVault."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Credential:
    """Represents a stored credential entry."""
    
    title: str
    username: str
    password: str
    url: Optional[str] = None
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.title:
            raise ValueError("Title is required")
        if not self.username:
            raise ValueError("Username is required")
        if not self.password:
            raise ValueError("Password is required")


@dataclass
class VaultState:
    """Represents the current state of the vault."""
    
    is_unlocked: bool = False
    encryption_key: Optional[bytes] = None
    db_key: Optional[bytes] = None
    
    def lock(self) -> None:
        """Lock the vault and wipe sensitive data."""
        self.is_unlocked = False
        
        # Attempt to wipe keys from memory
        if self.encryption_key:
            key_array = bytearray(self.encryption_key)
            for i in range(len(key_array)):
                key_array[i] = 0
            self.encryption_key = None
        
        if self.db_key:
            db_array = bytearray(self.db_key)
            for i in range(len(db_array)):
                db_array[i] = 0
            self.db_key = None
    
    def unlock(self, encryption_key: bytes, db_key: Optional[bytes] = None) -> None:
        """Unlock the vault with the given keys."""
        self.encryption_key = encryption_key
        self.db_key = db_key
        self.is_unlocked = True


@dataclass
class AppConfig:
    """Application configuration."""
    
    idle_timeout_minutes: int = 5
    clipboard_clear_seconds: int = 30
    minimize_to_tray: bool = False
    start_minimized: bool = False


@dataclass
class DeletionRecord:
    """Represents an entry in deletion history."""

    title: str
    username: str
    deleted_at: str


@dataclass
class AuditEvent:
    """Represents an audit log event shown in History."""

    title: str
    action: str  # created | edited | deleted
    occurred_at: str
