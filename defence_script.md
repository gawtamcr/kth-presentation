# Defence script — STL-FM (KTH revision, 2026-10-21; synced with the thesis on 2026-10-22)

One entry per slide of `STL-FM Defense.pptx`: what is on the slide, the thesis source, and a
time. The spoken text is in each slide's speaker notes, which `assets/build_deck.py` writes
(`s.notes`); edit the notes there, not in PowerPoint. Terms follow
`.claude/references/terminology.md`: requirement, learned prior, demonstrations, plausible,
logic satisfaction, task success, requirement class, STL Optimizer,
endpoint-inpaint planner. The thesis writes eventually and always as ◇ and □.

Style rules for this revision:
- KTH template.
- Short noun-phrase headings.
- One claim line on results slides only.
- Display equations typeset from the thesis LaTeX by `assets/make_math.py`.
- A section bar (Motivation → Background → Method → Results → Conclusions) on every talk slide.
- A roadmap slide opens each part, highlighting its group of the pipeline.
- Author–year sources at the bottom left of background slides.

Thesis: *STL-FM: Trajectory Planning Through STL-Guided Flow Matching. Imposing Temporal
Requirements on a Generative Motion Prior at Inference Time.*

---

## Deck order

Talk (32 slides, estimated 21.5 min):

| # | Heading | Section | s |
|---|---|---|---|
| 1 | STL-FM: Trajectory Planning Through STL-Guided Flow Matching (cover) | — | 20 |
| 2 | Adhesive bonding with an ABB YuMi | Motivation | 40 |
| 3 | Current practice | Motivation | 60 |
| 4 | From programming to generation | Motivation | 60 |
| 5 | Requirements that change after training | Motivation | 50 |
| 6 | Problem | Motivation | 50 |
| 7 | Aim and research questions | Motivation | 40 |
| 8 | Approach (full roadmap) | Motivation | 30 |
| 9 | Stating the requirement (roadmap) | Background | 10 |
| 10 | Signal Temporal Logic | Background | 40 |
| 11 | Evaluated fragment | Background | 40 |
| 12 | Quantitative robustness | Background | 50 |
| 13 | Smooth robustness | Background | 40 |
| 14 | Learning the prior (roadmap) | Background | 10 |
| 15 | Flow matching | Background | 50 |
| 16 | Generation from noise | Background | 20 |
| 17 | Related work | Background | 50 |
| 18 | Comparison of approaches (on trial) | Background | 50 |
| 19 | Guiding the prior (roadmap) | Method | 10 |
| 20 | Guided velocity field | Method | 50 |
| 21 | Guided sampler | Method | 40 |
| 22 | Evaluating the plans (roadmap) | Results | 10 |
| 23 | Experimental setup | Results | 50 |
| 24 | Six requirement classes | Results | 40 |
| 25 | Logic satisfaction in navigation | Results | 50 |
| 26 | Time to satisfaction | Results | 50 |
| 27 | Arena excursion | Results | 50 |
| 28 | Underdetermination by robustness | Results | 50 |
| 29 | Cube manipulation | Results | 50 |
| 30 | Logic satisfaction and task success | Results | 40 |
| 31 | Conclusions | Conclusions | 60 |
| 32 | Future work | Conclusions | 30 |
| 33 | (KTH logo end slide) | — | — |

The times sum to 1290 s, which is 21.5 min. Rehearsal timing has not been done.

Backup (34–52): 34 Supplementary material (divider). 35 Plausible samples that violate the
requirement. 36 Requirements witnessed by one demonstration. 37 Sparsity of the robustness
gradient. 38 Maximizers of a reach requirement. 39 Unbounded maximizers under avoidance.
40 Maximization over plausible trajectories. 41 Constant guidance strength. 42 Compilation and
smoothing bias. 43 Steps of the guided sampler. 44 Reproducing the STL Optimizer.
45 Navigation results, all four planners.
46 Disjunction and until in navigation. 47 Robustness against budget. 48 Cube results, all three
classes. 49 Kitchen study. 50 Physical platform. 51 Roughness of guided plans. 52 Limitations.

