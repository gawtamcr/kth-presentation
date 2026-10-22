#!/usr/bin/env python3
"""Crop propositions, algorithms and tables from the compiled thesis PDF for the backup slides.

Proposition and theorem boxes are found by the tcolorbox colours; algorithms and tables by their
horizontal rules, taking the group of rules nearest an anchor word.

Usage:  python3 make_backup_crops.py THESIS_PDF
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
PDF = Path(sys.argv[1])
DPI = 300

# name, page, kind, anchor word
ITEMS = [
    ("bk_prop_witness", 112, "box", "underdetermines"),
    ("bk_prop_sparse", 118, "box", None),
    ("bk_prop_nomax", 122, "box", None),
    ("bk_thm_resolves", 124, "box", None),
    ("bk_prop_smoothing", 59, "box", None),
    ("bk_alg_compile", 58, "rules", "Algorithm"),
    ("bk_alg_sampler", 66, "rules", "Guided"),
    ("bk_tab_openloop", 76, "rules", "Endpoint-inpaint"),
    ("bk_tab_anytime", 81, "rules", "Req.-only"),
    ("bk_tab_closedloop", 83, "rules", "Endpoint-inpaint"),
]


def render(page, tmp):
    out = Path(tmp) / f"p{page}"
    subprocess.run(["pdftoppm", "-png", "-r", str(DPI), "-f", str(page), "-l", str(page), "-singlefile",
                    str(PDF), str(out)], check=True)
    return np.array(Image.open(f"{out}.png").convert("RGB")).astype(int), Image.open(f"{out}.png")


def anchor_y(page, word):
    xml = subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-bbox", str(PDF), "-"],
                         capture_output=True, text=True).stdout
    for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', xml):
        if word in m.group(5):
            return float(m.group(2)) * DPI / 72
    raise KeyError((page, word))


def runs(idx):
    out, start = [], None
    for i, v in enumerate(idx):
        if start is None:
            start = prev = v
        elif v != prev + 1:
            out.append((start, prev)); start = v
        prev = v
    if start is not None:
        out.append((start, prev))
    return out


def crop_box(a, ay=None):
    """The tcolorbox, found by its body and header fill; the run containing the anchor, else the longest."""
    near = lambda c, tol: (np.abs(a - np.array(c)).max(axis=2) <= tol)
    m = near((239, 243, 255), 6) | near((198, 219, 239), 10)
    rows = np.where(m.sum(1) > a.shape[1] * 0.12)[0]
    merged = []
    for r in runs(rows):
        if merged and r[0] - merged[-1][1] <= 12:
            merged[-1] = (merged[-1][0], r[1])
        else:
            merged.append(r)
    cand = [r for r in merged if r[1] - r[0] > 60]
    if ay is not None and any(r[0] - 40 <= ay <= r[1] for r in cand):
        cand = [r for r in cand if r[0] - 40 <= ay <= r[1]]
    y0, y1 = max(cand, key=lambda r: r[1] - r[0])
    cols = np.where(m[y0:y1 + 1].sum(0) > (y1 - y0) * 0.5)[0]
    return cols.min() - 4, y0 - 4, cols.max() + 4, y1 + 4


def crop_rules(a, ay):
    """From the nearest rule above the anchor to the last rule within a float's height below it."""
    dark = (a.max(axis=2) < 160)

    def longest(row):
        best = cur = 0
        for v in row:
            cur = cur + 1 if v else 0
            best = max(best, cur)
        return best
    rows = [r for r in np.where(dark.sum(1) > 600)[0] if longest(dark[r]) > 900]
    rules = [(r0 + r1) // 2 for r0, r1 in runs(rows)]
    above = [r for r in rules if ay - 260 <= r <= ay + 40]
    below = [r for r in rules if ay + 40 < r <= ay + 1500]
    y0, y1 = int(max(above) if above else ay - 20), int(max(below))
    cols = np.where(dark[y0 - 2:y0 + 3].any(0))[0]
    return cols.min() - 10, y0 - 14, cols.max() + 10, y1 + 14


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        for name, page, kind, word in ITEMS:
            a, im = render(page, tmp)
            ay = anchor_y(page, word) if word else None
            box = crop_box(a, ay) if kind == "box" else crop_rules(a, ay)
            im.crop(tuple(int(v) for v in box)).save(HERE / f"{name}.png")
            print(name, page, box)
