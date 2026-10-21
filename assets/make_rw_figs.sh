#!/usr/bin/env bash
# Crop the overview figure of one paper per related-work class, from the Zotero PDFs,
# for the related-work slide. Boxes are in 300-dpi pixels of the given page.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
Z="/mnt/c/Users/SEGARAM/Zotero/storage"
crop() {  # pdf page x y w h name
    pdftoppm -png -r 300 -f "$2" -l "$2" -singlefile -x "$3" -y "$4" -W "$5" -H "$6" "$1" "$HERE/rw_$7"
}
crop "$Z/DWH3J8J5/Meng and Fan - 2025 - TeLoGraF Temporal Logic Planning via Graph-encoded Flow Matching.pdf" \
     4 225 245 2050 545 telograf
crop "$Z/YYWWL8GQ/Liu et al. - 2025 - Zero-Shot Trajectory Planning for Signal Temporal Logic Tasks.pdf" \
     4 1296 252 816 600 zstp
crop "$Z/6TEGH9JG/Xiao et al. - 2023 - SafeDiffuser Safe Planning with Diffusion Probabilistic Models.pdf" \
     1 900 1386 1416 762 safediffuser
crop "$Z/WPEJV7N7/Zhong et al. - 2022 - Guided Conditional Diffusion for Controllable Traffic Simulation.pdf" \
     1 1365 720 915 504 ctg
crop "$Z/XVTTU88H/Kurtz and Lin - 2021 - Trajectory Optimization for High-Dimensional Nonlinear Systems Under STL Specifications.pdf" \
     1 1320 675 990 765 kurtz
echo "wrote rw_*.png"
