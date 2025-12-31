# NapishtimVault

A secure, minimalist password manager built with Python and PyQt6.

## Features

- 🔐 Master password authentication with Argon2 hashing
- 🔒 AES-256-GCM encryption for all stored credentials
- 💾 Encrypted-at-rest SQLite storage (SQLCipher)
- ⏱️ Auto-lock after 5 minutes of inactivity or when minimized
- 📋 Clipboard auto-clear after 30 seconds
- 🎨 Dark, minimalist UI

## Setup

### Prerequisites
- Python 3.10 or higher

### Installation

1. Create and activate virtual environment:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
python -m pip install -U pip
python -m pip install -r requirements.txt
```

### Running the Application

```powershell
python -m napishtimvault.app
```

Or directly:
```powershell
python src/napishtimvault/app.py
```

## Building Executable

```powershell
python -m pip install pyinstaller
pyinstaller --noconsole --name NapishtimVault --onefile src/napishtimvault/app.py
```

The executable will be created in the `dist/` folder.

## Security

- Master password is never stored - only its Argon2 hash
- All credentials are encrypted with AES-256-GCM
- Encryption key is derived from master password using Argon2
- Database is encrypted at rest using SQLCipher
- Secrets are kept in memory for minimum time
- Auto-lock wipes in-memory keys

## License

MIT License
