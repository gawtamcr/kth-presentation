# Interactive STL explainer demos

Four self-contained HTML pages, built during defence-prep conversations to explain
STL/robustness/smoothing/compilation and STLCG++'s masking construction concretely. Each is a
single file with no external dependencies beyond a Google Fonts stylesheet — open any of them
directly in a browser. Each was also published as a Claude Artifact; those links still work for
the author but are not required to view the files.

## 1. `stl-explainer.html`
**STL, Robustness, Smoothness, Compilation**, published at
https://claude.ai/artifact/YUAYG6eYGb91YinLXjBqUo

A four-stage conceptual walkthrough, each stage a card with the thesis's own definitions:

1. STL syntax — the grammar, predicates, bounded temporal operators.
2. Robustness — the recursive definition turning satisfaction into a signed margin, and the
   soundness property.
3. Smoothness — why exact min/max break gradient-based guidance, the log-sum-exp surrogate,
   and the bias bound it introduces.
4. Compilation — the formula-to-tensor-graph pipeline as a left-to-right diagram, plus the
   per-node table of what each syntax-tree node computes.

No sliders; this one is read-only, for establishing vocabulary before the interactive demos.

## 2. `stl-robustness-calculator.html`
**Robustness Calculator**, published at https://claude.ai/artifact/H5UpbjxzooSvDqCDvZ63Fw

A single running example: the two-reach-plus-avoid requirement
`◇[0,3]A ∧ ◇[4,7]B ∧ □[0,7]¬O` scored on an 8-state 1D trajectory.

- **Trajectory panel** — a number line with region bands for A, B, and obstacle O; one slider
  per timestep (t=0…7). Moving a state updates everything downstream live.
- **Three window panels** — the reach-A window (smooth max), the reach-B window (smooth max),
  and the avoid window (smooth min), each showing the full arithmetic table (z, κ·z, e^(κ·z),
  the sum, the log, the division by κ) so every number can be reproduced by hand on a
  calculator.
- **Combine panel** — the top-level And as one more smooth min over the three clause scores,
  with a satisfied/not-satisfied verdict from the *exact* score and the bias bound from
  Proposition 4.2 (thesis numbering) for comparison.
- **Flow-time panel** — the same trajectory interpolated from a fixed noisy start toward the
  trajectory built above, as flow time s runs 0→1. Stepping through it computes the exact score
  on the evolving estimate at every step, demonstrating that the score is evaluated repeatedly
  during generation (at the predicted endpoint τ̂(s)) rather than once on the finished
  trajectory.

A shared κ (sharpness) slider controls every smoothing step in the page at once.

## 3. `stlcg-masking-visual.html`
**Recurrence vs Masking**, published at https://claude.ai/artifact/R1Ta5d4P6LGXLWZNb2Yzz8

A side-by-side, playable comparison of how a single temporal operator (Eventually, window
length K) is computed by the two libraries:

- **Left — STLCG (recurrent).** "Step back one t" fills one column of the trace at a time,
  walking backward from the last timestep, with a memory box showing the running best value —
  mirroring STLCG's RNN-style sequential computation.
- **Right — STLCG++ (masking).** "Compute all at once" reveals the whole unrolled grid's mask
  and fills every column of the trace in a single step.

A shared signal (6 sliders) and window-size K slider drive both sides identically; the step
counters make the contrast explicit — the left's step count always equals the signal length,
the right's never leaves 1.

## 4. `eventually-always-masking.html`
**Eventually, Eventually-Always**, published at https://claude.ai/artifact/6oj18xuYh6txLCPezf8c5r

Ties the masking mechanism to a concrete reach requirement with physical units: a 1D
trajectory `x(t)`, t=0…10, starting at x=0, climbing into a goal band `x≥5`.

- **Trajectory** — 11 sliders (one per timestep) plus a line plot with the goal band shaded,
  and the predicate margin `s(t) = x(t) − 5` shown as a row of signed numbers.
- **φ₁ = ◇[a,b](x≥5)** (plain Eventually) — the masking grid for every starting column, with
  column 0 highlighted as the only one ever read, since this clause is not nested inside
  anything.
- **φ₂ = ◇[a',b'] □[a,b](x≥5)** (Eventually-Always, nested) — two panels. The first computes
  the inner Always's robustness *trace at every starting time* (one-shot, masked min,
  out-of-horizon cells padded with a large value so they cannot win the min). The second feeds
  that whole trace into the outer Eventually, reporting two numbers side by side: the max over
  genuine (unpadded) columns versus the max over all columns including padded ones — making
  visible when the reported score is a boundary artifact of the padding rather than a genuine
  held window.
- **All three windows are sliders** (`a`,`b` for φ₁; `a`,`b` for the inner Always; `a`,`b` for
  the outer Eventually), with the formula line at the top updating live and every grid resizing
  (padding rows included) to match.

This is the demo that most directly motivates why the full robustness *trace* (not just one
value) is needed once operators nest, which is exactly the computational problem STLCG++'s
masking construction (demo 3) is built to solve efficiently.

## Companion document

`predicted-endpoint-and-masking.md`, in this same folder, is a prose write-up (thesis register,
written for NotebookLM to turn into an explainer video) covering the guided velocity field, the
predicted endpoint τ̂(s), why and how often the requirement score is evaluated during
generation, and the masking construction from demo 3 — the conceptual throughline that these
four interactive demos make concrete and playable.
