#!/usr/bin/env bash
# ------------------------------------------------------------
# Load variables from .env and call the app with --msg-file using uv
# Usage: ./run-apa.sh --msg-file path/to/prompt.txt
# ------------------------------------------------------------
set -euo pipefail

# Get the script directory
SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR"

# 1. Check if uv is installed, install if not
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Source the shell to make uv available
    export PATH="$HOME/.cargo/bin:$PATH"
    if ! command -v uv &> /dev/null; then
        echo "Failed to install uv. Please install manually: https://docs.astral.sh/uv/getting-started/installation/" >&2
        exit 1
    fi
fi

# 2. Export every assignment found in .env (if the file exists)
ENV_FILE="$SCRIPT_DIR/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a               # automatically export sourced names
  # shellcheck source=/dev/null
  . "$ENV_FILE"
  set +a
fi

# 3. Ensure the single required CLI argument is provided
if [[ $# -ne 2 || "$1" != "--msg-file" ]]; then
  echo "Usage: $0 --msg-file <path/to/file.txt>" >&2
  exit 1
fi

# 4. Use uv to run the Python application (automatically manages virtual environment and dependencies)
exec uv run python main.py --msg-file "$2"
