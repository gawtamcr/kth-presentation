# Defence deck — handoff (start here)

Context for a new Claude instance working on the thesis defence presentation.
Last updated 2026-10-21 (KTH revision). Read this file, then `deck_summary.md` (every slide in
deck order), `decisions.md`, then `open_items.md`.

## What this is
A 25-minute defence talk for the KTH master's thesis *STL-FM: Trajectory Planning Through
STL-Guided Flow Matching*.
- Author: Gawtam Chithra Ramesh. Examiner: Dimos V. Dimarogonas (KTH DCS; STL control
  synthesis, CBFs for STL).
- Supervisors: Luzia Knödler, Shaohang Han, Matthew Lock and Jonathan Styrud.
- Audience: the examiner and the opponent.
- Template: the official KTH PowerPoint template. The thesis was done at ABB, which is credited
  on the cover.
- The thesis is `OVERLEAF/kth-thesis/main_thesis.tex` (+ `appendix.tex`). Every slide claim
  must match it.

## State on 2026-10-21
`OVERLEAF/PPT/STL-FM Defense.pptx` has 51 slides, all built by script and checked in a
PowerPoint render:
- 1 cover, then Motivation 2–8, Background 9–19, Method 20–22, Results 23–32 and
  Conclusions 33–34. Slide 35 is the KTH logo end slide.
- Roadmap slides open each part: 9 requirement, 14 prior, 20 sampler, 23 plan and execution.
- 36–51 are backup: the divider, plausible samples, five formal results in plain language,
  constant guidance strength, compilation and the sampler in plain language, three tables,
  kitchen, physical platform, roughness and limitations.
