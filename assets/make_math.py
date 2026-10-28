#!/usr/bin/env python3
"""Display equations for the defence slides, typeset by lualatex in the thesis fonts.

Each equation is compiled as a standalone document with the thesis notation macros
(main_thesis.tex, "notation macros") and the thesis fonts (kth/kth-fonts.tex: TeX Gyre Termes,
TeX Gyre Pagella Math), then rendered to eq_<name>.png at DPI. The builder places each image at
its natural size, so an equation set at 20 pt matches 20 pt slide text. The LaTeX follows the
thesis labels named in each entry.

Usage:  python3 make_math.py [name ...]      (all equations when no name is given)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DPI = 600

PREAMBLE = r"""
\documentclass[border=1.5pt]{standalone}
\usepackage{xcolor}
\usepackage{amsmath,amssymb}
\usepackage{fontspec}
\defaultfontfeatures{Ligatures={TeX}}
\setmainfont{TeX Gyre Termes}
\usepackage{mathtools}
\usepackage[warnings-off={mathtools-colon,mathtools-overbracket}]{unicode-math}
\setmathfont{TeX Gyre Pagella Math}
\definecolor{ink}{HTML}{262626}
\definecolor{muted}{HTML}{6E6E6E}
\definecolor{cblue}{HTML}{1954A6}
\definecolor{cgreen}{HTML}{7B8D1E}
\definecolor{cpink}{HTML}{D85497}
% fig_guided_sampler.tex palette (color1bg..color5bg), for the guided-sampler slides
\definecolor{ccyan}{HTML}{24A0D8}
\definecolor{cgrad}{HTML}{6D7D1B}
\definecolor{cgrey}{HTML}{63666A}
\newcommand{\R}{\mathbb{R}}
\newcommand{\E}{\mathbb{E}}
\newcommand{\T}{\mathcal{T}}
\newcommand{\Sat}{\mathcal{S}}
\newcommand{\Opt}{\mathcal{O}}
\newcommand{\Mfd}{\mathcal{M}}
\newcommand{\proj}{\pi}
\newcommand{\rob}{\rho}
\newcommand{\vtheta}{v_\theta}
\newcommand{\stlsat}{\models}
\newcommand{\Eventually}{\lozenge}
\newcommand{\Always}{\Box}
\newcommand{\smin}{\mathrm{smin}}
\newcommand{\smax}{\mathrm{smax}}
\newcommand{\note}[1]{\textcolor{muted}{\text{#1}}}
"""

# name: (point size, LaTeX in display math, source in the thesis)
EQS = {
    # Remark rem:fragment, Definition def:stl-syntax restricted to the evaluated fragment
    "fragment": (22, r"""
        \varphi \;::=\; \mu \;\mid\; \neg\mu \;\mid\; \varphi_1 \wedge \varphi_2
        \;\mid\; \Eventually_{[a,b]}\varphi \;\mid\; \Always_{[a,b]}\varphi,
        \qquad \mu := \big(h(x) \ge 0\big)"""),
    # eq:intro-bond, coloured as the phrases on the slide
    "bond": (30, r"""
        \varphi \;=\; \textcolor{cblue}{\Eventually_{[a,b]}}\,
        \textcolor{cgreen}{\Always_{[0,d]}\,\mathit{seated}}
        \;\wedge\; \textcolor{cpink}{\Always_{[0,T]}\,\neg\,\mathit{operator}}"""),
    # Definition def:robustness, the rows of the evaluated fragment
    "robustness": (20, r"""
        \begin{aligned}
        \rob(\mu, x, t) &= h(x(t)) &
        \qquad\qquad \rob(\Eventually_{[a,b]}\varphi, x, t) &= \max_{t'\in[t+a,t+b]}\rob(\varphi,x,t') \\
        \rob(\neg\varphi, x, t) &= -\,\rob(\varphi, x, t) &
        \rob(\Always_{[a,b]}\varphi, x, t) &= \min_{t'\in[t+a,t+b]}\rob(\varphi,x,t') \\
        \rob(\varphi_1\wedge\varphi_2, x, t) &= \min\big(\rob(\varphi_1,x,t),\,\rob(\varphi_2,x,t)\big)
        \end{aligned}"""),
    # eq:robustness-sound, for a trajectory evaluated at t = 0
    "soundness": (20, r"""
        \rob_\varphi(\tau) > 0 \;\Longrightarrow\; \tau \stlsat \varphi"""),
    # eq:logsumexp
    "smooth": (22, r"""
        \smax_\kappa(z_1,\ldots,z_n) = \tfrac{1}{\kappa}\log\sum_i e^{\kappa z_i},
        \qquad \smin_\kappa(z) = -\,\smax_\kappa(-z)"""),
    # eq:fm-loss with the linear path of Section 3.3
    "fm_loss": (20, r"""
        \begin{aligned}
        \mathcal{L}_{\mathrm{FM}}(\theta) &= \E\Big[\big\|\vtheta(\psi_s, s) - (\tau_1 - \tau_0)\big\|^2\Big] \\
        \psi_s &= (1-s)\,\tau_0 + s\,\tau_1, \qquad
        \tau_0\sim\mathcal{N}(0,I),\ \ \tau_1\sim p_{\mathrm{data}},\ \ s\sim\mathcal{U}[0,1]
        \end{aligned}"""),
    # eq:fm-ode-bg
    "fm_ode": (20, r"""
        \frac{d\tau}{ds} = \vtheta(\tau, s), \qquad \tau(0)\sim\mathcal{N}(0, I), \qquad s : 0 \to 1"""),
    # eq:guided-velocity, coloured as fig_guided_sampler.tex: cblue prior, cgrad requirement gradient
    "guided": (30, r"""
        v_{\mathrm{guided}}(\tau, s) \;=\;
        \underbrace{\textcolor{cblue}{\vtheta(\tau, s)}}_{\mathclap{\text{learned prior}}}
        \;+\; \lambda_0\,
        \underbrace{\textcolor{cgrad}{\widetilde{\nabla}_{\hat\tau}\rob_\varphi\big(\hat\tau(s)\big)}}_{\mathclap{\substack{
            \text{requirement gradient,} \\ \text{at the predicted endpoint}}}}\hspace{1.2em}"""),
    # eq:smoothness-penalty and eq:grad-normalize, with the mask of Algorithm alg:guided-ode line 7
    # coloured as fig_guided_sampler.tex: cpink requirement score, cgrey smoothness penalty, cgrad gradient pipeline
    "conditioning": (20, r"""
        \mathcal{J}(\hat\tau) = \textcolor{cpink}{\rob_\varphi(\hat\tau)}
            - \textcolor{cgrey}{\gamma\sum_t \big\|p_{t+1}-2p_t+p_{t-1}\big\|^2},
        \qquad
        \textcolor{cgrad}{\widetilde{\nabla} = \frac{\mathrm{mask}_{\mathrm{pos}}\big(\nabla_{\hat\tau}\mathcal{J}\big)}
                                  {\big\|\mathrm{mask}_{\mathrm{pos}}\big(\nabla_{\hat\tau}\mathcal{J}\big)\big\|}}"""),
    # Algorithm alg:guided-ode, lines 4 to 13, and eq:predicted-endpoint
    # coloured as fig_guided_sampler.tex: ccyan predicted endpoint, cgrad gradient pipeline, cblue prior, cgrey re-pin
    "step": (22, r"""
        \begin{aligned}
        \textcolor{ccyan}{\hat\tau} &\textcolor{ccyan}{{}= \tau + (1-s)\,\vtheta(\tau, s)} && \note{predicted endpoint} \\
        \textcolor{cgrad}{g} &\textcolor{cgrad}{{}= \widetilde{\nabla}_{\hat\tau}\,\mathcal{J}(\hat\tau)} && \note{masked, penalized, normalized gradient} \\
        \tau &\leftarrow \tau + \Delta s\,\big(\textcolor{cblue}{\vtheta(\tau, s)} + \lambda_0\, \textcolor{cgrad}{g}\big) && \note{constant-strength step} \\
        \textcolor{cgrey}{\proj_0(\tau)} &\textcolor{cgrey}{{}\leftarrow x_{\mathrm{start}}} && \note{re-pin the start state}
        \end{aligned}"""),
    # Section sec:setup-metrics
    "metrics": (22, r"""
        \begin{aligned}
        \text{logic satisfaction} &= \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}\big[\rob_\varphi(\tau_i) > 0\big]
            && \note{plan, exact semantics} \\[4pt]
        \text{task success} &= \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}\big[\text{rollout } i \text{ succeeds}\big]
            && \note{execution, the environment's criterion}
        \end{aligned}"""),
    # eq:tweedie, Section 3.3 (linear path), eq:guided-bounded
    "bounded": (22, r"""
        \begin{aligned}
        \nabla_x\log p_t(x) &= \frac{\alpha_t\,\E[x_0\mid x_t = x] - x}{\sigma_t^2}
            && \note{diffusion score, grows like $1/\sigma_t^2$ as $t \to 0$} \\[6pt]
        \tfrac{d}{ds}\psi_s &= \tau_1 - \tau_0 = \mathcal{O}(1)
            && \note{flow-matching target, uniformly in $s$} \\[6pt]
        \big\|v_{\mathrm{guided}}(\tau,s)\big\| &\le \big\|\vtheta(\tau,s)\big\| + \lambda_0 = \mathcal{O}(1)
            && \note{with $\|\widetilde{\nabla}\| = 1$}
        \end{aligned}"""),
    # Section sec:exp-cube, the sequence class
    "cube": (26, r"""
        \varphi = \Eventually_{[0,20]}\,\mathit{pick} \;\wedge\; \Eventually_{[20,100]}\,\mathit{place}"""),
    # Section sec:exp-kitchen
    "kitchen": (22, r"""
        \varphi = \Eventually_{[60,130]}\,\mathit{microwave} \;\wedge\; \Eventually_{[140,230]}\,\mathit{kettle}"""),
    # Section sec:exp-gofa
    "gofa": (20, r"""
        \varphi = \Always_{[\mathit{grasp},\,\mathit{place}]}
        \big(|\mathrm{roll}|,\ |\mathrm{pitch}|,\ |\mathrm{yaw}| < 5^\circ\big)"""),
    # the backup statements, one key formula each, without equation numbers
    # def:requirement and prop:witness-underdetermines
    "witness": (22, r"""
        \Sat_\varphi = \{\tau\in\T : \tau\stlsat\varphi\}, \qquad
        \{\tau^\star\} \subsetneq \Sat_{\varphi_1} \subsetneq \Sat_{\varphi_2} \subsetneq \cdots \subsetneq \T"""),
    # prop:sparse-gradient
    "sparse": (22, r"""
        \proj_t\big(\nabla_\tau\rob_\varphi(\tau)\big) = 0 \ \text{ for } t\notin\mathcal{A}(\tau), \qquad
        |\mathcal{A}(\tau)| \le m, \qquad \dim N(\tau) \ge (H-m)\,d"""),
    # prop:spurious-maxima and eq:optimal-set
    "spurious": (22, r"""
        \begin{gathered}
        \varphi = \Eventually_{[a,b]}\,\mu, \qquad h_\mu(x) = r - \|x_{\mathrm{pos}} - c\| \\[4pt]
        \Opt_\varphi = \operatorname*{arg\,max}_{\tau}\,\rob_\varphi(\tau)
            = \bigcup_{t\in[a,b]} \{\tau\in\T : x^{\mathrm{pos}}_t = c\}
        \end{gathered}"""),
    # prop:no-maximizer, part (i)
    "nomax": (22, r"""
        \varphi = \Always_{[0,H-1]}\,\neg\mu, \qquad
        \rob_\varphi(\tau) = \min_t\big(\|x^{\mathrm{pos}}_t - c\| - r\big), \qquad
        \sup_\tau \rob_\varphi(\tau) = +\infty"""),
    # eq:constrained-problem, thm:prior-resolves
    "constrained": (24, r"""
        \max_{\tau}\; \rob_\varphi(\tau) \quad \text{subject to} \quad \tau\in\Mfd"""),
    # prop:smoothing-bias
    "smoothing_bias": (20, r"""
        \begin{gathered}
        \max_i z_i \le \smax_\kappa(z) \le \max_i z_i + \frac{\log n}{\kappa}, \qquad
        \min_i z_i - \frac{\log n}{\kappa} \le \smin_\kappa(z) \le \min_i z_i \\[6pt]
        \rob^{(\kappa)}_\varphi(\tau) > L\,\kappa^{-1}\log n \;\Longrightarrow\; \tau\stlsat\varphi
        \end{gathered}"""),
    # Algorithm alg:guided-ode, lines 5 and 8 to 12
    "sampler": (22, r"""
        \hat\tau = \tau + (1-s)\,\vtheta(\tau, s), \qquad
        \tau \leftarrow \tau + \Delta s\,\big(\vtheta(\tau, s) + \lambda_0\, g\big)"""),
    # Table tab:nav-windows, class 1 instance
    "nav_reach": (16, r"""
        \varphi = \Eventually_{[0,63]}\,\mu_1"""),
    # Table tab:nav-windows, class 2 instance
    "nav_nested": (16, r"""
        \varphi = \Eventually_{[0,15]}\,\Always_{[0,48]}\,\mu_1"""),
    # Table tab:nav-windows, class 3 instance
    "nav_recurrence": (16, r"""
        \varphi = \Always_{[0,48]}\,\Eventually_{[0,15]}\,\mu_1"""),
    # Table tab:nav-windows, class 4 instance
    "nav_sequence": (16, r"""
        \varphi = \Eventually_{[0,15]}\mu_1 \wedge \Eventually_{[15,30]}\mu_2 \wedge \Eventually_{[30,45]}\mu_3"""),
    # Table tab:nav-windows, class 5 instance
    "nav_seqavoid": (14, r"""
        \varphi = \Eventually_{[0,15]}\mu_1 \wedge \Eventually_{[15,30]}\mu_2
        \wedge \Always_{[0,63]}\neg\mu_3 \wedge \Always_{[0,63]}\neg\mu_4"""),
    # Table tab:nav-windows, class 6 instance
    "nav_composite": (12, r"""
        \varphi = \Eventually_{[0,15]}\bigl(\mu_1 \wedge \Eventually_{[0,15]}(\Always_{[0,10]}\mu_2
        \wedge \Eventually_{[10,22]}\Always_{[0,11]}\mu_3)\bigr) \wedge \Always_{[0,63]}(\neg\mu_4 \wedge \neg\mu_5)"""),
}


def render(name, size, body, tmp):
    tex = (PREAMBLE + r"\begin{document}" + "\n"
           + rf"\fontsize{{{size}}}{{{round(size * 1.25)}}}\selectfont\color{{ink}}"
           + rf"$\displaystyle {body.strip()}$" + "\n" + r"\end{document}" + "\n")
    src = Path(tmp) / f"{name}.tex"
    src.write_text(tex, encoding="utf-8")
    run = subprocess.run(["lualatex", "-interaction=nonstopmode", "-halt-on-error", src.name],
                         cwd=tmp, capture_output=True, text=True)
    if run.returncode != 0:
        sys.exit(f"{name}: lualatex failed\n" + run.stdout[-2000:])
    out = HERE / f"eq_{name}"
    subprocess.run(["pdftoppm", "-png", "-r", str(DPI), "-singlefile", str(src.with_suffix(".pdf")), str(out)],
                   check=True)
    return out.with_suffix(".png")


if __name__ == "__main__":
    names = sys.argv[1:] or list(EQS)
    with tempfile.TemporaryDirectory() as tmp:
        for n in names:
            size, body = EQS[n]
            print("wrote", render(n, size, body, tmp).name)
