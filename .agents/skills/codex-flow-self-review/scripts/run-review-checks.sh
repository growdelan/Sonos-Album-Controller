#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_VALIDATION="$SCRIPT_DIR/../../../harness/scripts/validation-python.sh"

if [ -x "$HARNESS_VALIDATION" ]; then
  "$HARNESS_VALIDATION"
else
  echo "Uruchom tylko komendy walidacyjne, które faktycznie istnieją w tym repo."
  echo "Domyślnie dla Python/unittest: uv run python -m unittest discover -s tests -p \"test_*.py\""
fi
