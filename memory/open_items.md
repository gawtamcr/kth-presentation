# Open items (2026-10-21, after the KTH revision)

## Pending author review
- **Whole deck:** the KTH revision has been built and checked for layout in a PowerPoint
  render. The author has not yet reviewed it.
- **Slide 19:** the comparison table is on trial. The author asked to see how it looks before
  deciding to keep it.
- **Language:** the `academic-voice` and `terminology` reports on headings, claim lines and
  notes were applied on 2026-10-21, except the items listed below. The notes are still sketches.
- **Left for the author (the reports raised them; the deck follows the thesis):**
  - The cover subtitle "Imposing temporal requirements on a generative motion prior" is the
    registered thesis subtitle, although the term sheet allows neither "temporal requirement"
    nor "generative prior".
  - "Logic satisfaction" (thesis results chapters) against the sheet's "requirement
    satisfaction".
  - "Predicted endpoint" τ̂(s) against "endpoint pin" and "endpoint-inpaint", where
    endpoint means the final state. The thesis has the same dual use.
  - The problem box wording "plausible under the demonstrations" (term sheet D1).
  - The thesis itself still has "plausibility prior", "task-agnostic demonstrations" (Problem
    4.1) and "task" for φ (l.1654, l.1884).
- **Timing:** not rehearsed. The estimate is 22.7 min for 34 talk slides, including four
  roadmap slides at 10 s each (see `defence_script.md`).

## Known issues
- **Figtree is not installed on Windows.** The template's embedded subset is dropped by the
  build because it garbled text, so PowerPoint substitutes Calibri. Install Figtree, from Google
  Fonts under the OFL, on the render machine and on the defence laptop. Then re-render and
  recheck the line breaks: the layout was checked with Arial and Calibri metrics.
- **Carry-gap units in the thesis.**
  - Table `tab:closedloop` gives per-class gaps in cm (6.5–13.2) but a pooled row of
    0.64 / 0.69 / 1.25.
  - The text gives pooled medians of 12.5 cm and 6.9 cm.
  - The panels `cube_sequence_*.pdf` print "gap 1.30" / "gap 0.68".
  - The pooled row and the panels look like decimetres.
  - Slide 31 quotes only the text's pooled medians. The author should fix the thesis or be
    ready for the question; backup slide 47 shows the table.
- **June cube videos** may not match the final setup (λ₀ = 50, κ = 10, final windows). The
  author accepted them for now.
- **Backup crops:** only the three tables (slides 46–47) are still crops, from a thesis compiled
  on 2026-10-21 00:22. Rerun `make_backup_crops.py` after thesis changes, because the page numbers
  in its `ITEMS` list may shift. Its proposition and algorithm crops (`bk_prop_*`, `bk_thm_*`,
  `bk_alg_*`) are no longer used.
- **Plain-language backup slides 38–45:** these are paraphrases of the thesis statements. If a
  statement in `appendix.tex` or §4.2 changes, update the slide text and the formula in
  `make_math.py`.

## Possible next steps
1. Author review of the KTH revision, and a decision on the trial table (slide 19).
2. Install Figtree, then re-render and recheck the breaks.
3. Rehearse and time; trim if over 22 minutes.
4. Optionally re-render the cube videos from the final checkpoints for slides 30–31.
