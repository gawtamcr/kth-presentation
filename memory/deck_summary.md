# Deck summary, slide by slide (STL-FM Defense.pptx, 49 slides, KTH revision 2026-10-21, self-contained the same day, synced with the thesis 2026-10-22, trimmed 2026-10-22, slides 25-26 merged 2026-10-23, slides 10-13 merged to 10-11, 2026-10-23)

Deck numbering. Headings are short noun phrases. "Claim" is the one-sentence line under the
evidence on a results slide, and "Click" is a PowerPoint click build. Every slide has speaker
notes with thesis references. Per-slide sources and times are in
`OVERLEAF/PPT/defence_script.md`. Every talk slide carries the section bar, and a roadmap slide
(`section_roadmap`) opens each part with its group of the pipeline highlighted.

## Motivation (1–8)
1. **Cover.** KTH blue.
   - Title and subtitle, author, "Master's thesis defence, carried out at ABB Robotics".
   - Examiner Dimos V. Dimarogonas and the four supervisors.
2. **Adhesive bonding with an ABB YuMi.** The YuMi photo (GE Healthcare, ABB customer story),
   two lines and the customer's quote, with the source caption under the photo.
3. **Current practice.** Timeline strips, six clicks:
   - adhesive A, replayed ✓✓✓;
   - adhesive B, seated too late ✗, then the timing is reprogrammed ✓;
   - bead moved, off the bead ✗, then the path is reprogrammed ✓;
   - the closing lines.
4. **From programming to generation.** Program, Imitate and Generate panels, one per click,
   without badges or italic second lines. In the Generate panel a zone stated after training
   rejects three samples.
5. **Requirements that change after training.** The thesis requirements figure without its
   (a)–(c) labels.
6. **Problem.** Figure 1.1. On click, the problem box and the line on training-time
   conditioning.
7. **Aim and research questions.**
   - The aim (§1.3), with the gloss of the learned prior.
   - RQ1: does a demonstration determine the requirement?
   - RQ2: does the robustness score alone determine a trajectory? (§1.2)
   - The Method callout: STL-FM, robustness guidance of the learned prior.
8. **Approach.** The simplified system pipeline in full, with no badges.

## Background (9–16)
9. **Stating the requirement.** Roadmap, requirement row highlighted.
10. **Signal Temporal Logic.** The requirement in words. On click, eq. (1.1) typeset; on a
    second click, what the requirement bounds. Below that, a small added line folding in the
    evaluated fragment: "predicates μ, negation, conjunction, bounded ◇ and ◻". The talk does
    not mention disjunction and until (not in the report the examiner received; backup 43).
    Cite Maler and Nickovic 2004.
11. **Robustness** (merged from the former Evaluated fragment / Quantitative robustness / Smooth
    robustness, 2026-10-23). The robustness recursion for the fragment and soundness, the
    log-sum-exp (smooth) definition, above one new figure: a 1D plot of an avoidance margin c(t)
    over time, left panel showing the exact robustness as a single minimizing witness instant
    t*, right panel showing the smooth surrogate's gradient spreading over several neighbouring
    instants near t*, κ = 10. The old cell figure (+2.6, −8.6, −6.0 cm) and the old cell-view
    gradient-arrows figure are no longer used. Cite Donzé and Maler 2010; Leung et al. 2021;
    Kapoor et al. 2025.
12. **Learning the prior.** Roadmap, prior row highlighted.
13. **Flow matching.** The Fig. 3.1 animation (click) beside the FM loss with the linear path
    and the generative ODE, with K = 64. Cite Lipman et al. 2023 and Liu et al. 2022.
14. **Generation from noise.** The diffusion clip (click). The notes say it is diffusion.
15. **Related work.** Five paper-figure tiles (CTG highlighted) and the STL-FM tile, with the
    caption "figures reproduced from the cited papers".
16. **Comparison of approaches (on trial).** A table of seven approaches:
    - trajectory optimization;
    - control barrier functions (Lindemann and Dimarogonas 2019);
    - TeLoGraF;
    - ZSTP;
    - SafeDiffuser;
    - CTG;
    - STL-FM.

    The columns are where the requirement enters, the rest of the motion from, and the
    property. All cells come from Ch. 2. The footer reads "Entries summarize the cited works".

(Dropped 2026-10-22, author: no significant new information — **Learned prior**, demonstrations
beside unguided-prior samples, formerly 17.)

## Method (17–19)
17. **Guiding the prior.** Roadmap, guided sampler highlighted.
18. **Guided velocity field.**
    - eq. (4.4) with underbraces.
    - The penalized objective and the masked, normalized gradient.
    - "λ₀ ≥ 0 is one constant strength", and "no component of the sampling loop is trained".
19. **Guided sampler.** The loop line, and the four update equations of Algorithm 2 lines
    4–13: τ̂, g, the Euler step and the re-pin. A closing line on why τ̂ and not τ(s), and
    "The full sampler is in backup" bottom left.

