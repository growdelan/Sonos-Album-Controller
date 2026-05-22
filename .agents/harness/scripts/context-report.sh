#!/usr/bin/env bash
set -euo pipefail

printf '== harness context report ==\n'
printf 'date: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || true)"
printf '\n== git status --short ==\n'
git status --short 2>/dev/null || true

printf '\n== top-level files ==\n'
find . -maxdepth 2 \
  -path './.git' -prune -o \
  -path './.venv' -prune -o \
  -path './__pycache__' -prune -o \
  -type f -print | sort | sed 's#^./##'

printf '\n== python project markers ==\n'
for f in pyproject.toml uv.lock requirements.txt setup.py setup.cfg tox.ini; do
  [ -f "$f" ] && echo "$f"
done

printf '\n== tests ==\n'
if [ -d tests ]; then
  find tests -maxdepth 3 -type f | sort
else
  echo 'brak katalogu tests/'
fi

printf '\n== changed files vs HEAD ==\n'
if git rev-parse --verify HEAD >/dev/null 2>&1; then
  git diff --name-status HEAD || true
else
  echo 'repo nie ma jeszcze commita HEAD'
fi
