#!/usr/bin/env bash
set -euo pipefail

printf '== python validation ==\n'

if [ -d tests ]; then
  if command -v uv >/dev/null 2>&1; then
    echo '+ uv run python -m unittest discover -s tests -p "test_*.py"'
    uv run python -m unittest discover -s tests -p "test_*.py"
  else
    echo '+ python -m unittest discover -s tests -p "test_*.py"'
    python -m unittest discover -s tests -p "test_*.py"
  fi
else
  echo 'brak katalogu tests/ — pomijam domyślne unittest discover'
fi

if [ -f pyproject.toml ] && grep -q "ruff" pyproject.toml 2>/dev/null; then
  if command -v uv >/dev/null 2>&1; then
    echo '+ uv run ruff check .'
    uv run ruff check .
  else
    echo 'ruff wykryty w pyproject.toml, ale uv nie jest dostępny'
  fi
fi

if [ -f pyproject.toml ] && grep -q "mypy" pyproject.toml 2>/dev/null; then
  if command -v uv >/dev/null 2>&1; then
    echo '+ uv run mypy .'
    uv run mypy .
  else
    echo 'mypy wykryty w pyproject.toml, ale uv nie jest dostępny'
  fi
fi