## Results (20–27)
20. **Evaluating the plans.** Roadmap, plan and execution highlighted.
21. **Experimental setup.** The scenes and a planner × {prior, requirement, endpoint pin} table
    with full planner names, and a note that STL-FM with endpoint pin differs by at most 0.05 on
    any of the six classes.
22. **Six requirement classes.** Six classes, each with its formula and a pair of panels,
    STL-FM beside the STL Optimizer (added 2026-10-23). Claim: one prior and one λ₀ are used for
    all six.
23. **Logic satisfaction and time to satisfaction** (merged from former 25–26, 2026-10-23). Two
    stacked panels over classes 1–6: satisfaction-rate bars on top, first satisfaction in estimated
    seconds below (the percentage-of-budget panel was dropped). Claim: STL-FM satisfies most
    classes at comparable rates and plans 5 to 25 times faster. Cube and kitchen plan times are in
    the notes; the budget-percentage narrative was cut from the notes along with the panel.
24. **Arena excursion.** The STL Optimizer against STL-FM on sequence with
    avoidance. Claim: every plan of the STL Optimizer for that class leaves the
    arena.
25. **Underdetermination by robustness.** The sparse and unbounded figure, with m of 64 to 256.
    Claim: robustness alone does not determine a trajectory (backup).
26. **Cube manipulation.** The sequence requirement in words and as a formula, its predicates,
    and the STL-FM video. Claim: 10 of 30 against none. The carry gap (12.5 against 6.9 cm) that
    explains the gap in completions is in the notes and in backup slide 45's table, not on its own
    slide.
27. **Logic satisfaction and task success.** Pooled bars and STL-FM per class. Claim: each
    occurs without the other.

(Dropped 2026-10-22, author: no significant new information — **Carry gap**, the planned paths
and the STL Optimizer video with the pooled median gap per planner, formerly 32; its one number
not already on slide 26 or in backup moved to the notes there and to backup slide 45.)

## Conclusions (28–30)
28. **Conclusions.** RQ1, RQ2 and Method callouts with their answers, and the line that logic
    satisfaction and task success do not coincide.
29. **Future work.** Five numbered items:
    1. differentiable dynamics;
    2. physical platform;
    3. parameter sweep;
    4. barrier-filtered execution.

    The kitchen figure sits beside them.
30. KTH logo end slide.

(Dropped 2026-10-22, author: no significant new information — **Evaluation metrics**, the
logic-satisfaction and task-success formulas, a run, and the fixed-instance remark, formerly 25.
The terms themselves are still used from slide 22 on, defined informally in the notes rather than
on their own slide; the fixed-instance remark moved to backup if asked.)

## Backup (31–49)
- 31 Supplementary material (light-blue divider).
- 32 Plausible samples that violate the requirement.
- 33–37, the formal results in plain language. Each slide has the key formula on top, the
  statement in words, and a muted closing line. There are no numbers, equation tags or pointers
  to the thesis.
  - 33 Requirements witnessed by one demonstration (Prop A.1.2). Closing line: RQ1 has a
    negative answer.
  - 34 Sparsity of the robustness gradient (Prop A.3.1). Closing line: m is 1 to 5 against
    horizons of 64 to 256.
  - 35 Maximizers of a reach requirement (Prop A.3.3, new). Closing line: maximality implies
    nothing about plausibility.
  - 36 Unbounded maximizers under avoidance (Prop A.3.4). Closing line: the free coordinates
    come from a component other than the requirement. It is not tied to the arena excursion,
    which the no-avoidance ablation shows is not caused by avoidance.
  - 37 Maximization over plausible trajectories (Thm A.3.6). Existence, determinacy and
    plausibility appear as bold run-ins. Closing line: the learned prior satisfies neither
    hypothesis.
- 38 Constant guidance strength: eq:tweedie against the FM target and eq:guided-bounded, "well
  posed", Θ(λ₀), λ₀ = 50, λ(t) ∝ σₜᵏ.
- 39 Compilation and smoothing bias (Algorithm 1 and Prop 4.2.1, plain language, 16 pt).
- 40 Steps of the guided sampler (Algorithm 2, plain language, five numbered steps; the clamp
  is off in all reported runs).
- 41 Reproducing the STL Optimizer (added 2026-10-22): single-integrator controls, the same
  stljax/STLCG++ score STL-FM's guidance uses, the violation-penalty objective and its
  regularizers, the 1,500–6,000-step budget. Closing line: STLCG++ supplies the score; the
  optimization design follows Belta and Vasile 2020, not STLCG++ itself.
- 42 Tables 5.4 and 5.5. 43 Disjunction and until in navigation, classes 7–10, which the report
  given to the examiner did not contain (panels, a satisfaction and plan-time table, ordered visit).
  44 Robustness against budget, the ten per-class curves. 45 Table 5.6, carry gap included. Both
  table slides are still crops, with the thesis class numbers. The notes name the classes.
- 46 Kitchen study. 47 Physical platform. 48 Roughness of guided plans. 49 Limitations.
