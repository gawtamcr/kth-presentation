# Deck summary, slide by slide (STL-FM Defense.pptx, 52 slides, KTH revision 2026-10-21, self-contained the same day, synced with the thesis 2026-10-22, trimmed 2026-10-22)

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

## Background (9–18)
9. **Stating the requirement.** Roadmap, requirement row highlighted.
10. **Signal Temporal Logic.** The requirement in words. On click, eq. (1.1) typeset; on a
    second click, what the requirement bounds. Cite Maler and Nickovic 2004.
11. **Evaluated fragment.** The grammar φ ::= μ | ¬μ | φ₁∧φ₂ | ◇[a,b]φ | □[a,b]φ, then a table
    of the constructs with their readings and load-and-bond examples. The talk does not
    mention disjunction and until (not in the report the examiner received; backup 46).
12. **Quantitative robustness.** The robustness recursion for the fragment and soundness,
    above the cell figure (+2.6, −8.6, −6.0 cm, illustrative). Cite Donzé and Maler 2010.
13. **Smooth robustness.** The log-sum-exp definition and the exact-versus-smoothed gradient
    figure; κ = 10, scored exactly. Cite Leung et al. 2021 and Kapoor et al. 2025.
14. **Learning the prior.** Roadmap, prior row highlighted.
15. **Flow matching.** The Fig. 3.1 animation (click) beside the FM loss with the linear path
    and the generative ODE, with K = 64. Cite Lipman et al. 2023 and Liu et al. 2022.
16. **Generation from noise.** The diffusion clip (click). The notes say it is diffusion.
17. **Related work.** Five paper-figure tiles (CTG highlighted) and the STL-FM tile, with the
    caption "figures reproduced from the cited papers".
18. **Comparison of approaches (on trial).** A table of seven approaches:
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

## Method (19–21)
19. **Guiding the prior.** Roadmap, guided sampler highlighted.
20. **Guided velocity field.**
    - eq. (4.4) with underbraces.
    - The penalized objective and the masked, normalized gradient.
    - "λ₀ ≥ 0 is one constant strength", and "no component of the sampling loop is trained".
21. **Guided sampler.** The loop line, and the four update equations of Algorithm 2 lines
    4–13: τ̂, g, the Euler step and the re-pin. A closing line on why τ̂ and not τ(s), and
    "The full sampler is in backup" bottom left.

## Results (22–30)
22. **Evaluating the plans.** Roadmap, plan and execution highlighted.
23. **Experimental setup.** The scenes and a planner × {prior, requirement, endpoint pin} table
    with full planner names, and a note that STL-FM with endpoint pin differs by at most 0.05 on
    any of the six classes.
24. **Six requirement classes.** Six STL-FM panels. Claim: one prior and one λ₀ are used for
    all six.
25. **Logic satisfaction in navigation.** Bar chart over classes 1–6. Claim: logic satisfaction
    alone does not distinguish STL-FM from the STL Optimizer.
26. **Time to satisfaction.** Two stacked panels over classes 1–6, first satisfaction as a percentage of
    the budget and in estimated seconds, for STL-FM and the STL Optimizer. Claim: the
    optimizer satisfies the requirement earlier in its budget but later in wall-clock time. Cube and
    kitchen plan times are in the notes.
27. **Arena excursion.** The STL Optimizer against STL-FM on sequence with
    avoidance. Claim: every plan of the STL Optimizer for that class leaves the
    arena.
28. **Underdetermination by robustness.** The sparse and unbounded figure, with m of 64 to 256.
    Claim: robustness alone does not determine a trajectory (backup).
29. **Cube manipulation.** The sequence requirement in words and as a formula, its predicates,
    and the STL-FM video. Claim: 10 of 30 against none. The carry gap (12.5 against 6.9 cm) that
    explains the gap in completions is in the notes and in backup slide 48's table, not on its own
    slide.
30. **Logic satisfaction and task success.** Pooled bars and STL-FM per class. Claim: each
    occurs without the other.

(Dropped 2026-10-22, author: no significant new information — **Carry gap**, the planned paths
and the STL Optimizer video with the pooled median gap per planner, formerly 32; its one number
not already on slide 29 or in backup moved to the notes there and to backup slide 48.)

## Conclusions (31–33)
31. **Conclusions.** RQ1, RQ2 and Method callouts with their answers, and the line that logic
    satisfaction and task success do not coincide.
32. **Future work.** Five numbered items:
    1. differentiable dynamics;
    2. physical platform;
    3. parameter sweep;
    4. barrier-filtered execution.

    The kitchen figure sits beside them.
33. KTH logo end slide.

(Dropped 2026-10-22, author: no significant new information — **Evaluation metrics**, the
logic-satisfaction and task-success formulas, a run, and the fixed-instance remark, formerly 25.
The terms themselves are still used from slide 24 on, defined informally in the notes rather than
on their own slide; the fixed-instance remark moved to backup if asked.)

## Backup (34–52)
- 34 Supplementary material (light-blue divider).
- 35 Plausible samples that violate the requirement.
- 36–40, the formal results in plain language. Each slide has the key formula on top, the
  statement in words, and a muted closing line. There are no numbers, equation tags or pointers
  to the thesis.
  - 36 Requirements witnessed by one demonstration (Prop A.1.2). Closing line: RQ1 has a
    negative answer.
  - 37 Sparsity of the robustness gradient (Prop A.3.1). Closing line: m is 1 to 5 against
    horizons of 64 to 256.
  - 38 Maximizers of a reach requirement (Prop A.3.3, new). Closing line: maximality implies
    nothing about plausibility.
  - 39 Unbounded maximizers under avoidance (Prop A.3.4). Closing line: the free coordinates
    come from a component other than the requirement. It is not tied to the arena excursion,
    which the no-avoidance ablation shows is not caused by avoidance.
  - 40 Maximization over plausible trajectories (Thm A.3.6). Existence, determinacy and
    plausibility appear as bold run-ins. Closing line: the learned prior satisfies neither
    hypothesis.
- 41 Constant guidance strength: eq:tweedie against the FM target and eq:guided-bounded, "well
  posed", Θ(λ₀), λ₀ = 50, λ(t) ∝ σₜᵏ.
- 42 Compilation and smoothing bias (Algorithm 1 and Prop 4.2.1, plain language, 16 pt).
- 43 Steps of the guided sampler (Algorithm 2, plain language, five numbered steps; the clamp
  is off in all reported runs).
- 44 Reproducing the STL Optimizer (added 2026-10-22): single-integrator controls, the same
  stljax/STLCG++ score STL-FM's guidance uses, the violation-penalty objective and its
  regularizers, the 1,500–6,000-step budget. Closing line: STLCG++ supplies the score; the
  optimization design follows Belta and Vasile 2020, not STLCG++ itself.
- 45 Tables 5.4 and 5.5. 46 Disjunction and until in navigation, classes 7–10, which the report
  given to the examiner did not contain (panels, a satisfaction and plan-time table, ordered visit).
  47 Robustness against budget, the ten per-class curves. 48 Table 5.6, carry gap included. Both
  table slides are still crops, with the thesis class numbers. The notes name the classes.
- 49 Kitchen study. 50 Physical platform. 51 Roughness of guided plans. 52 Limitations.
