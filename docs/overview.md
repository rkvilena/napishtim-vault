# NapishtimVault - Architecture & System Design

This document describes **how the system is designed and how the code works**: architecture layers, runtime flow, data model, cryptography, and security internals.

> Looking for setup, usage, building, or backups? See the [README](../README.md).

> This document reflects the **current implementation** in `src/`. Historical/planned designs mentioning Argon2, AES-256-GCM, or SQLCipher are **not implemented**; the code uses Scrypt + Fernet + standard-library SQLite.

## 1. Architecture at a Glance

NapishtimVault is a single-process PyQt6 desktop app with a layered design:

    +-------------------------------------------------------+
    |                     UI Layer                          |
    |  login.py (Setup/Login)     vault.py (vault list)     |
    |  dialogs.py (add/edit/confirm/history/change-pwd)     |
    |  styles.py (dark theme)                               |
    +-----------------------|-------------------------------+
                            | Qt signals only
    +-----------------------v-------------------------------+
    |                Application Layer                      |
    |  app.py: NapishtimVault (QMainWindow)                 |
    |  - view switching (QStackedWidget)                    |
    |  - wires signals -> handlers                          |
    |  - owns VaultState, security managers, repositories   |
    +-----------|---------------------------|---------------+
                |                           |
    +-----------v-----------+   +-----------v---------------+
    |     Crypto Layer      |   |      Security Layer       |
    | kdf.py (Scrypt)       |   | idle.py (IdleMonitor)     |
    | aead.py (Fernet)      |   | clipboard.py (auto-clear) |
    | hashing.py (verifier) |   |                           |
    +-----------|-----------+   +---------------------------+
                |
    +-----------v-------------------------------------------+
    |                  Storage Layer                        |
    |  db.py  (Database: connection + schema)               |
    |  repo.py (ConfigRepository, CredentialRepository)     |
    +-------------------------------------------------------+
    |  models.py: Credential, VaultState, AuditEvent, ...   |
    +-------------------------------------------------------+

Key rule: **the UI never touches the database or keys directly.** Views emit signals; `app.py` handlers use repositories; repositories do encryption at their boundary; `models.py` dataclasses carry plaintext between layers.

## 2. Module Map

| Path | Responsibility |
|---|---|
| `run.py` | Launcher; puts `src/` on `sys.path`, calls `napishtimvault.app.main()` |
| `src/napishtimvault/app.py` | Main window, lifecycle, signal wiring, all feature handlers |
| `src/napishtimvault/models.py` | Dataclasses: `Credential`, `VaultState`, `AuditEvent`, `AppConfig`, `DeletionRecord` |
| `src/napishtimvault/ui/login.py` | `SetupWidget` (first run), `LoginWidget` (unlock + reset request) |
| `src/napishtimvault/ui/vault.py` | Vault list, per-entry action buttons, search box, status bar |
| `src/napishtimvault/ui/dialogs.py` | `CredentialDialog` (+ password generator), `ConfirmDialog`, `HistoryDialog`, `ChangeMasterPasswordDialog` |
| `src/napishtimvault/ui/styles.py` | Dark stylesheet (`DARK_STYLESHEET`) |
| `src/napishtimvault/storage/db.py` | SQLite connection, schema init, data-dir resolution |
| `src/napishtimvault/storage/repo.py` | `ConfigRepository`, `CredentialRepository` (CRUD + search + audit) |
| `src/napishtimvault/crypto/kdf.py` | Scrypt derivation, salt generation, `wipe_bytes` |
| `src/napishtimvault/crypto/aead.py` | Fernet encrypt/decrypt, key normalization |
| `src/napishtimvault/crypto/hashing.py` | Verifier token create/verify |
| `src/napishtimvault/security/idle.py` | `IdleMonitor`: app-wide event filter, 3-min timer, minimize detection |
| `src/napishtimvault/security/clipboard.py` | `ClipboardManager`: copy + 30s auto-clear |

Generated/local-only paths (not source): `.venv/`, `build/`, `dist/`, `NapishtimVault.spec`, `__pycache__/`, `src/.ruff_cache/`.

## 3. Runtime Flow

### 3.1 Startup

1. `run.py` inserts `src/` into `sys.path` and calls `napishtimvault.app.main()`.
2. `main()` creates the `QApplication` (name `NapishtimVault`, Fusion style) and shows the `NapishtimVault` main window.
3. The constructor builds three views into a `QStackedWidget` (Setup, Login, Vault), connects every UI signal to a handler, creates `ClipboardManager` and `IdleMonitor`, then opens the database.
4. `_init_database()` opens/creates `vault.db`, initializes the schema, and checks `ConfigRepository.is_initialized()`:
   - salt + verifier token present -> **Login** view
   - otherwise -> **Setup** view

