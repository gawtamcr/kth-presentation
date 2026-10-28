#!/usr/bin/env python3
"""Static figures for the defence slides, in the style of the thesis motivation figures.

fig_robustness_cell.png      slide 10: three executions in the load-and-bond cell, top view,
                             and the robustness of each (illustrative values, cm)
fig_robustness_gradient.png  slide 11: the gradient of the robustness score on one plan,
                             under the exact semantics and under the smooth surrogate

Requirement (thesis eq. 1.1):  phi = <>_[a,b] []_[0,d] seated  AND  []_[0,T] not operator
Robustness is a margin in the units of the predicates, here centimetres.
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Circle

HERE = Path(__file__).resolve().parent
TEX = "/usr/share/texmf/fonts/opentype/public/tex-gyre"
for f in ("texgyretermes-regular.otf", "texgyretermes-italic.otf", "texgyretermes-bold.otf"):
    font_manager.fontManager.addfont(f"{TEX}/{f}")
plt.rcParams.update({"font.family": "TeX Gyre Termes", "mathtext.fontset": "custom",
                     "mathtext.rm": "TeX Gyre Termes", "mathtext.it": "TeX Gyre Termes:italic",
                     "font.size": 17})

BLUE, CYAN, PINK, GREEN, GREY = "#1954a6", "#24a0d8", "#d85497", "#7f9a1c", "#63666a"
ORANGE = "#e07b00"

# ── cell and requirement (illustrative) ──
T, DT = 10.0, 0.05
t = np.arange(0.0, T + 1e-9, DT)
A, B, D = 4.0, 6.0, 2.0
SEAT, R = np.array([75.0, 32.0]), 3.0
Y_OP = 12.0
PICK = np.array([15.0, 45.0])


def path(tk, pk):
    tk, pk = np.asarray(tk, float), np.asarray(pk, float)
    out = np.empty((len(t), 2))
    for i, ti in enumerate(t):
        j = int(np.clip(np.searchsorted(tk, ti, side="right") - 1, 0, len(tk) - 2))
        u = np.clip((ti - tk[j]) / (tk[j + 1] - tk[j]), 0.0, 1.0)
        s = (1 - np.cos(np.pi * u)) / 2
        out[i] = pk[j] * (1 - s) + pk[j + 1] * s
    return out


RUNS = [
    ("seated on time", path([0, 1, 2.5, 4.3, 5.2, 7.6, 9, 10],
                            [PICK, PICK, (45, 40), (76.5, 32.5), (75.4, 32.2), SEAT, (75, 50), (75, 50)])),
    ("seated late", path([0, 1, 3, 5.5, 6.8, 7.4, 9.6, 10],
                         [PICK, PICK, (35, 42), (58, 37), (76.5, 32.5), (75.4, 32.2), SEAT, (75, 40)])),
    ("enters the operator zone", path([0, 1, 2.2, 4.3, 5.2, 7.6, 9, 10],
                                      [PICK, PICK, (40, 6), (76.5, 32.5), (75.4, 32.2), SEAT, (75, 50),
                                       (75, 50)])),
]
NB = int(round(B / DT))


def margins(p):
    return R - np.linalg.norm(p - SEAT, axis=1), p[:, 1] - Y_OP


def rho(p, smin=np.min, smax=np.max):
    s, c = margins(p)
    nd = int(round(D / DT))
    win = range(int(round(A / DT)), NB + 1)
    f = smax(np.array([smin(s[i:i + nd + 1]) for i in win]))
    return smin(np.array([f, smin(c)])), f, c.min()


def soft(k):
    smin = lambda z: -np.log(np.sum(np.exp(-k * (z - z.min())))) / k + z.min()
    smax = lambda z: np.log(np.sum(np.exp(k * (z - z.max())))) / k + z.max()
    return smin, smax


def cell(ax, title, zone_label_right=False):
    ax.set_xlim(-2, 102); ax.set_ylim(-3, 63); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 100, 60, fc="#efefef", ec="#c8c8c8", lw=1.2))
    ax.add_patch(Rectangle((0, 0), 100, Y_OP, fc="white", ec=PINK, lw=0.8, hatch="////", alpha=0.55))
    ax.text(97 if zone_label_right else 3, Y_OP / 2, "operator zone", color=PINK, va="center",
            ha="right" if zone_label_right else "left", fontsize=15,
            bbox=dict(fc="white", ec="none", pad=1.5))
    ax.add_patch(Rectangle(PICK - (5, 4), 10, 8, fc="#d9d9d9", ec="#9a9a9a"))
    ax.add_patch(Rectangle(SEAT - (10, 7), 20, 14, fc="#d9d9d9", ec="#9a9a9a"))
    ax.add_patch(Circle(SEAT, R, fc="#dbe6f4", ec=BLUE, ls="--", lw=1.2))
    ax.text(SEAT[0], SEAT[1] - 11.5, "housing", ha="center", color=GREY, fontsize=15)
    ax.text(PICK[0], PICK[1] + 6, "part", ha="center", color=GREY, fontsize=15)
    ax.set_title(title, fontsize=18, color="#262626", pad=6)


def fig_cell():
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.2))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.90, bottom=0.12, wspace=0.06)
    for k, (ax, (name, p)) in enumerate(zip(axes, RUNS)):
        cell(ax, f"({'abc'[k]}) {name}", zone_label_right=(k == 2))
        ax.plot(p[:, 0], p[:, 1], color=GREY, lw=1.8)
        ax.plot(p[::10, 0], p[::10, 1], "o", ms=3.2, color=GREY)
        r, f, cmin = rho(p)
        if k == 1:
            pb = p[NB]
            ax.plot(*pb, "o", ms=8, color=PINK, zorder=5)
            ax.annotate("", xy=SEAT, xytext=pb, arrowprops=dict(arrowstyle="<->", color=PINK, lw=1.4,
                                                                shrinkA=4, shrinkB=0))
            ax.text(pb[0] - 1, pb[1] + 4, r"at $t=b$", color=PINK, ha="center", fontsize=15)
        if k == 2:
            i = int(np.argmin(p[:, 1]))
            ax.plot(*p[i], "o", ms=8, color=PINK, zorder=5)
            ax.annotate("", xy=(p[i, 0] - 8, Y_OP), xytext=(p[i, 0] - 8, p[i, 1]),
                        arrowprops=dict(arrowstyle="<->", color=PINK, lw=1.4, shrinkA=0, shrinkB=0))
        ok = r > 0
        ax.text(50, -10, rf"$\rho = {r:+.1f}$ cm".replace("-", "−"), ha="center", va="top",
                fontsize=20, color=GREEN if ok else PINK)
    fig.savefig(HERE / "fig_robustness_cell.png", dpi=300)
    plt.close(fig)


def fig_gradient():
    name, p = RUNS[1]
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.3))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.04, wspace=0.05)
    titles = ["exact min and max: one waypoint", "smooth surrogate: a few waypoints"]
    for k, ax in enumerate(axes):
        cell(ax, titles[k])
        idx = np.arange(0, len(t), 5)
        ax.plot(p[:, 0], p[:, 1], color=GREY, lw=1.8)
        ax.plot(p[idx, 0], p[idx, 1], "o", ms=4, color=GREY)
        if k == 0:
            g = np.zeros_like(p)
            g[NB] = (SEAT - p[NB]) / np.linalg.norm(SEAT - p[NB])
        else:
            smin, smax = soft(0.3)
            g = np.zeros_like(p)
            base = rho(p, smin, smax)[0]
            for i in idx:
                for j in range(2):
                    q = p.copy(); q[i, j] += 1e-3
                    g[i, j] = (rho(q, smin, smax)[0] - base) / 1e-3
            g /= np.abs(g).max()
        if k == 0:
            ax.plot(*p[NB], "o", ms=9, color=CYAN, zorder=7)
            ax.text(p[NB, 0] - 2, p[NB, 1] + 4.5, r"$t=b$", color=CYAN, ha="center", fontsize=15)
        for i in idx:
            n = np.linalg.norm(g[i])
            if n > 0.04:
                ax.annotate("", xy=p[i] + 12 * g[i], xytext=p[i],
                            arrowprops=dict(arrowstyle="-|>,head_length=0.5,head_width=0.25",
                                            color=CYAN, lw=2.0, shrinkA=0, shrinkB=0), zorder=6)
    fig.savefig(HERE / "fig_robustness_gradient.png", dpi=300)
    plt.close(fig)


def fig_robustness_1d():
    """1D margin signal c(t) = x_y(t) - Y_op for the operator-zone requirement []_[0,T] not operator,
    one run that dips into the zone. Left: exact min, one witness instant t*, zero gradient elsewhere.
    Right: smooth surrogate at kappa = 10, gradient spread over the neighbouring samples."""
    name, p = RUNS[2]
    c = p[:, 1] - Y_OP
    idx = np.arange(0, len(t), 4)
    istar = int(np.argmin(c))
    smin, _ = soft(10.0)

    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.0))
    fig.subplots_adjust(left=0.065, right=0.99, top=0.85, bottom=0.17, wspace=0.14)
    titles = [r"exact: $\rho=\min_t c(t)$, one witness", r"smooth surrogate: gradient spreads over $t$"]
    for k, ax in enumerate(axes):
        ax.set_title(titles[k], fontsize=18, color="#262626", pad=8)
        ax.axhline(0.0, color=PINK, lw=1.0, ls="--", zorder=1)
        ax.text(t[-1], 0.6, "operator zone", color=PINK, ha="right", va="bottom", fontsize=14)
        ax.plot(t, c, color=GREY, lw=2.0, zorder=3)
        ax.set_xlim(t[0], t[-1])
        ax.set_ylim(-16, 24)
        ax.set_xlabel(r"$t$", fontsize=16)
        if k == 0:
            ax.set_ylabel(r"$c(t) = x_y(t) - Y_{\mathrm{op}}$", fontsize=16)
        ax.set_xticks([]); ax.set_yticks([0])
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        if k == 0:
            ax.plot(t[istar], c[istar], "o", ms=9, color=CYAN, zorder=5)
            ax.annotate("", xy=(t[istar], 0), xytext=(t[istar], c[istar]),
                        arrowprops=dict(arrowstyle="-", color=CYAN, lw=1.4, ls=":"))
            ax.text(t[istar], c[istar] - 3.0, r"$t^\ast=\arg\min_t c(t)$", color=CYAN,
                    ha="center", va="top", fontsize=14)
            ax.text(t[istar] + 0.3, c[istar] + 2.2, rf"$\rho = {c[istar]:+.1f}$", color=CYAN,
                    ha="left", fontsize=15)
        else:
            base = smin(c)
            win = range(max(istar - 10, 0), min(istar + 11, len(c)))
            g = np.zeros_like(c)
            for i in win:
                cq = c.copy(); cq[i] += 1e-3
                g[i] = (smin(cq) - base) / 1e-3
            g /= g.max() if g.max() > 0 else 1.0
            ax.plot(t[istar], c[istar], "o", ms=9, color=CYAN, zorder=5)
            for i in win:
                if g[i] > 0.02:
                    ax.plot([t[i], t[i]], [c[i], c[i] + 14 * g[i]], color=CYAN, lw=2.5,
                            solid_capstyle="round", zorder=4, alpha=0.5 + 0.5 * g[i])
            ax.text(t[istar] + 0.3, c[istar] + 2.2, rf"$\mathrm{{smin}}_\kappa = {base:+.1f}$", color=CYAN,
                    ha="left", fontsize=15)
    fig.savefig(HERE / "fig_robustness_1d.png", dpi=300)
    plt.close(fig)


def nav_frame(ax, xlim=(-5.3, 5.3), ylim=(-5.3, 6.3)):
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.add_patch(Rectangle((-5, -5), 10, 11, fc="white", ec="#9a9a9a", lw=1.2, zorder=0))


def nav_scene(ax):
    ax.add_patch(Circle((-4.1, -0.6), 0.5, fc="none", ec="#f28e2b", ls="--", lw=1.5, zorder=2))
    ax.plot(-4.1, -0.6, "*", ms=13, color="#f28e2b", zorder=3)
    ax.add_patch(Circle((3.0, 0.9), 0.5, fc="none", ec="#e15759", ls="--", lw=1.5, zorder=2))
    ax.plot(3.0, 0.9, "*", ms=13, color="#e15759", zorder=3)
    for c in [(0.4, -1.5), (1.0, 3.4)]:
        ax.add_patch(Circle(c, 0.5, fc="#9a9a9a", ec="#7a7a7a", zorder=2))
    ax.plot(-4.0, -2.6, "o", ms=9, color="#2ca02c", zorder=4)


def smooth_path(keys, n=64):
    tk = np.array([k[0] for k in keys], float); pk = np.array([k[1] for k in keys], float)
    ts = np.arange(n)
    out = np.empty((n, 2))
    for i, ti in enumerate(ts):
        j = int(np.clip(np.searchsorted(tk, ti, side="right") - 1, 0, len(tk) - 2))
        u = np.clip((ti - tk[j]) / (tk[j + 1] - tk[j]), 0, 1)
        sm = (1 - np.cos(np.pi * u)) / 2
        out[i] = pk[j] * (1 - sm) + pk[j + 1] * sm
    return out


def fig_sparse():
    """Prop. sparse-gradient and Prop. no-maximizer, on a sequence-with-avoidance plan."""
    P = smooth_path([(0, (-4.0, -2.6)), (14, (-4.1, -0.7)), (30, (2.9, 0.9)), (63, (3.6, 4.6))])
    Q = smooth_path([(0, (-4.0, -2.6)), (14, (-3.2, -0.2)), (30, (2.0, 1.6)), (63, (3.6, 4.6))])
    active = [14, 30]
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.6))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.88, bottom=0.03, wspace=0.04)

    ax = axes[0]
    nav_frame(ax); nav_scene(ax)
    ax.set_title("the score depends on a few waypoints", fontsize=18, pad=6)
    ax.plot(Q[:, 0], Q[:, 1], color=GREY, lw=1.6, zorder=3)
    ax.plot(Q[:, 0], Q[:, 1], "o", ms=3.5, color="#b5b5b5", zorder=4)
    for i, tgt in zip(active, [(-4.1, -0.6), (3.0, 0.9)]):
        ax.plot(*Q[i], "o", ms=9, color=CYAN, zorder=6)
        d = np.array(tgt) - Q[i]
        ax.annotate("", xy=Q[i] + 0.9 * d, xytext=Q[i],
                    arrowprops=dict(arrowstyle="-|>", color=CYAN, lw=2.2, shrinkA=0, shrinkB=0), zorder=7)
    ax.text(-1.0, -4.3, "gradient zero at every grey waypoint", ha="center", fontsize=15, color=GREY)

    ax = axes[1]
    nav_frame(ax, xlim=(-5.3, 10.5), ylim=(-5.3, 9.6))
    nav_scene(ax)
    ax.set_title("where only avoidance applies, the maximizers are unbounded", fontsize=18, pad=6)
    ax.plot(P[:31, 0], P[:31, 1], color=GREY, lw=1.6, zorder=3)
    ax.plot(P[:31, 0], P[:31, 1], "o", ms=3.5, color="#b5b5b5", zorder=4)
    for k, end in enumerate([(3.6, 4.6), (6.5, 7.0), (9.5, 8.6), (9.8, 2.2), (7.5, -3.8)]):
        T = smooth_path([(30, P[30]), (63, end)], n=64)[30:]
        ax.plot(T[:, 0], T[:, 1], color=GREY if k == 0 else PINK, lw=1.6, ls="-" if k == 0 else "--",
                zorder=3)
    ax.text(7.6, -4.6, r"same $\rho$ for every tail", ha="center", fontsize=15, color=PINK)
    ax.text(-4.8, 6.35, "arena", fontsize=14, color=GREY, va="bottom")
    fig.savefig(HERE / "fig_sparse_unbounded.png", dpi=300)
    plt.close(fig)


def fig_modes():
    """Why the model must be generative: demonstrations pass a fixture on either side, a model with one
    output averages them through the fixture, a generative model samples either side."""
    x = np.linspace(0, 10, 120)
    bump = np.sin(np.pi * x / 10)
    rng = np.random.default_rng(4)
    hs = np.concatenate([rng.uniform(1.9, 2.7, 4), -rng.uniform(1.9, 2.7, 4)])
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 3.9))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.86, bottom=0.03, wspace=0.06)
    titles = ["Demonstrations", "A model with one output", "A generative model"]
    for k, ax in enumerate(axes):
        ax.set_xlim(-0.8, 10.8); ax.set_ylim(-3.6, 3.6); ax.set_aspect("equal"); ax.axis("off")
        ax.add_patch(Rectangle((-0.8, -3.6), 11.6, 7.2, fc="#f6f6f6", ec="#c8c8c8", lw=1.0))
        ax.add_patch(Circle((5, 0), 1.25, fc="#9a9a9a", ec="#7a7a7a", zorder=3))
        ax.text(5, 0, "fixture", ha="center", va="center", fontsize=13, color="white", zorder=4)
        ax.plot(0, 0, "o", ms=10, color="#2ca02c", zorder=5)
        ax.plot(10, 0, "*", ms=16, color="#e15759", zorder=5)
        ax.set_title(titles[k], fontsize=18, pad=6)
        if k == 0:
            for h in hs:
                ax.plot(x, h * bump, color=GREY, lw=1.6, alpha=0.85)
        elif k == 1:
            for h in hs:
                ax.plot(x, h * bump, color="#d0d0d0", lw=1.2)
            ax.plot(x, np.mean(hs) * bump, color=PINK, lw=3.0, zorder=6)
            ax.text(5, -2.95, "the average passes through the fixture", ha="center", fontsize=14, color=PINK)
        else:
            for h in rng.uniform(1.9, 2.7, 6) * np.array([1, -1, 1, -1, 1, -1]):
                ax.plot(x, h * bump, color=BLUE, lw=1.8)
            ax.text(5, -2.95, "each sample passes on one side", ha="center", fontsize=14, color=BLUE)
    fig.savefig(HERE / "fig_modes.png", dpi=300)
    plt.close(fig)


def fig_progression():
    """Slide 4, three panels: a programmed motion, an imitated motion (one per state), generated motions
    among which a requirement stated later selects."""
    x = np.linspace(0, 10, 120)
    bump = np.sin(np.pi * x / 10)
    rng = np.random.default_rng(7)
    demos = [h * bump + w * np.sin(2 * np.pi * x / 10) for h, w in
             zip(rng.uniform(-2.4, 2.6, 9), rng.uniform(-0.5, 0.5, 9))]
    ZX0, ZX1, ZY = 3.4, 6.6, -1.0          # zone stated later: x-range, upper edge (bottom band)

    def scene(ax):
        ax.set_xlim(-0.8, 10.8); ax.set_ylim(-3.6, 3.6); ax.set_aspect("equal"); ax.axis("off")
        ax.add_patch(Rectangle((-0.8, -3.6), 11.6, 7.2, fc="#f6f6f6", ec="#c8c8c8", lw=1.0))
        ax.plot(0, 0, "o", ms=10, color="#2ca02c", zorder=6)
        ax.plot(10, 0, "*", ms=16, color="#e15759", zorder=6)

    def save(fig, name):
        fig.savefig(HERE / name, dpi=300); plt.close(fig)

    # 1 programmed: one hand-coded polyline
    fig, ax = plt.subplots(figsize=(4.0, 2.8)); fig.subplots_adjust(0, 0, 1, 1); scene(ax)
    ax.plot([0, 2.5, 7.5, 10], [0, 1.6, 1.6, 0], color=GREY, lw=3.0, solid_joinstyle="miter")
    for px, py in [(2.5, 1.6), (7.5, 1.6)]:
        ax.plot(px, py, "s", ms=7, color=GREY)
    save(fig, "fig_prog_1.png")

    # 2 imitated: demonstrations faded, one predicted motion
    fig, ax = plt.subplots(figsize=(4.0, 2.8)); fig.subplots_adjust(0, 0, 1, 1); scene(ax)
    for d in demos:
        ax.plot(x, d, color="#c9c9c9", lw=1.3)
    ax.plot(x, np.mean(demos, axis=0), color=BLUE, lw=3.0)
    save(fig, "fig_prog_2.png")

    # 3 generated: samples, and a zone stated later that selects among them
    fig, ax = plt.subplots(figsize=(4.0, 2.8)); fig.subplots_adjust(0, 0, 1, 1); scene(ax)
    ax.add_patch(Rectangle((ZX0, -3.6), ZX1 - ZX0, ZY + 3.6, fc="white", ec=PINK, lw=0.9, hatch="////",
                           alpha=0.6, zorder=1))
    for h, w in zip([2.4, 1.7, 1.0, 0.45, -0.35, -1.3, -1.9, -2.5], [0.3, -0.3, 0.25, -0.2, 0.2, -0.25, 0.3, -0.2]):
        y = h * bump + w * np.sin(2 * np.pi * x / 10)
        inside = ((x > ZX0) & (x < ZX1) & (y < ZY)).any()
        ax.plot(x, y, color="#e3b5cc" if inside else BLUE, lw=1.4 if inside else 2.2,
                ls="--" if inside else "-", zorder=3)
    save(fig, "fig_prog_3.png")


# ── result charts, values from Table tab:openloop (ten classes, 2026-10-22) and Table tab:closedloop ──
PLANNER_COL = {"Endpoint-inpaint": "#9a9a9a", "STL-FM": BLUE, "STL Optimizer": PINK}


def fig_nav_satisfaction():
    classes = ["Reach", "Nested\nreach-and-\ndwell", "Recurrence", "Sequence", "Sequence\nwith\navoidance",
               "Composite", "Choice of\ntarget", "Choice of\nsequence", "Ordered\nvisit", "Avoidance\nuntil reach"]
    vals = {"Endpoint-inpaint": [1.00, 0, 0, 0, 0, 0, 0.18, 0.02, 0.05, 0.03],
            "STL-FM": [0.96, 1.00, 0.98, 0.89, 0.89, 0.78, 0.98, 0.96, 0.27, 0.97],
            "STL Optimizer": [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 0.98, 1.00, 0.00, 1.00]}
    leaves = (3, 4, 7, 8, 9)   # every plan of the STL Optimizer leaves the arena (star in tab:openloop)
    # The talk shows classes 1-6 only; 7-10 (disjunction and until) were not in the report the examiner received.
    classes = classes[:6]; vals = {k: v[:6] for k, v in vals.items()}; leaves = tuple(i for i in leaves if i < 6)
    fig, ax = plt.subplots(figsize=(12.4, 4.4))
    fig.subplots_adjust(left=0.07, right=0.995, top=0.88, bottom=0.25)
    x = np.arange(len(classes)); w = 0.27
    for k, (name, v) in enumerate(vals.items()):
        bars = ax.bar(x + (k - 1) * w, v, w * 0.92, color=PLANNER_COL[name], label=name)
        for i, (b, val) in enumerate(zip(bars, v)):
            txt = f"{val:.2f}"
            if name == "STL Optimizer" and i in leaves:
                txt += "†"
            ax.text(b.get_x() + b.get_width() / 2, val + 0.02, txt, ha="center", va="bottom", fontsize=12,
                    color=PLANNER_COL[name])
    ax.set_xticks(x); ax.set_xticklabels(classes, fontsize=14)
    ax.set_ylim(0, 1.12); ax.set_yticks([0, 0.5, 1.0])
    ax.set_ylabel("logic satisfaction", fontsize=16)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(ncol=3, frameon=False, fontsize=15, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    ax.text(1.0, 1.06, "† every plan leaves the arena", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=14, color=PINK)
    fig.savefig(HERE / "fig_nav_satisfaction.png", dpi=300)
    plt.close(fig)


def fig_time_budget():
    """First satisfaction against wall-clock time, per navigation class.

    Seconds: the per-class medians behind the ranges of Section sec:results-anytime
    (CODE/flow-2d/outputs/ch5_ext_n100/ch5_numbers_ext.txt, section G), whose extremes are the
    thesis's 0.10-2.56 s and 0.83-7.29 s. Ordered visit is left out, as in the thesis, and the
    optimizer has no satisfying run on it.
    """
    classes = ["Reach", "Nested\nreach-and-\ndwell", "Recurrence", "Sequence", "Sequence\nwith\navoidance",
               "Composite", "Choice of\ntarget", "Choice of\nsequence", "Ordered\nvisit", "Avoidance\nuntil reach"]
    sec = {"STL-FM": [0.098, 0.534, 0.534, 0.652, 0.677, 1.072, 0.214, 0.624, None, 2.559],
           "STL Optimizer": [0.830, 1.001, 1.053, 3.162, 5.789, 6.747, 6.084, 7.027, None, 7.289]}
    # The talk shows classes 1-6 only; 7-10 are in a backup slide.
    classes = classes[:6]; sec = {k: v[:6] for k, v in sec.items()}
    fig, ax = plt.subplots(1, 1, figsize=(12.4, 2.6))
    fig.subplots_adjust(left=0.075, right=0.995, top=0.80, bottom=0.26)
    x = np.arange(len(classes)); w = 0.36
    for k, (name, v) in enumerate(sec.items()):
        xs = [xi + (k - 0.5) * w for xi, val in zip(x, v) if val is not None]
        ax.bar(xs, [val for val in v if val is not None], w * 0.92, color=PLANNER_COL[name], label=name)
    ax.set_ylim(0, 8 * 1.08)
    ax.set_ylabel("seconds, estimated", fontsize=14)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e3e3e3", lw=0.8); ax.set_axisbelow(True)
    ax.set_xticks(x); ax.set_xticklabels(classes, fontsize=14)
    ax.legend(ncol=2, frameon=False, fontsize=14, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    fig.savefig(HERE / "fig_time_budget.png", dpi=300)
    plt.close(fig)


def fig_cube_logic_task():
    LOGIC, TASK = CYAN, "#7f9a1c"
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.4), gridspec_kw={"width_ratios": [1, 1]})
    fig.subplots_adjust(left=0.07, right=0.99, top=0.84, bottom=0.14, wspace=0.18)
    panels = [("Pooled, 30 runs per planner", ["Endpoint-inpaint", "STL-FM", "STL Optimizer"],
               [(1, 1), (20, 10), (30, 0)], 30),
              ("STL-FM, 10 runs per class", ["Nested reach-\nand-dwell", "Sequence", "Sequence with\navoidance"],
               [(1, 9), (10, 1), (9, 0)], 10)]
    for ax, (title, names, counts, n) in zip(axes, panels):
        x = np.arange(len(names)); w = 0.36
        for k, (col, lab) in enumerate([(LOGIC, "logic satisfaction"), (TASK, "task success")]):
            v = [c[k] / n for c in counts]
            bars = ax.bar(x + (k - 0.5) * w, v, w * 0.92, color=col, label=lab)
            for b, c in zip(bars, counts):
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.02, f"{c[k]}/{n}", ha="center",
                        va="bottom", fontsize=13, color=col)
        ax.set_xticks(x); ax.set_xticklabels(names, fontsize=15)
        ax.set_ylim(0, 1.12); ax.set_yticks([0, 0.5, 1.0])
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_title(title, fontsize=17, pad=8)
    axes[0].set_ylabel("rate", fontsize=16)
    axes[0].legend(frameon=False, fontsize=15, loc="upper left", bbox_to_anchor=(0.0, 1.0))
    fig.savefig(HERE / "fig_cube_logic_task.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    for name, p in RUNS:
        r, f, c = rho(p)
        print(f"{name}: rho {r:+.2f} (seat part {f:+.2f}, clearance {c:+.2f})")
    fig_cell()
    fig_gradient()
    fig_robustness_1d()
    fig_sparse()
    fig_nav_satisfaction()
    fig_cube_logic_task()
    fig_time_budget()
    fig_modes()
    fig_progression()
    print("wrote fig_robustness_cell, fig_robustness_gradient, fig_robustness_1d, fig_sparse_unbounded, "
          "fig_nav_satisfaction, fig_cube_logic_task, fig_modes, fig_prog_1-3")
