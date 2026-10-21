#!/bin/bash
# Restart a gnomad_match worker (resume mode) until its log reports DONE. Output stays in the project folder.
K=$1
D=$HOME/Documents/HACKATON/_private/blind_gnomad
cd "$D" || exit 1
while true; do
  if grep -q "^DONE" "gnomad_match.$K.log" 2>/dev/null; then exit 0; fi
  if ! pgrep -f "gnomad_match.py $K 4" > /dev/null 2>&1; then
    echo "restart $(date +%T)" >> "gnomad_match.$K.log"
    "$HOME/.venv-hackaton-h01/bin/python" gnomad_match.py "$K" 4 >> "gnomad_match.$K.log" 2>&1
  fi
  sleep 30
done