### 3.2 Setup (first run)

1. `SetupWidget` collects password + confirmation (minimum 8 characters, validated in the UI).
2. It emits `setup_complete(password)`; the handler then:
   - generates a 16-byte salt (`generate_salt()`)
   - derives the Fernet key via Scrypt (`derive_fernet_key`)
   - stores `kdf_salt` and `verifier_token` (Fernet token over a fixed plaintext) in `config`
   - unlocks `VaultState`, creates `CredentialRepository(db, key)`, and shows the Vault

### 3.3 Login (subsequent runs)

1. `LoginWidget` emits `login_success(password)`.
2. The stored `kdf_salt` and `verifier_token` are loaded; the key is re-derived from the entered password.
3. `verify_verifier_token` succeeds **only** if the derived key decrypts the token back to the fixed verifier plaintext.
4. Success: unlock, create repository, show Vault. Failure: inline error — note there is **no rate limiting**.
5. The Login view also offers **Reset Vault**: after confirmation the app stops the idle monitor, force-clears the clipboard, locks state, closes and **deletes the DB file**, and returns to Setup.

### 3.4 Vault usage

- Every operation flows: UI signal -> handler -> repository method -> transaction (write + matching `audit_log` row) -> `_refresh_credentials` -> list rebuild.
- Search: `search_changed` -> `CredentialRepository.search(query)` -> SQL `LIKE` on plaintext `title`/`username`.
- Copy username/password: the handler fetches the credential (decrypting the password), then `ClipboardManager.copy(text)` starts the 30-second clear timer.
- History: fetches the latest 200 `audit_log` rows into `HistoryDialog`.

### 3.5 Locking and shutdown

- `IdleMonitor` starts when the Vault becomes visible. It installs an application-wide event filter; mouse/key/wheel activity resets a single-shot 3-minute timer. A `WindowStateChange` to minimized on the main window emits `minimized`.
- Either signal locks the vault: stop the monitor, `VaultState.lock()` (zeroes mutable key copies, clears references), drop the repository, show Login.
- `closeEvent`: lock, `force_clear()` the clipboard, close the DB, accept.

## 4. Data Model & Storage

### 4.1 Location

- Windows: `%LOCALAPPDATA%\NapishtimVault\vault.db`
- Linux/macOS: `$XDG_DATA_HOME/NapishtimVault/vault.db` (default `~/.local/share/NapishtimVault/vault.db`)
- `get_data_dir()` creates the directory if missing; `Database(db_path=...)` is injectable for tests.

### 4.2 Schema (standard `sqlite3`, plain file — no SQLCipher)

**config** — key/value blob store

| key | value |
|---|---|
| `kdf_salt` | 16-byte Scrypt salt |
| `verifier_token` | Fernet token over a fixed verifier plaintext |

**credentials**

| column | type | encrypted? |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | — |
| title | TEXT | **no** |
| username | TEXT | **no** (plaintext by design — enables search) |
| password | BLOB | **yes** — Fernet token |
| url | TEXT nullable | **no** |
| notes | TEXT nullable | **no** |
| created_at / updated_at | TEXT timestamps | **no** |

**audit_log** — `id`, `title` (plaintext), `action` (`created` / `edited` / `deleted`), `occurred_at`.

**deletion_history** — `id`, `title`, `username`, `deleted_at`. Present in the schema but **never written by current code** (deletions go to `audit_log`). Dead schema — candidate for removal or activation.

### 4.3 Repositories

- `ConfigRepository`: generic get/set/delete over `config`, plus `get/set_kdf_salt`, `get/set_verifier_token`, and `is_initialized()`.
- `CredentialRepository(db, fernet_key)`: CRUD, search, and `get_audit_events(limit=200)`. **Encryption happens at this boundary**: `_encrypt_password` on write, `_decrypt_password` on read — the UI only ever sees plaintext `Credential` objects.
- Writes use explicit `BEGIN` / `commit` / `rollback`, so a credential change and its audit row succeed or fail together.

## 5. Cryptography & Key Management

### 5.1 Key derivation (`crypto/kdf.py`)

- Scrypt (via `cryptography`): `n = 2**15`, `r = 8`, `p = 1`, 16-byte random salt (`secrets.token_bytes`), 32-byte output.
- Output is urlsafe-base64-encoded to form a Fernet key.
- Parameters are deliberately moderate to keep desktop unlock responsive.

### 5.2 Encryption (`crypto/aead.py`)