- The slides are self-contained (author's request, 2026-10-21). No slide or spoken note names a
  thesis proposition, theorem, equation, algorithm, table, figure, section or chapter. Thesis
  sources stay only in the bracketed tag at the end of each note and in `defence_script.md`.

The slide list with times is at the top of `OVERLEAF/PPT/defence_script.md`. Every slide has
speaker notes. Rehearsal timing has not been done; the estimate is 22.7 min.

## Files
| Path | Role |
|---|---|
| `OVERLEAF/PPT/STL-FM Defense.pptx` | **Generated** deck. Never edit by hand: a rebuild overwrites it. |
| `OVERLEAF/PPT/assets/kth_template.potx` | KTH PPT template 251203 (copied from the author's desktop). Read-only template: masters and layouts. Its embedded Figtree subset is dropped by the build. |
| `OVERLEAF/PPT/Thesis FINAL Defense.pptx` | The author's original ABB deck. No longer used by the build; kept for reference. |
| `OVERLEAF/PPT/defence_script.md` | Deck order with times, and per-slide content and thesis sources. |
| `OVERLEAF/PPT/assets/build_deck.py` | Builds the whole deck. All slide content lives in `slides()`, in deck order. |
| `OVERLEAF/PPT/assets/make_math.py` | Display equations, typeset by lualatex from the thesis LaTeX (thesis macros and fonts) to `eq_<name>.png`. |
| `OVERLEAF/PPT/assets/make_static_figs.py` | The matplotlib figures (TeX Gyre Termes, thesis palette). |
| `OVERLEAF/PPT/assets/fig_transport_anim.py`, `make_transport_anim.sh` | Fig. 3.1 animated. |
| `OVERLEAF/PPT/assets/make_rw_figs.sh` | Crops one overview figure per related-work class from the Zotero PDFs. |
| `OVERLEAF/PPT/assets/make_backup_crops.py` | Crops tables (and, unused since 2026-10-21, propositions and algorithms) from a compiled thesis PDF. |
| `OVERLEAF/PPT/assets/fig_requirements_slide.tex` | The thesis requirements figure without the (a)–(c) labels. |
| `OVERLEAF/PPT/assets/diffusion_clip.mp4`, `diffusion_clip_poster.png` | The diffusion clip (`media1.mp4`) extracted from the ABB deck. |
| `OVERLEAF/PPT/assets/render_deck.sh`, `render_deck.ps1` | Render all slides to PNG through Windows PowerPoint (the visual check). |
| `OVERLEAF/PPT/Refs/` | Laura's final deck and the joint mid-term deck, kept for reference. |

## How to work on it
1. Change slide content in `assets/build_deck.py` (`slides()`).
   - New or changed equations go in `EQS` in `make_math.py`, copied from the thesis label,
     then run `python3 make_math.py [name]`.
   - New figures go in `make_static_figs.py`.
2. Close the deck in PowerPoint first, then run `python3 OVERLEAF/PPT/assets/build_deck.py`.
   The builder:
   - reads the KTH template and creates every slide from a layout;
   - writes the notes;
   - runs the pptx skill's `clean.py`;
   - writes `STL-FM Defense.pptx`.
3. Check visually: `bash OVERLEAF/PPT/assets/render_deck.sh <some scratch dir>`, then look at the
   PNGs. Check every changed slide for overflow, overlap and wrapped headings or claim lines.
4. If the author edits a slide in PowerPoint, port the edit into `build_deck.py` (or extract its
   media into `assets/`) before the next rebuild.

## Builder facts worth knowing
**Layouts:**

| Use | Layout | Notes |
|---|---|---|
| Cover | `slideLayout1` "Title, KTH blue" | ctrTitle, subTitle idx 1 |
| Content | `slideLayout35` "Headline only" | 36 pt navy bold heading at y 1.20; KTH logo top left |
| Backup divider | `slideLayout4` "Title/chapter, light blue" | |
| End | `slideLayout43` "Logo" | |

- Slide size is 13.333 × 7.5 in. The content band is `CX, CW = 0.66, 12.02` and `TOP, BOTTOM = 2.05, 6.90`.
- The slide number is the sldNum placeholder, idx 12.

**Helpers:**
- `content(title, section, subtitle, backup)`. `section` draws the progress bar; `backup=True`
  gives a grey heading and no bar.
- `progress`, `claim(s, text)` (results slides only), `cite(s, text)` (author–year, bottom left).
- `eqimg(s, name, x, y, scale, align)` places an equation at its natural size; 600 dpi
  matches its point size.
- `callout` draws the RQ boxes.
- Also `box`, `label`, `arrow`, `rule`, `picture`, `video` (plays on click), `fit`,
  `roadmap(s, highlight)` and `section_roadmap(title, section, group, notes)`, where the group
  is one of `req`, `prior`, `sampler` or `plan`.
- Click reveals use `s.add(xml, click=k)`. Inline math glyphs use the run option
  `{"math": True}` (Cambria Math), and runs also take `sub` and `sup`.

**Package details:**
- `build()` turns the template content type into a presentation and adds an `mp4`
  content-type default; without it PowerPoint refuses to open the file.
- Notes slides are written from `NOTES_XML`.
- Media keep their asset file names. Avoid `imageN.png` names, which collide with template media.
- The pptx skill scripts (`add_slide.py`, `clean.py`) come from `PPTX_SKILL` (default path
  hard-coded in `build_deck.py`).

## Environment quirks
- **Figtree:** the template embeds only a subset of Figtree. PowerPoint drew text runs whose
  glyphs the subset lacks as garbage, and kept doing so for as long as the same PowerPoint
  process stayed alive. `build()` therefore drops the embedded subset. Without Figtree
  installed, PowerPoint substitutes Calibri. Install Figtree on Windows (Google Fonts, OFL)
  on the render machine and the defence laptop. If a render shows garbled text, check
  `tasklist.exe` for a stale `POWERPNT.EXE` and render again once it has exited.
- **`ffmpeg`:** not on PATH. Use `~/miniforge3/pkgs/ffmpeg-8.0.1-h2a5dc3a_3/bin/ffmpeg` with
  `LD_LIBRARY_PATH=$(ls -d ~/miniforge3/pkgs/*/lib | tr '\n' ':')`; H.264 via `libopenh264`.
- **Validation:** `lxml` is not installed, so the pptx skill's `validate.py` cannot run. The
  PowerPoint render is the validation.
- **No LibreOffice.** PowerPoint is installed on Windows (`POWERPNT.EXE`) and driven over
  COM. A failed open leaves a renamed copy locked, so use a fresh output dir.
- **Backup crops:** to compile the thesis, copy `kth-thesis` to a temp dir and run
  `latexmk -g main_thesis.tex` there (exit 12 is normal). Then run
  `python3 assets/make_backup_crops.py <that main_thesis.pdf>`.

## Author's standing preferences (apply to every slide)
- **Academic register** from `CLAUDE.md`: no figurative language, no colons in headings or
  claim lines, and no contractions. Terms come from `.claude/references/terminology.md`.
- **Headings:** short noun phrases, as in the KTH reference deck
  (nilsjor/kth-doctoral-thesis-presentation). This replaces the earlier sentence-title rule.
  Results slides carry one plain claim line under the evidence.
- **Math:** definitions in the talk (STL syntax and robustness, the FM loss and ODE, the
  guided velocity, the sampler step, the metrics). Propositions and theorems stay in backup,
  stated in plain language with one key formula, unnumbered.
- **Self-contained slides:** no pointer to the thesis document on any slide or in spoken notes.
  Point to backup instead ("(backup)").
- **No generated-looking devices:** no numbered badges, three-card layouts, italic
  micro-labels or pastel box-and-arrow diagrams.
- **Minimal motion:** real videos, the Fig. 3.1 animation, and plain click builds only.
- **Never overclaim:** numbers come from the thesis text and tables, quoted with their scope.
- **Ask before structural changes;** offer options with a recommendation.
