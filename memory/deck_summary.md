# Deck summary, slide by slide (STL-FM Defense.pptx, 51 slides, KTH revision 2026-10-21, self-contained the same day)

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

## Background (9–19)
9. **Stating the requirement.** Roadmap, requirement row highlighted.
10. **Signal Temporal Logic.** The requirement in words. On click, eq. (1.1) typeset; on a
    second click, what the requirement bounds. Cite Maler and Nickovic 2004.
11. **Evaluated fragment.** The grammar φ ::= μ | ¬μ | φ₁∧φ₂ | ◇[a,b]φ | □[a,b]φ, then a table
    of the constructs with their readings and load-and-bond examples. Disjunction and until
    are not evaluated.
12. **Quantitative robustness.** The robustness recursion for the fragment and soundness,
    above the cell figure (+2.6, −8.6, −6.0 cm, illustrative). Cite Donzé and Maler 2010.
13. **Smooth robustness.** The log-sum-exp definition and the exact-versus-smoothed gradient
    figure; κ = 10, scored exactly. Cite Leung et al. 2021 and Kapoor et al. 2025.
14. **Learning the prior.** Roadmap, prior row highlighted.
15. **Flow matching.** The Fig. 3.1 animation (click) beside the FM loss with the linear path
    and the generative ODE, with K = 64. Cite Lipman et al. 2023 and Liu et al. 2022.
16. **Generation from noise.** The diffusion clip (click). The notes say it is diffusion.
17. **Learned prior.** Navigation demonstrations beside samples of the unguided prior.
18. **Related work.** Five paper-figure tiles (CTG highlighted) and the STL-FM tile, with the
    caption "figures reproduced from the cited papers".
19. **Comparison of approaches (on trial).** A table of seven approaches:
    - trajectory optimization;
    - control barrier functions (Lindemann and Dimarogonas 2019);
    - TeLoGraF;
    - ZSTP;
    - SafeDiffuser;
    - CTG;
    - STL-FM.

    The columns are where the requirement enters, the rest of the motion from, and the
    property. All cells come from Ch. 2. The footer reads "Entries summarize the cited works".

## Method (20–22)
20. **Guiding the prior.** Roadmap, guided sampler highlighted.
21. **Guided velocity field.**
    - eq. (4.4) with underbraces.
    - The penalized objective and the masked, normalized gradient.
    - "λ₀ ≥ 0 is one constant strength", and "no component of the sampling loop is trained".
22. **Guided sampler.** The loop line, and the four update equations of Algorithm 2 lines
    4–13: τ̂, g, the Euler step and the re-pin. A closing line on why τ̂ and not τ(s), and
    "The full sampler is in backup" bottom left.

## Results (23–32)
23. **Evaluating the plans.** Roadmap, plan and execution highlighted.
24. **Experimental setup.** The scenes and a planner × {prior, requirement, endpoint pin} table
    with full planner names, and a note on STL-FM with endpoint pin.
25. **Evaluation metrics.** The formulas for the logic-satisfaction and task-success rates, a
    run, and the fixed-instance remark.
26. **Six requirement classes.** Six STL-FM panels. Claim: one prior and one λ₀ are used for
    all six.
27. **Logic satisfaction in navigation.** Bar chart. Claim: logic satisfaction alone does not
    distinguish STL-FM from the requirement-only optimizer.
28. **Arena excursion.** The requirement-only optimizer against STL-FM on sequence with
    avoidance. Claim: every plan of the requirement-only optimizer for that class leaves the
    arena.
29. **Underdetermination by robustness.** The sparse and unbounded figure, with m of 64 to 256.
    Claim: robustness alone does not determine a trajectory (backup).
30. **Cube manipulation.** The sequence requirement in words and as a formula, its predicates,
    and the STL-FM video. Claim: 10 of 30 against none (Fisher p = 0.0008).
31. **Carry gap.** The planned paths and the requirement-only video, with a line on the pooled
    median gap per planner (12.5 against 6.9 cm). Claim: without the prior the planned cube
    moves without contact.
32. **Logic satisfaction and task success.** Pooled bars and STL-FM per class. Claim: each
    occurs without the other.

## Conclusions (33–35)
33. **Conclusions.** RQ1, RQ2 and Method callouts with their answers, and the line that logic
    satisfaction and task success do not coincide.
34. **Future work.** Five numbered items:
    1. differentiable dynamics;
    2. physical platform;
    3. parameter sweep;
    4. barrier-filtered execution;
    5. disjunction and until.

    The kitchen figure sits beside them.
35. KTH logo end slide.

## Backup (36–51)
- 36 Supplementary material (light-blue divider).
- 37 Plausible samples that violate the requirement.
- 38–42, the formal results in plain language. Each slide has the key formula on top, the
  statement in words, and a muted closing line. There are no numbers, equation tags or pointers
  to the thesis.
  - 38 Requirements witnessed by one demonstration (Prop A.1.2). Closing line: RQ1 has a
    negative answer.
  - 39 Sparsity of the robustness gradient (Prop A.3.1). Closing line: m is 1 to 5 against
    horizons of 64 to 256.
  - 40 Maximizers of a reach requirement (Prop A.3.3, new). Closing line: maximality implies
    nothing about plausibility.
  - 41 Unbounded maximizers under avoidance (Prop A.3.4). Closing line: the free coordinates
    come from a component other than the requirement. It is not tied to the arena excursion,
    which the no-avoidance ablation shows is not caused by avoidance.
  - 42 Maximization over plausible trajectories (Thm A.3.6). Existence, determinacy and
    plausibility appear as bold run-ins. Closing line: the learned prior satisfies neither
    hypothesis.
- 43 Constant guidance strength: eq:tweedie against the FM target and eq:guided-bounded, "well
  posed", Θ(λ₀), λ₀ = 50, λ(t) ∝ σₜᵏ.
- 44 Compilation and smoothing bias (Algorithm 1 and Prop 4.2.1, plain language, 16 pt).
- 45 Steps of the guided sampler (Algorithm 2, plain language, five numbered steps; the clamp
  is off in all reported runs).
- 46 Tables 5.4 and 5.5. 47 Table 5.6. Both are still crops, with the thesis class numbers. The
  notes name the classes.
- 48 Kitchen study. 49 Physical platform. 50 Roughness of guided plans. 51 Limitations.
