#!/usr/bin/env bash
# Render every slide of the deck to OUT_DIR/Snn.png through PowerPoint on the Windows side.
# A copy of the deck is rendered, so the real file is never locked. PowerPoint keeps a renamed
# copy open after a failed run; use a fresh OUT_DIR if "PowerPoint could not open the file".
# Usage: bash render_deck.sh OUT_DIR [DECK]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$(mkdir -p "$1" && cd "$1" && pwd)"
DECK="${2:-$HERE/../STL-FM Defense.pptx}"
COPY="$OUT/deck_$(date +%H%M%S).pptx"
rm -f "$OUT"/S*.png
cp "$DECK" "$COPY"
cd /mnt/c && powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$(wslpath -w "$HERE/render_deck.ps1")" \
    -In "$(wslpath -w "$COPY")" -Out "$(wslpath -w "$OUT")"
ls "$OUT"/S*.png | wc -l
