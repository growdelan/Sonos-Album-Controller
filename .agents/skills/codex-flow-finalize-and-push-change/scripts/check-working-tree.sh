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
  else
    echo "== changed files vs HEAD =="
    echo "repo nie ma jeszcze commita HEAD"
  fi

  echo
  echo "== git remote -v =="
  git remote -v || true
else
  echo "To nie jest katalog wewnątrz repo git — pomijam git status i remote."
fi
