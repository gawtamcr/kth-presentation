# Decisions log (2026-10-20 to 2026-10-21)

Each decision with its reason, in the order made. Later decisions override earlier ones.

## Process
- Work top-down: outline → per-slide script → visuals → build → (rehearsal, not done).
- The original deck was criticised and replaced, not edited: no results, claims that
  contradicted the thesis (said "diffusion", "CBFs", "formally verified", "formal
  guarantees"), wrong research question, empty dividers, text walls, mid-term residue.
- Removed `Refs/Thesis Defense Final.pptx` (superseded). Kept the mid-term deck and Laura's deck.
- Outline v2 (Laura-informed, roadmap slides) was adopted. A from-scratch v3 and an
  animation-heavy sample slide were rejected; the author asked to return to v2.

## Audience and story
- Audience is academic (examiner + opponent): one formal slide in the talk, the
  propositions in backup.
- Roadmap = a simplified version of the thesis's `fig_system_pipeline`, drawn natively,
  shown in full on slide 7 with the aim and contributions ①–③, then highlighted per section
  (8 requirement, 13 prior, 18 sampler, 22 plan/execution). Contributions are previewed on
  slide 7 and recapped on slide 32; no separate contributions slide.
- The method is presented before the formal result. The excursion slide and the formal
  "robustness alone does not determine a trajectory" slide sit in Results and analysis
  (27–28), after the navigation bar chart (26). The six-class STL-FM panels moved to results (25).
- Kitchen and physical-platform (GoFA) studies: backup only (45–46); they also appear as
  images on the future-work slide.

## Act A (redone 2026-10-21 after author feedback)
- The author found generative models introduced abruptly and the problem unclear.
- Slide 2 is the author's ABB example: single-arm YuMi applying fast-setting glue at GE
  Healthcare (photo from the ABB customer story; quote "Even in half an hour, we can get some
  major changes done to the code"). Rebuilt natively from the author's PowerPoint slide.
- Slide 3: today's practice as a click build of timeline strips: one programmed motion
  replayed; a new adhesive → seated too late → timing reprogrammed; bead moved → off the bead →
  path reprogrammed; "each change is a change in the code; timing and position exist only
  inside the program".
- Slide 4: program → imitate → generate, one column per click. **The headline reason for a
  generative model is the thesis's own (§3.3.1): regression returns one trajectory per input;
  a generative model represents a distribution, so a requirement stated later has
  alternatives to select from.** Generalization near the demonstrations is noted in column 2;
  multimodality (averaging) is only a supporting point in the notes. The author explicitly
  criticised "multiple paths" as the main motivation.
- Slide 5: the thesis requirements figure without (a)/(b)/(c), captions kept.
- Slide 6: Figure 1.1 plus an explicit problem statement (click). The old "training or
  inference" slide is merged into it.
- From the author's pasted TL;DR, only the conventional-vs-generative contrast was used. Not
  used, because the thesis does not do or claim them: "conditioned on camera observations",
  "improve placement success compared with conventional motion planning".

## Background, method, results
- STL is taught on the real-world load-and-bond requirement (thesis eq. 1.1):
  ◇[a,b] ◻[0,d] seated ∧ ◻[0,T] ¬operator. Robustness is shown as a margin in cm (distance to
  seat, clearance), never as a time margin.
- Thesis notation: ◇ eventually, ◻ always (not F/G).
- Fig. 3.1 is animated (exception to minimal motion, author's request) and is followed by
  `media1.mp4`, which is a diffusion clip the author keeps; its title and notes do not call it
  flow matching.
- Related work (slide 17) uses images, not text: overview figures of TeLoGraF, ZSTP,
  Kurtz and Lin, SafeDiffuser, CTG (highlighted) and an STL-FM tile.
- Slide 20 (predicted endpoint) redraws one sampler step natively; the thesis dataflow figure
  is too dense at slide size (it is in backup as Algorithm 2).
- Slide 21's velocity/score plot is a labelled schematic.
- STL-FM with endpoint pin is folded into notes and a backup table.
- June cube videos (`CODE/flow-3d/results/ogbench/single/single_noobstacle/viz/`) are used
  as they are.

## Results wording, corrected against the thesis
- Navigation: the requirement-only optimizer satisfies every class on every run; STL-FM
  0.78–1.00 on classes 2–6, 0.96 on reach; endpoint-inpaint only reach. Satisfaction alone
  does not separate the planners; evidence for the prior is the arena excursion (median
  largest coordinate 10.27 vs half-width 5.0, at steps 31–63) and the cube carry gap, not smoothness.
- Cube (OGBench single cube, 10 runs × 3 classes): requirement-only 30/30 satisfied, 0/30
  completed; STL-FM 20/30 satisfied, 10/30 completed (Fisher p = 0.0008); endpoint-inpaint
  1/30, 1/30. STL-FM's completions come mostly from nested reach-and-dwell (logic 1/10, task
  9/10); on sequence 10/10 logic, 1/10 task. Message: logic satisfaction and task success
  each occur without the other.
- Pooled median carry gap 12.5 cm (requirement-only) vs 6.9 cm (STL-FM), Mann–Whitney p < 1e-6.
- "One prior serves six requirement classes" — not a claim that adaptation to a changed
  parameter was tested (that sweep is future work, §7.2).
- Planner names follow the thesis: endpoint-inpaint planner, STL-FM, STL-FM with endpoint
  pin, requirement-only optimizer.

## KTH revision (2026-10-21, author's answers; these override the rules above where they differ)
Reference deck: nilsjor/kth-doctoral-thesis-presentation. Examiner: Dimos V. Dimarogonas.
Critique adopted: the deck looked generated. The signs were uniform sentence titles; badges,
three-card layouts, italic micro-labels and pastel box diagrams; a schematic plot that
looked like data; and five copies of the roadmap. It also lacked formal definitions and any
positioning against control synthesis under STL.

**Template and headings**
- Template: the official KTH template (`assets/kth_template.potx`), with ABB credited on the
  cover. Rejected: keeping the ABB template; KTH Beamer.
- Headings: short noun phrases everywhere. Rejected: hybrid; keeping sentence titles.
- Claims: one line on results slides only, under the evidence. Rejected: every slide; notes only.

**Math and framing**
- Math depth: definitions only in the talk. That means STL syntax and robustness, the FM loss
  and ODE, the guided velocity and conditioning, the sampler step and the metrics.
  Propositions stay in backup. Rejected: the formal core in the talk; the current level.
- Framing: the two questions of §1.2 as RQ1 and RQ2 (slide 7), answered on Conclusions (29),
  plus the Method callout. Rejected: aim and contributions only.

**Cuts**
- Accepted: only the roadmaps to a progress bar (old slides 8, 13, 18 and 22 deleted).
- Rejected: dropping the diffusion clip, merging Act A from five slides to three, and
  folding the metrics and six-class slides.

**Positioning and slide 21**
- Positioning: keep the related-work tiles as they are and add a comparison table "to see
  how it looks". The table is slide 17, **on trial**, and includes control barrier functions
  (Lindemann and Dimarogonas 2019). Rejected: a sixth tile with a backup slide on the CBF
  relation.
- The old slide 21 (constant strength) moves to backup (slide 38). It is rebuilt from the
  thesis expressions: the score against the FM target, and eq:guided-bounded with "well
  posed". The schematic plot and its generator were removed.

**Smaller choices made in implementation**
- The grammar sits on the "Evaluated fragment" slide (10), not on the STL slide (9), to avoid
  repeating the construct table.
- The approach roadmap is shown once, as slide 8, after the RQ slide, without badges.
- Equations are typeset by lualatex in the thesis fonts (`make_math.py`). Inline symbols stay
  Cambria Math.
- Figures and diagrams keep the thesis palette; the KTH palette is used for the chrome
  (headings, section bar).

**Language pass (same day, from the academic-voice and terminology reports)**

The main on-slide changes:
- **Slide 6:** retraining is scoped to "outside its distribution" (thesis l.1023).
- **Slide 38:** the ratio is stated as Θ(λ₀), "of the same bounded order".
- **Slide 29:**
  - RQ2 states its answer and scopes the excursion to the two sequence classes.
  - The method line names whose rate it gives.
  - The closing line is "do not coincide".
- **Slide 24:** the claim names the requirement-only optimizer.
- **Headings:** slide 2 is now "Adhesive bonding with an ABB YuMi", and slide 25 is now
  "Underdetermination by robustness".
- **Terms:**
  - "learned prior" is introduced on slide 7;
  - "unguided prior" is used for prior samples without a requirement;
  - the class is spelled "nested reach-and-dwell" (also in the two charts);
  - planner names are written in full on slide 20.
- **Slide 43:** the kitchen numbers are scoped (complete-v2, mean robustness, task success
  0 of 80).
- **Slide 30:** future work has five items.

**Roadmap slides restored (same day, author's request: "Add the roadmap slides also")**
- The four section roadmap slides are back, each highlighting its group of the pipeline as in
  the earlier deck:
  - 9 "Stating the requirement" (Background);
  - 14 "Learning the prior" (Background);
  - 20 "Guiding the prior" (Method);
  - 23 "Evaluating the plans" (Results).
- The section bar stays on every talk slide as well.
- The build drops the template's embedded Figtree subset, which made PowerPoint draw garbled
  text. PowerPoint uses an installed Figtree, and otherwise substitutes Calibri.

## Self-contained slides (2026-10-21, author's request: "The slides must be self-contained. Remove all references to thesis doc like proposition etc.")
- No slide names a thesis proposition, theorem, equation, algorithm, table, figure, section or
  chapter. Alt texts follow the same rule.
- Talk slides:
  - slide 19, footer "Entries summarize the cited works";
  - slide 22, "The full sampler is in backup";
  - slide 29, the claim ends "(backup)";
  - slide 33, the proposition numbers were removed from the RQ1 and RQ2 answers.
- "This thesis" meaning the work itself stays on the cover notes, slide 11 and the STL-FM row
  of slide 19.
- Formal backup slides, author's answers:
  - **Plain-language statements**, each with one key formula. Rejected: re-typesetting the
    statements unnumbered, and masking the numbers in the crops.
  - Headings name the result. The words "Proposition" and "Theorem" do not appear on the slides.
  - **Proposition A.3.3 was added** as slide 40, because the theorem refers to it. Rejected:
    rewriting the theorem without it.
- Speaker notes: the spoken text names no thesis item, and the **bracketed source tags are
  kept** as the presenter's aid. Rejected: stripping both, and leaving the notes unchanged.
- Results tables (46–47): the **crops are kept**. They carry no explicit pointer, only the
  thesis class numbers and planner letters; the notes give the class names. Rejected: native
  tables with names.
