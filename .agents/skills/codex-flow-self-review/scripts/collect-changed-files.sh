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
    echo "== changed files vs HEAD =="
    git diff --name-status HEAD || true
    echo
    echo "== staged files =="
    git diff --cached --name-status || true
  else
    echo "== repository has no commits yet; listing files =="
    git ls-files || true
  fi
else
  echo "To nie jest katalog wewnątrz repo git — lista plików roboczych:"
  find . -path './.git' -prune -o -type f -print | sort | sed 's#^./##'
fi
