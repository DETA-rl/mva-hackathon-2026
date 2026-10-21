#!/usr/bin/env bash
# Prepare the publishable copy of this repository: export the committed tree (HEAD only: no history, no uncommitted
# or ignored file) to OUT_DIR, make it a NEW git repository with one commit, and scan it with tools/leak_scan.py
# (file contents, file names, the git history and its commit metadata). Exit code 1 if the scan finds anything.
#
# Usage: PUBLIC_GIT_EMAIL="<no-reply address>" tools/make_public_tree.sh OUT_DIR PATTERNS_FILE
#   OUT_DIR        new or empty folder outside this repository
#   PATTERNS_FILE  private regexes for tools/leak_scan.py (local user, machine, network and session names); keep it
#                  outside the repository
#   PUBLIC_GIT_EMAIL  e-mail written into the single commit (required; use a no-reply address, never a personal
#                  mailbox); PUBLIC_GIT_NAME defaults to "Team DETA"; PUBLIC_COMMIT_MESSAGE optional. The identity is
#                  never taken from the local git configuration.
# It never adds a remote and never pushes. Publishing is a separate, manual step.
set -euo pipefail
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
OUT=${1:?OUT_DIR}; PAT=$(readlink -f "${2:?PATTERNS_FILE}")
PUBLIC_GIT_NAME=${PUBLIC_GIT_NAME:-Team DETA}; : "${PUBLIC_GIT_EMAIL:?set PUBLIC_GIT_EMAIL (a no-reply address)}"
case "$PUBLIC_GIT_EMAIL" in *noreply*|*no-reply*) ;; *) echo "note: PUBLIC_GIT_EMAIL does not look like a no-reply address" >&2;; esac
[ -f "$PAT" ] || { echo "patterns file not found: $PAT" >&2; exit 2; }
if [ -e "$OUT" ] && [ -n "$(ls -A "$OUT")" ]; then echo "OUT_DIR exists and is not empty: $OUT" >&2; exit 2; fi
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
case "$OUT/" in "$SRC"/*) echo "OUT_DIR must be outside the repository" >&2; exit 2;; esac
case "$PAT" in "$SRC"/*) echo "PATTERNS_FILE must be outside the repository" >&2; exit 2;; esac
if [ -n "$(git -C "$SRC" status --porcelain --untracked-files=no)" ]; then
  echo "note: uncommitted changes in $SRC are not exported (HEAD only)" >&2
fi
HEAD=$(git -C "$SRC" rev-parse --short HEAD)
git -C "$SRC" archive --format=tar HEAD | tar -x -C "$OUT"

# a clean git environment: no global or system configuration (identity, hooks, templates, signing)
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME="$PUBLIC_GIT_NAME" GIT_AUTHOR_EMAIL="$PUBLIC_GIT_EMAIL"
export GIT_COMMITTER_NAME="$PUBLIC_GIT_NAME" GIT_COMMITTER_EMAIL="$PUBLIC_GIT_EMAIL"
MSG=${PUBLIC_COMMIT_MESSAGE:-"MVA Hackathon 2026 analysis code, public release

Single-commit export of the authors' working repository (commit $HEAD)."}
git -C "$OUT" init -q --template= -b main
git -C "$OUT" add -A
git -C "$OUT" -c commit.gpgsign=false commit -q -m "$MSG"
git -C "$OUT" remote | grep -q . && { echo "unexpected remote in $OUT" >&2; exit 1; }
echo "exported $(git -C "$OUT" ls-files | wc -l) files from commit $HEAD to $OUT as one commit $(git -C "$OUT" rev-parse --short HEAD)"
python3 "$SRC/tools/leak_scan.py" "$OUT" --patterns "$PAT" --allow-email "$PUBLIC_GIT_EMAIL"
