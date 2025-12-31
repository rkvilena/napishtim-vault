"""Main application entry point for NapishtimVault."""

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from .ui import (
    LoginWidget, SetupWidget, VaultWidget, 
    CredentialDialog, ConfirmDialog, ChangeMasterPasswordDialog, DARK_STYLESHEET
)
from .storage import Database, CredentialRepository, ConfigRepository
from .crypto import (
    derive_fernet_key,
    generate_salt,
    make_verifier_token,
    verify_verifier_token,
    encrypt,
    decrypt,
)
from .security import ClipboardManager, IdleMonitor
from .models import VaultState, Credential


class NapishtimVault(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # State
        self._vault_state = VaultState()
        self._db: Optional[Database] = None
        self._config_repo: Optional[ConfigRepository] = None
        self._cred_repo: Optional[CredentialRepository] = None
        
        # Security managers
        self._clipboard = ClipboardManager(self)
        self._idle_monitor = IdleMonitor(self)
        
        # Connect security signals
        self._idle_monitor.idle_timeout.connect(self._on_idle_timeout)
        self._idle_monitor.minimized.connect(self._on_minimized)
        self._clipboard.cleared.connect(self._on_clipboard_cleared)
        
        self._init_ui()
        self._init_database()
    
    def _init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("NapishtimVault")
        self.setMinimumSize(500, 600)
        self.resize(550, 700)
        
        # Apply dark theme
        self.setStyleSheet(DARK_STYLESHEET)
        
        # Central stacked widget for switching views
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)
        
        # Create views
        self._setup_widget = SetupWidget()
        self._setup_widget.setup_complete.connect(self._on_setup_complete)
        self._stack.addWidget(self._setup_widget)
        
        self._login_widget = LoginWidget()
        self._login_widget.login_success.connect(self._on_login)
        self._login_widget.reset_requested.connect(self._on_reset_requested)
        self._stack.addWidget(self._login_widget)
        
        self._vault_widget = VaultWidget()
        self._vault_widget.add_clicked.connect(self._on_add_credential)
        self._vault_widget.edit_clicked.connect(self._on_edit_credential)
        self._vault_widget.delete_clicked.connect(self._on_delete_credential)
        self._vault_widget.copy_username.connect(self._on_copy_username)
        self._vault_widget.copy_password.connect(self._on_copy_password)
        self._vault_widget.lock_clicked.connect(self._lock_vault)
        self._vault_widget.change_master_password_clicked.connect(self._on_change_master_password)
        self._vault_widget.search_changed.connect(self._on_search)
        self._stack.addWidget(self._vault_widget)
    
    def _init_database(self):
        """Initialize database connection."""
        # Create database without encryption key first (for config)
        self._db = Database()
        self._db.connect()
        self._config_repo = ConfigRepository(self._db)
        
        # Check if vault is initialized
        if self._config_repo.is_initialized():
            self._show_login()
        else:
            self._show_setup()
    
    def _show_setup(self):
        """Show the setup screen."""
        self._stack.setCurrentWidget(self._setup_widget)
    
    def _show_login(self):
        """Show the login screen."""
        self._login_widget.clear()
        self._stack.setCurrentWidget(self._login_widget)
    
    def _show_vault(self):
        """Show the vault screen."""
        self._stack.setCurrentWidget(self._vault_widget)
        self._refresh_credentials()
        
        # Start idle monitoring
        self._idle_monitor.start(self)
    
    def _on_setup_complete(self, password: str):
        """Handle master password setup."""
        try:
            # Generate salt and derive Fernet key
            salt = generate_salt()
            fernet_key = derive_fernet_key(password, salt)

            # Store salt + verifier token (used to validate password on login)
            self._config_repo.set_kdf_salt(salt)
            self._config_repo.set_verifier_token(make_verifier_token(fernet_key))

            # Unlock vault
            self._vault_state.unlock(fernet_key)

            # Create credential repository with encryption key
            self._cred_repo = CredentialRepository(self._db, fernet_key)
            
            self._show_vault()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create vault: {e}")
    
    def _on_login(self, password: str):
        """Handle login attempt."""
        try:
            salt = self._config_repo.get_kdf_salt()
            token = self._config_repo.get_verifier_token()
            if not salt or not token:
                self._login_widget.show_error("Vault corrupted: missing verifier")
                return

            fernet_key = derive_fernet_key(password, salt)

            if not verify_verifier_token(fernet_key, token):
                self._login_widget.show_error("Incorrect password")
                return

            # Unlock vault
            self._vault_state.unlock(fernet_key)

            # Create credential repository
            self._cred_repo = CredentialRepository(self._db, fernet_key)
            
            self._show_vault()
            
        except Exception as e:
            self._login_widget.show_error(f"Login failed: {e}")

    def _on_reset_requested(self):
        """Reset the entire vault (deletes local DB) and return to setup."""
        if not ConfirmDialog.confirm(
            "Reset Vault",
            "This will permanently delete all saved credentials on this device. Continue?",
            self,
        ):
            return

        try:
            # Stop monitoring + clear transient secrets
            self._idle_monitor.stop()
            self._clipboard.force_clear()
            self._vault_state.lock()
            self._cred_repo = None

            db_path: Optional[Path] = None
            if self._db is not None:
                db_path = self._db.db_path
                self._db.close()
                self._db = None

            # Fall back if db was not initialized for some reason
            if db_path is None:
                from .storage.db import get_db_path

                db_path = get_db_path()

            if db_path.exists():
                db_path.unlink()

            # Recreate fresh DB and show setup
            self._db = Database()
            self._db.connect()
            self._config_repo = ConfigRepository(self._db)
            self._show_setup()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset vault: {e}")
    
    def _lock_vault(self):
        """Lock the vault and return to login."""
        # Stop idle monitoring
        self._idle_monitor.stop()
        
        # Clear clipboard
        self._clipboard.force_clear()
        
        # Lock state (wipes keys)
        self._vault_state.lock()
        self._cred_repo = None
        
        # Clear vault UI
        self._vault_widget.set_credentials([])
        self._vault_widget.clear_search()
        
        # Show login
        self._show_login()
    
    def _on_idle_timeout(self):
        """Handle idle timeout - auto-lock."""
        self._lock_vault()
        self._login_widget.show_error("Locked due to inactivity")
    
    def _on_minimized(self):
        """Handle window minimized - auto-lock."""
        self._lock_vault()
    
    def _on_clipboard_cleared(self):
        """Handle clipboard cleared."""
        if self._vault_state.is_unlocked:
            self._vault_widget.show_status("📋 Clipboard cleared")
    
    def _refresh_credentials(self, search_query: str = ""):
        """Refresh the credentials list."""
        if not self._cred_repo:
            return
        
        try:
            if search_query:
                credentials = self._cred_repo.search(search_query)
            else:
                credentials = self._cred_repo.get_all()
            
            self._vault_widget.set_credentials(credentials)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load credentials: {e}")
    
    def _on_search(self, query: str):
        """Handle search input change."""
        self._refresh_credentials(query)
    
    def _on_add_credential(self):
        """Show add credential dialog."""
        dialog = CredentialDialog(parent=self)
        if dialog.exec() and dialog.result_credential:
            try:
                self._cred_repo.create(dialog.result_credential)
                self._refresh_credentials()
                self._vault_widget.show_status("✓ Credential added")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to add credential: {e}")
    
    def _on_edit_credential(self, credential_id: int):
        """Show edit credential dialog."""
        credential = self._cred_repo.get(credential_id)
        if not credential:
            return
        
        dialog = CredentialDialog(credential, parent=self)
        if dialog.exec() and dialog.result_credential:
            try:
                self._cred_repo.update(dialog.result_credential)
                self._refresh_credentials()
                self._vault_widget.show_status("✓ Credential updated")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to update credential: {e}")
    
    def _on_delete_credential(self, credential_id: int):
        """Handle delete credential."""
        credential = self._cred_repo.get(credential_id)
        if not credential:
            return
        
        if ConfirmDialog.confirm(
            "Delete Credential",
            f"Are you sure you want to delete '{credential.title}'?",
            self
        ):
            try:
                self._cred_repo.delete(credential_id)
                self._refresh_credentials()
                self._vault_widget.show_status("✓ Credential deleted")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete credential: {e}")
    
    def _on_copy_username(self, credential_id: int):
        """Copy username to clipboard."""
        credential = self._cred_repo.get(credential_id)
        if credential:
            self._clipboard.copy(credential.username)
            self._vault_widget.show_status("📋 Username copied (clears in 30s)")
    
    def _on_copy_password(self, credential_id: int):
        """Copy password to clipboard."""
        credential = self._cred_repo.get(credential_id)
        if credential:
            self._clipboard.copy(credential.password)
            self._vault_widget.show_status("📋 Password copied (clears in 30s)")

    def _on_change_master_password(self):
        """Change the master password and re-encrypt all stored secrets."""
        if not self._db or not self._config_repo:
            QMessageBox.warning(self, "Error", "Vault not initialized")
            return

        dialog = ChangeMasterPasswordDialog(self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        current_password = dialog.current_password
        new_password = dialog.new_password

        try:
            salt = self._config_repo.get_kdf_salt()
            token = self._config_repo.get_verifier_token()
            if not salt or not token:
                QMessageBox.warning(self, "Error", "Vault corrupted: missing verifier")
                return

            old_key = derive_fernet_key(current_password, salt)
            if not verify_verifier_token(old_key, token):
                QMessageBox.warning(self, "Incorrect Password", "Current master password is incorrect")
                return

            new_salt = generate_salt()
            new_key = derive_fernet_key(new_password, new_salt)

            conn = self._db.connection
            conn.execute("BEGIN")
            try:
                cursor = conn.execute("SELECT id, password FROM credentials")
                rows = cursor.fetchall()

                for row in rows:
                    plaintext = decrypt(row["password"], old_key)
                    new_ciphertext = encrypt(plaintext, new_key)
                    conn.execute(
                        "UPDATE credentials SET password = ?, updated_at = datetime('now') WHERE id = ?",
                        (new_ciphertext, row["id"]),
                    )

                # Update config last
                conn.execute(
                    "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                    ("kdf_salt", new_salt),
                )
                conn.execute(
                    "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                    ("verifier_token", make_verifier_token(new_key)),
                )

                conn.commit()
            except Exception:
                conn.rollback()
                raise

            # Swap in-memory key and repositories
            self._vault_state.unlock(new_key)
            self._cred_repo = CredentialRepository(self._db, new_key)
            self._refresh_credentials(self._vault_widget.search_input.text())
            self._vault_widget.show_status("✓ Master password updated")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to change master password: {e}")
    
    def closeEvent(self, event):
        """Handle window close."""
        # Lock vault before closing
        if self._vault_state.is_unlocked:
            self._vault_state.lock()
        
        # Clear clipboard
        self._clipboard.force_clear()
        
        # Close database
        if self._db:
            self._db.close()
        
        event.accept()


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("NapishtimVault")
    app.setOrganizationName("NapishtimVault")
    
    # Set app-wide style
    app.setStyle("Fusion")
    
    window = NapishtimVault()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
