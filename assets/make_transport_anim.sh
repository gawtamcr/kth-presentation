#!/usr/bin/env bash
# Render fig_transport_anim.mp4 (Fig. 3.1 animated) for the defence slides.
# ffmpeg is the cached conda package, run against the cached conda libraries.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
FRAMES="${1:-$(mktemp -d)}"
PKGS="$HOME/miniforge3/pkgs"
FF="$PKGS/ffmpeg-8.0.1-h2a5dc3a_3/bin/ffmpeg"
LIBS="$(ls -d "$PKGS"/*/lib | tr '\n' ':')"

python3 "$HERE/fig_transport_anim.py" "$FRAMES"
LD_LIBRARY_PATH="$LIBS" "$FF" -hide_banner -loglevel error -y -framerate 25 \
    -i "$FRAMES/f_%04d.png" -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
    -c:v libopenh264 -b:v 6M -pix_fmt yuv420p "$HERE/fig_transport_anim.mp4"
cp "$FRAMES/f_0000.png" "$HERE/fig_transport_anim_poster.png"
echo "wrote $HERE/fig_transport_anim.mp4"
