#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

claude \
  --bare \
  --no-session-persistence \
  --add-dir /Users/cyan/Project/EmbodiedAI \
  --permission-mode acceptEdits \
  -p "$(cat prompt-to-paste.md)" \
  | tee stdout.md

