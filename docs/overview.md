# NapishtimVault Project Overview

This document explains the codebase structure, the main runtime flow, the key algorithms, and the design choices so you can fully understand how the app works.

## What the App Is

NapishtimVault is a local-only password manager with a PyQt6 GUI. It stores credentials in a local SQLite database, encrypts passwords using a key derived from the master password, and locks itself after inactivity or minimization.

## Repository Structure

- run.py: Lightweight launcher that ensures src/ is on sys.path and runs the app.
- src/napishtimvault/app.py: Main application window, lifecycle, and feature wiring.
- src/napishtimvault/ui/: GUI widgets, dialogs, and styles.
  - login.py: Setup and login screens.
  - vault.py: Main vault list view and item widgets.
  - dialogs.py: Add/edit credential dialog, history, confirm, and master password change.
  - styles.py: Dark theme stylesheet.
- src/napishtimvault/storage/: Persistence and data access.
  - db.py: SQLite connection and schema.
  - repo.py: Repositories for config and credentials.
- src/napishtimvault/crypto/: Key derivation and encryption helpers.
  - kdf.py: Scrypt key derivation.
  - aead.py: Fernet encryption/decryption.
  - hashing.py: Verifier token creation/verification.
- src/napishtimvault/security/: Runtime protections.
  - clipboard.py: Auto-clear clipboard manager.
  - idle.py: Idle monitor for auto-lock.
- src/napishtimvault/models.py: Dataclasses for app and domain models.

## Main Program Flow

1. App startup
   - run.py loads src/ and calls napishtimvault.app.main().
   - app.py creates a QApplication and a NapishtimVault main window.
2. Initialization
   - NapishtimVault builds the UI stack (Setup, Login, Vault).
   - Database is opened and schema is initialized if needed.
   - If config is missing, show Setup; otherwise show Login.
3. Setup flow (first run)
   - User sets a master password in SetupWidget.
   - A random salt is generated.
   - A key is derived with Scrypt.
   - An encrypted verifier token is stored in the config table.
   - Vault is unlocked in memory and the Vault view is shown.
4. Login flow (subsequent runs)
   - Stored salt and verifier token are loaded.
   - A key is derived from the entered password and salt.
   - Verifier token decryption succeeds only if the password is correct.
   - Vault is unlocked and the Vault view is shown.
5. Vault usage
   - Credentials are loaded from the database and displayed.
   - Add/Edit/Delete actions open dialogs and call repository methods.
   - Search queries run a SQL LIKE search on title or username.
6. Auto-lock and shutdown
   - IdleMonitor starts when the vault is visible.
   - On idle timeout or minimization, the vault locks and wipes keys.
   - Closing the app also locks and clears clipboard contents.

## Data Model and Storage

### Database Location
- The database file is stored under the OS user data directory:
  - Windows: %LOCALAPPDATA%/NapishtimVault/vault.db
  - Linux/macOS: ~/.local/share/NapishtimVault/vault.db

### Schema
- config: key/value store for salt and verifier token.
- credentials: encrypted passwords, plus metadata fields.
- audit_log: creation/edit/deletion events with timestamps.

### Repositories
- ConfigRepository reads/writes the KDF salt and verifier token.
- CredentialRepository handles CRUD and search.
- Passwords are encrypted/decrypted on the repository boundary so the UI deals with plaintext objects.

## Cryptography and Key Management

- Key derivation: Scrypt with a random 16-byte salt, producing a 32-byte key (kdf.py).
- Salt lifecycle: generated once at setup, stored in config, reused for logins, and replaced only when the master password is changed.
- Key format: Scrypt output is base64-encoded into a Fernet key for use with cryptography’s Fernet API.
- Password encryption: credential passwords are encrypted/decrypted at the repository boundary using Fernet; usernames remain plaintext for search.
- Master password verification: a fixed verifier plaintext is encrypted and stored; login succeeds only if it decrypts with the derived key.
- Memory hygiene: when locking, VaultState overwrites key bytes and clears references.

## Security Features and Behaviors

- Auto-lock after inactivity using IdleMonitor (3 minutes by default).
- Auto-lock on window minimization.
- Clipboard auto-clear after 30 seconds via ClipboardManager.
- Credential passwords are encrypted at rest; usernames remain plaintext to support search.

## UI Architecture

- QStackedWidget handles view switching between Setup, Login, and Vault.
- Signals connect UI widgets to app-level handlers:
  - LoginWidget emits login_success.
  - SetupWidget emits setup_complete.
  - VaultWidget emits add/edit/delete/copy/lock/search/history actions.
- Dialogs return structured results (CredentialDialog returns a Credential).

## Audit and History

- Each create/edit/delete writes a row into audit_log.
- HistoryDialog shows the latest events (most recent first).

## Key Files to Read First

- app.py: end-to-end flow, security wiring, and UI orchestration.
- storage/repo.py: how credentials and history are persisted.
- crypto/kdf.py and crypto/aead.py: how keys and encryption are done.
- ui/vault.py and ui/dialogs.py: how user actions map to app handlers.