The slides are self-contained (author's request, 2026-10-21). No slide names a thesis
proposition, theorem, equation, algorithm, table, figure, section or chapter. The sources stay
in this file and in the bracketed tags at the end of each speaker note.

---

## Motivation

**1 · Cover.** Title, subtitle, author, "Master's thesis defence, carried out at ABB Robotics",
examiner Dimos V. Dimarogonas, the four supervisors.

**2 · Adhesive bonding with an ABB YuMi.** The author's YuMi photo with two lines and the
customer's quote. The photo caption gives the source. Source: ABB customer story, IRB 14050 at
GE Healthcare.

**3 · Current practice.** A six-click build of the timeline strips:
- adhesive A, replayed;
- adhesive B, seated too late, then the timing is reprogrammed;
- bead moved, placed off the bead, then the path is reprogrammed;
- the closing lines.

Source: §1.1.

**4 · From programming to generation.** Program, Imitate and Generate, one column per click.
The reason for the progression is §3.3.1: regression returns one trajectory per input, so a
requirement stated after training can select only from a distribution.

**5 · Requirements that change after training.** The thesis requirements figure without its
(a)–(c) labels. Source: §1.1, eq. 1.1.

**6 · Problem.** Figure 1.1. On click, the problem box and the line on training-time
conditioning. Source: §1.1, §1.2, Problem 4.1.

**7 · Aim and research questions.**
- Aim (§1.3): a method for imposing STL requirements on a trained generative model at
  inference time. Under it, the gloss of the learned prior (l.916).
- RQ1: does a demonstration determine the requirement?
- RQ2: does the robustness score alone determine a trajectory?
- Both questions are worded as in §1.2.
- Method: STL-FM, robustness guidance of the learned prior.

**8 · Approach.** The simplified system pipeline (thesis Fig. 5.1) in full.

## Background

**9 · Stating the requirement (roadmap).** The pipeline with the requirement row highlighted.

**10 · Signal Temporal Logic.** The requirement in words, coloured by part. On click, eq. (1.1)
typeset from the thesis; on a second click, the line on what the requirement bounds. Source:
Maler and Nickovic 2004; §1.1, §3.2.

**11 · Evaluated fragment.** The grammar of the evaluated fragment (`rem:fragment`), then a
table of each construct, its reading and the load-and-bond example. The talk does not mention
disjunction and until, which the report given to the examiner did not evaluate; backup slide 46
shows their navigation results if asked. Source: `rem:fragment`.

**12 · Quantitative robustness.** The robustness recursion for the fragment (`def:robustness`)
and soundness (`eq:robustness-sound`), above the cell figure with three executions (values
illustrative). Source: Donzé and Maler 2010.

**13 · Smooth robustness.** The log-sum-exp surrogate (`eq:logsumexp`) above the gradient
figure, exact against smoothed. Guidance uses κ = 10, and satisfaction is scored exactly.
Source: Leung et al. 2021; Kapoor et al. 2025.

**14 · Learning the prior (roadmap).** The pipeline with the prior row highlighted.

**15 · Flow matching.** The Fig. 3.1 animation plays on click. Beside it, the FM loss with the
linear path (`eq:fm-loss`, §3.3) and the generative ODE (`eq:fm-ode-bg`), with K = 64. Source:
Lipman et al. 2023; Liu et al. 2022.

**16 · Generation from noise.** A diffusion clip from the original deck, which plays on click.
The notes say it is diffusion, not flow matching.

**17 · Related work.** Five overview-figure tiles (TeLoGraF, ZSTP, Kurtz and Lin, SafeDiffuser,
CTG highlighted) and the STL-FM tile. The caption says the figures are reproduced from the
cited papers.

**18 · Comparison of approaches (on trial).** A table of seven rows:
- trajectory optimization;
- control barrier functions (Lindemann and Dimarogonas 2019);
- training-time conditioning;
- decompose-and-stitch;
- safe-set enforcement;
- CTG;
- STL-FM.

Its columns are where the requirement enters, what determines the rest of the motion, and a
property stated in Chapter 2. Every cell paraphrases Ch. 2 (§2.2 model-based, §2.3 guidance,
§2.4 decompose, §2.5 conditioning, §2.6 constraints, §2.7 position).

## Method

**19 · Guiding the prior (roadmap).** The pipeline with the guided sampler highlighted.

**20 · Guided velocity field.** `eq:guided-velocity` with braces on its terms. Below it, the
penalized objective (`eq:smoothness-penalty`) and the masked, normalized gradient
(`eq:grad-normalize`, Algorithm 2 line 7). Then two lines: one constant strength, and no
component of the sampling loop is trained.

**21 · Guided sampler.** The loop line, then Algorithm 2 lines 4–13 as four equations: the
predicted endpoint, the conditioned gradient, the constant-strength step, and the re-pin of
the start. A closing line explains why the gradient is taken at τ̂ and not at τ(s). The
bottom-left line says the full sampler is in backup (slide 43).

## Results

**22 · Evaluating the plans (roadmap).** The pipeline with plan and execution highlighted.

**23 · Experimental setup.** The arena and cube scenes, and a table of the planners against
learned prior, requirement and endpoint pin. A note says that STL-FM with endpoint pin differs
in satisfaction rate by at most 0.05 on any of the six classes. Source: §5.1.2–5.1.3, §5.2.1.

**24 · Six requirement classes.** Six STL-FM panels. Claim: one learned prior and one constant
strength λ₀ are used for all six requirement classes. Source: `tab:families`, Table 5.4.

**25 · Logic satisfaction in navigation.** A bar chart over classes 1–6. Claim: logic satisfaction
alone does not distinguish STL-FM from the STL Optimizer. Source: Table 5.4, §6.1.

**26 · Time to satisfaction.** Two stacked bar panels over classes 1–6 for STL-FM and the
STL Optimizer: first satisfaction as a percentage of the budget, and the same point in
estimated seconds. A line gives the budgets and the ranges over classes 1–6, 0.10 to 1.07 s against 0.83 to 6.75 s.
Claim: the STL Optimizer satisfies the requirement earlier in its budget but later in
wall-clock time. The notes give the plan times, including cube and kitchen, and the timing
protocol. Added 2026-10-22. Source: §5.2.3, `tab:anytime`, §5.3, §5.4, `app:anytime`.
The bars in seconds come from `CODE/flow-2d/outputs/ch5_ext_n100/ch5_numbers_ext.txt` (section G);
the thesis prints only their ranges over ten classes. The six-class ranges on the slide are computed
from the same numbers (author's choice, 2026-10-22).

**27 · Arena excursion.** The STL Optimizer beside STL-FM on sequence with
avoidance. Claim: every plan of the STL Optimizer for sequence with avoidance
leaves the arena. Source: §5.2.2, §6.1.

**28 · Underdetermination by robustness.** The sparse-gradient and unbounded-tails figure, with
the line on m of 64 to 256 waypoints. Claim: robustness alone does not determine a trajectory
(backup). Source: Props A.3.1 and A.3.4, backup slides 37–39.

**29 · Cube manipulation.** The sequence requirement in words and as a formula, with its
predicates, and the STL-FM rollout video. Claim: STL-FM completes 10 of 30 executions and the
STL Optimizer none. Source: §5.3, Table 5.6. The carry gap (12.5 cm for the STL Optimizer, 6.9 cm
for STL-FM, the mechanism behind the completion numbers above) no longer has its own talk slide;
it is in backup slide 48's table (removed 2026-10-22, author: no significant new information over
this slide and 30).

**30 · Logic satisfaction and task success.** Pooled bars and STL-FM bars per class. Claim:
each occurs without the other. Source: Table 5.6, §6.2.

## Conclusions

**31 · Conclusions.** The RQ1, RQ2 and Method callouts with their answers:
- RQ1 by Prop A.1.2.
- RQ2 by Props A.3.1 and A.3.4, with the excursion on the sequencing requirements and the carry gap.
- The method by STL-FM's satisfaction of the dwell, sequence and avoidance requirements at
  0.78–1.00 per class and 10 of 30 cube executions.

A closing line says that logic satisfaction and task success do not coincide. Source: §7.1,
§6.1–6.3.

**32 · Future work.** Four numbered items:
1. a differentiable dynamics model;
2. execution on the physical platform;
3. a sweep of a requirement's parameters;
4. a barrier-filtered controller for execution.

The kitchen plan-against-execution figure sits beside the list. Source: §7.2, §2.6.

## Backup
- 35 Plausible samples (Fig. 1.1b style).
- 36–40: the formal results in plain language, one key formula each (`make_math.py`), without
  numbers. Headings name the result. Sources:
  - 36 Prop A.1.2 with `def:requirement`;
  - 37 Prop A.3.1;
  - 38 Prop A.3.3, added 2026-10-21 because the theorem refers to it;
  - 39 Prop A.3.4;
  - 40 Thm A.3.6 with the constrained problem, and the caveat of `rem:prior-idealization` as the
    closing line.
- 41 Constant guidance strength. The former talk slide, rebuilt from the thesis expressions
  (`eq:tweedie`, the FM target, `eq:guided-bounded`); it says "well posed", as the thesis does.
- 42 Compilation and smoothing bias: Algorithm 1 and Prop 4.2.1, in plain language.
- 43 Steps of the guided sampler: Algorithm 2, in plain language.
- 44 Reproducing the STL Optimizer: how the baseline is actually computed — single-integrator
  controls, the violation penalty descended by plain gradient descent, and the robustness score
  itself computed by the same masked, differentiable construction (stljax/STLCG++) that STL-FM's
  guidance uses. Added 2026-10-22, to pre-empt a question on what the baseline actually is.
  Source: §5.1.3 (`sec:setup-baselines`, prose objective, no equation label there).
- 45 and 48: Tables 5.4, 5.5 and 5.6, still cropped (author's choice). They keep the thesis's class
  numbers and planner letters; the notes give the class names. 48's carry-gap row is the only
  place the 12.5 cm / 6.9 cm figures appear in the deck now that the talk's carry-gap slide is gone.
- 46 Disjunction and until in navigation: classes 7–10, which the report given to the examiner did
  not contain. Four STL-FM panels with their formulas, a table of satisfaction for the four planners
  and of plan time, and a closing line on the ordered-visit local optimum. The notes carry the
  ordered-visit explanation and the branch statistics. Added 2026-10-22, from the former talk slides.
  Source: §5.2.1, §5.2.3, `tab:openloop`, `tab:anytime`, `app:ordered-visit`.
- 47 Robustness against budget: the ten per-class curves of `fig:anytime` and
  `fig:anytime-ext`, in a 5 × 2 grid. Added 2026-10-22.
- 49–50: kitchen and GoFA.
- 51 Roughness of guided plans.
- 52 Limitations.

The table crops are made by `assets/make_backup_crops.py THESIS_PDF`. Rerun it after the thesis
changes. The proposition and algorithm crops it also writes are no longer used by the build.
