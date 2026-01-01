"""UI module for NapishtimVault."""

from .login import LoginWidget, SetupWidget
from .vault import VaultWidget
from .dialogs import (
    CredentialDialog,
    ConfirmDialog,
    ChangeMasterPasswordDialog,
    HistoryDialog,
)
from .styles import DARK_STYLESHEET

__all__ = [
    "LoginWidget",
    "SetupWidget",
    "VaultWidget",
    "CredentialDialog",
    "ConfirmDialog",
    "ChangeMasterPasswordDialog",
    "HistoryDialog",
    "DARK_STYLESHEET",
]