- Fernet (internally AES-128-CBC + HMAC-SHA256) over credential **passwords only**.
- `_normalize_fernet_key` accepts raw 32 bytes or an already-encoded Fernet key.
- Fernet tokens embed a timestamp and are stored as BLOBs.

### 5.3 Master password verification (`crypto/hashing.py`)

There is deliberately **no password hash**. Instead:

- At setup: `make_verifier_token(key)` encrypts the fixed plaintext `b"napishtimvault::verifier"` and stores the token in `config`.
- At login: derive a key from the entered password and try to decrypt the token; success implies the password was correct.
- A wrong password costs exactly one Scrypt run — and there is **no rate limiting or lockout** (a known gap).

### 5.4 Key lifecycle

1. **Setup** — salt generated; key derived; salt + verifier stored.
2. **Login** — same salt reused; key re-derived from the entered password.
3. **Change password** (`_on_change_master_password`):
   - verify the current password via the verifier token
   - generate a **new** salt and derive a **new** key
   - in one transaction: decrypt every stored password with the old key, re-encrypt with the new key, replace `kdf_salt` and `verifier_token` (rollback on failure)
   - swap the `VaultState` key and rebuild the repository
4. **Lock** — `VaultState.lock()` copies keys into `bytearray`, zeroes them, and clears references. Best-effort only: the original `bytes` objects and decrypted credential strings cannot be guaranteed erased from RAM.
5. **Reset** — the DB file is deleted; everything is gone.

## 6. Security Behaviors & Design Trade-offs

| Mechanism | Implementation | Honest limits |
|---|---|---|
| Encrypted passwords | Fernet at the repository boundary | Only the `password` column; every other field is plaintext in the DB file |
| No password storage | Verifier-token scheme | Salt + token live unencrypted in `config`; safe only because Scrypt is expensive |
| Auto-lock (3 min) | App-wide event filter + QTimer | In-app events only — no OS-global idle detection (activity in other apps is not seen) |
| Lock on minimize | `WindowStateChange` filter | — |
| Clipboard auto-clear (30 s) | `ClipboardManager` timer | Clears only if the clipboard still holds the app's copy; clipboard managers may have captured it already; the timer restarts on every copy |
| Memory hygiene | `VaultState.lock()`, `wipe_bytes` | Best-effort; decrypted passwords exist as Python `str` while displayed and cannot be reliably zeroed |
| Audit history | `audit_log` rows on create/edit/delete | Plaintext, latest-200 view, **not** tamper-resistant — activity history, not a security log |
| Search | SQL `LIKE` on title/username | Passwords/URLs/notes are not searchable (a consequence of the encryption choice) |

Known gaps worth tracking as future work:

- No login rate limiting / lockout
- No database-level encryption (SQLCipher)
- No import / export / backup tooling
- `deletion_history` table is dead schema
- No automated tests

## 7. UI Architecture

- `QStackedWidget` switches Setup / Login / Vault; dialogs are modal.
- Communication is **one-way upward via Qt signals**:
  - `SetupWidget.setup_complete(str)`
  - `LoginWidget.login_success(str)`, `LoginWidget.reset_requested()`
  - `VaultWidget`: `add_clicked`, `edit_clicked(int)`, `delete_clicked(int)`, `copy_username(int)`, `copy_password(int)`, `lock_clicked`, `change_master_password_clicked`, `history_clicked`, `search_changed(str)`
- Credential rows are custom `QFrame` widgets (not `QListWidget` items) laid out in a scroll area for styling flexibility; each re-emits its action with the credential id.
- Dialogs return structured results (`CredentialDialog.result_credential: Optional[Credential]`), validated in `Credential.__post_init__` (title / username / password required).
- The password generator in `CredentialDialog` uses the `secrets` module with a user-selected length and character classes.

## 8. Build & Packaging

- `pyinstaller --clean --noconsole --name NapishtimVault --onefile --paths src run.py`
- `NapishtimVault.spec` and `build/` are generated artifacts; output lands at `dist/NapishtimVault.exe`.
- Runtime dependencies (pinned in `requirements.txt`): `PyQt6==6.10.1`, `cryptography==46.0.3`; DB access uses the standard-library `sqlite3`.

## 9. Key Files to Read First

1. `src/napishtimvault/app.py` — end-to-end flow, security wiring, handlers
2. `src/napishtimvault/storage/repo.py` — persistence + encryption boundary
3. `src/napishtimvault/crypto/kdf.py`, `crypto/aead.py`, `crypto/hashing.py` — the crypto core
4. `src/napishtimvault/ui/vault.py` + `ui/dialogs.py` — user actions -> signals
