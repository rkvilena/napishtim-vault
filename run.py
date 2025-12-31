from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    # Ensure `src/` is on sys.path so `import napishtimvault` works without installation.
    repo_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(repo_root / "src"))

    from napishtimvault.app import main as app_main

    app_main()


if __name__ == "__main__":
    main()
