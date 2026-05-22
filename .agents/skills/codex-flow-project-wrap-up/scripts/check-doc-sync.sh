#!/usr/bin/env bash
set -euo pipefail

is_git_repo() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1
}

if is_git_repo; then
  echo "== git status --short =="
  git status --short || true

  echo
  if git rev-parse --verify HEAD >/dev/null 2>&1; then
    echo "== recently changed files =="
    git diff --name-status HEAD || true
  else
    echo "== recently changed files =="
    echo "repo nie ma jeszcze commita HEAD"
  fi
else
  echo "To nie jest katalog wewnątrz repo git — pomijam git status."
fi

echo
for f in README.md AGENTS.md spec.md ROADMAP.md STATUS.md; do
  if [ -f "$f" ]; then
    echo "ok: $f"
  else
    echo "missing: $f"
  fi
done
