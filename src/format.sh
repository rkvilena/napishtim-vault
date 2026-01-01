#!/usr/bin/env bash
set -euo pipefail

# Formats all Python code under the repository's `src/` folder.
# Usage:
#   bash src/format.sh
#   (or from within src/) bash format.sh

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
SRC_DIR="${REPO_ROOT}/src"

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "error: expected src directory at: ${SRC_DIR}" >&2
  exit 1
fi

# Prefer the currently active venv/interpreter.
PYTHON_BIN="python"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  if command -v py >/dev/null 2>&1; then
    PYTHON_BIN="py"
  else
    echo "error: python not found on PATH (activate .venv first)" >&2
    exit 1
  fi
fi

if ! "${PYTHON_BIN}" -m ruff --version >/dev/null 2>&1; then
  echo "error: ruff is not installed in this Python environment." >&2
  echo "Install it (in .venv) with: ${PYTHON_BIN} -m pip install ruff" >&2
  exit 1
fi

echo "Formatting Python code under: ${SRC_DIR}"
"${PYTHON_BIN}" -m ruff format "${SRC_DIR}"

# Optional: apply safe auto-fixes (import sorting, small refactors, etc.)
# Remove this block if you only want formatting.
echo "Applying Ruff auto-fixes under: ${SRC_DIR}"
"${PYTHON_BIN}" -m ruff check --fix "${SRC_DIR}"

echo "Done."
