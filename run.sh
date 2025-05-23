#!/usr/bin/env bash
# ------------------------------------------------------------
# Load variables from .env and call the app with --msg-file
# Usage: ./run.sh --msg-file path/to/prompt.txt
# ------------------------------------------------------------
set -euo pipefail

# 1. export every assignment found in .env (if the file exists)
ENV_FILE="$(dirname "$0")/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a               # automatically export sourced names
  # shellcheck source=/dev/null
  . "$ENV_FILE"
  set +a
fi

# 2. ensure the single required CLI argument is provided
if [[ $# -ne 2 || "$1" != "--msg-file" ]]; then
  echo "Usage: $0 --msg-file <path/to/file.txt>" >&2
  exit 1
fi

# 3. launch the Python entry-point
python3 main.py --msg-file "$2"
