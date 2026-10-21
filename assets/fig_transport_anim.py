#!/usr/bin/env python3
"""Animate Fig. 3.1 (fig_transport) for the defence slides.

The geometry is the thesis figure's own: this script imports fig_transport_gen.py and
sweeps the flow time s from 0 to 1 instead of drawing the three panels s = 0, 0.45, 1.
Colours and line styles follow fig_transport.tex. Two tracked points, one per mode, carry
the trajectory glyphs above the panel, which morph from a noise trajectory tau(0) to a
plausible trajectory tau(1) along the linear path.

Usage:  python3 fig_transport_anim.py FRAME_DIR
        (then encode FRAME_DIR/f_%04d.png with ffmpeg, see make_transport_anim.sh)
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

SRC = Path(__file__).resolve().parents[2] / "kth-thesis/figures/FlowMatching/src"
sys.path.insert(0, str(SRC))
import fig_transport_gen as g  # noqa: E402

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

# colours of fig_transport.tex
C1, C3, C4, C5 = "#1954a6", "#d85497", "#b0c92b", "#63666a"


def mix(hex_a, pct, hex_b="#ffffff"):
    """TikZ colour!pct: pct percent of hex_a, the rest hex_b."""
    a = np.array([int(hex_a[i:i + 2], 16) for i in (1, 3, 5)]) / 255
    b = np.array([int(hex_b[i:i + 2], 16) for i in (1, 3, 5)]) / 255
    return tuple(a * pct / 100 + b * (1 - pct / 100))


PANEL_BG = mix(C3, 4)
GRID = mix(C5, 40)
DLINE = mix(C3, 72, "#000000")
FRAME = mix(C5, 65)
TAU = mix(C4, 45, "#000000")
LBL = C5
SHADE_COLS = [mix(C3, s) for s in g.SHADES]

plt.rcParams.update({"mathtext.fontset": "cm", "font.family": "serif",
                     "font.serif": ["DejaVu Serif"], "font.size": 15})

U1, U2 = g.U1, g.U2
X, Y = np.meshgrid(np.linspace(-U1, U1, 420), np.linspace(-U2, U2, 280))
TRACK = [(g.C1 + 0.10, g.C2 + 0.26), (g.C1 + 0.10, g.C2 - 0.26)]   # upper and lower mode

# trajectory glyphs: fixed noise draw tau(0), and the two plausible arcs tau(1)
rng = np.random.default_rng(3)
GX = np.linspace(-0.36, 0.36, 40)
NOISE = [np.cumsum(rng.normal(0, 0.055, GX.size)) for _ in TRACK]
NOISE = [n - n.mean() for n in NOISE]
ARCS = [0.20 - 1.4 * GX**2, -0.20 + 1.4 * GX**2]
ARCS = [a - a.mean() for a in ARCS]
GLYPH_X = [-0.62, 0.62]
GLYPH_Y = 1.66

fig = plt.figure(figsize=(5.0, 4.94), facecolor="white")
ax = fig.add_axes([0, 0, 1, 1])


def draw(s):
    ax.clear()
    ax.set_xlim(-2.22, 2.22); ax.set_ylim(-2.0, 2.39)
    ax.set_aspect("equal"); ax.axis("off")

    clip = Rectangle((-U1, -U2), 2 * U1, 2 * U2, transform=ax.transData)
    ax.add_patch(Rectangle((-U1, -U2), 2 * U1, 2 * U2, fc=PANEL_BG, ec="none", zorder=0))

    D = g.density_image(X, Y, s)
    cf = ax.contourf(X, Y, D, levels=list(g.LEVELS) + [1e9], colors=SHADE_COLS, zorder=1)
    cf.set_clip_path(clip)
    for xs, ys in g.grid_paths(s):
        ln, = ax.plot(xs, ys, color=GRID, lw=0.6, zorder=2)
        ln.set_clip_path(clip)
    cl = ax.contour(X, Y, D, levels=g.LEVELS, colors=[DLINE], linewidths=0.8, zorder=3)
    cl.set_clip_path(clip)
    for x, y, ang, L in g.arrows(s):
        a = np.radians(ang)
        ax.annotate("", xy=(x + L * np.cos(a), y + L * np.sin(a)), xytext=(x, y),
                    arrowprops=dict(arrowstyle="-|>,head_length=0.35,head_width=0.18",
                                    color=C1, lw=0.7, shrinkA=0, shrinkB=0), zorder=4)
    ax.add_patch(Rectangle((-U1, -U2), 2 * U1, 2 * U2, fc="none", ec=FRAME, lw=1.1, zorder=5))

    # tracked points, their velocity, and their trajectory glyphs
    for i, (u1, u2) in enumerate(TRACK):
        x, y = g.psi(u1, u2, s)
        fx, fy = g.f(u1, u2)
        a = np.arctan2(fy, fx)
        if s < 1.0:
            ax.annotate("", xy=(x + 0.5 * np.cos(a), y + 0.5 * np.sin(a)), xytext=(x, y),
                        arrowprops=dict(arrowstyle="-|>,head_length=0.6,head_width=0.3",
                                        color=C1, lw=2.0, shrinkA=0, shrinkB=0), zorder=7)
        ax.plot(x, y, "o", ms=9, mfc=TAU, mec="white", mew=1.2, zorder=8)
        gx, gy = GLYPH_X[i], GLYPH_Y
        ax.add_patch(FancyBboxPatch((gx - 0.44, gy - 0.25), 0.88, 0.50,
                                    boxstyle="round,pad=0,rounding_size=0.04",
                                    fc="white", ec=mix(C5, 45), lw=1.0, zorder=6))
        curve = (1 - s) * NOISE[i] + s * ARCS[i]
        ax.plot(gx + GX, gy + curve, color=TAU, lw=1.8, zorder=7)
        ax.plot([gx, x], [gy - 0.25, y + 0.05], ls=(0, (1, 2)), color=mix(C5, 55), lw=0.9,
                zorder=5)
    lab = r"$\tau(0)$" if s == 0 else (r"$\tau(1)$, two modes" if s >= 1 else r"$\tau(s)$")
    ax.text(0, GLYPH_Y + 0.33, lab, ha="center", va="bottom", color=LBL, fontsize=15)
    if 0 < s < 1:
        ux, uy = g.psi(*TRACK[0], s)
        ax.text(ux + 0.12, uy + 0.30, r"$v_\theta$", color=C1, fontsize=17, zorder=9)

    # distribution label and flow-time axis
    plab = (r"$p_0=\mathcal{N}(0,I)$" if s == 0 else
            r"$p_1=p_{\mathrm{data}}$" if s >= 1 else r"$p_s$")
    ax.text(0, -U2 - 0.10, plab, ha="center", va="top", color=LBL, fontsize=15)
    ax.text(-U1 - 0.10, 0, r"$\mathcal{T}=\mathbb{R}^{H\times D}$", rotation=90,
            ha="right", va="center", color=LBL, fontsize=14)
    yb = -1.66
    ax.annotate("", xy=(U1, yb), xytext=(-U1, yb),
                arrowprops=dict(arrowstyle="-|>", color=mix(C5, 70), lw=1.2))
    ax.plot(-U1 + 2 * U1 * s, yb, "o", ms=8, color=C5, zorder=6)
    ax.text(-U1 - 0.06, yb, r"$s=0$", ha="right", va="center", color=LBL, fontsize=14)
    ax.text(U1 + 0.06, yb, r"$s=1$", ha="left", va="center", color=LBL, fontsize=14)
    ax.text(0, yb - 0.10, "flow time $s$", ha="center", va="top", color=LBL, fontsize=14)


if __name__ == "__main__":
    FPS, HOLD0, SWEEP, HOLD1 = 25, 20, 100, 50
    ss = [0.0] * HOLD0 + list(np.linspace(0, 1, SWEEP)) + [1.0] * HOLD1
    cache = {}
    for k, s in enumerate(ss):
        key = round(float(s), 6)
        if key not in cache:
            draw(float(s))
            p = OUT / f"f_{k:04d}.png"
            fig.savefig(p, dpi=200)
            cache[key] = p
        else:
            (OUT / f"f_{k:04d}.png").write_bytes(cache[key].read_bytes())
    print("frames", len(ss))
