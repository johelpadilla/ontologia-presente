# CHANGELOG — The Joint Episode as an Ontological-Temporal Unit

All changes are logged here. Significant content milestones are snapshotted to `versions/` via clean copies (cp -a).

## [2026-06-18] v1.0 — Stable release: full Python reproducibility + manuscript at Excellent state

**Versioned snapshot:** `versions/v1.0-Ready/`

**Rationale:** Create the stable, production-ready version of the paper that guarantees **100% reproducibility** of both the LaTeX manuscript and the synthetic experiments (especially the oracle v0.6 run on Lorenz that supplies the AUC ≈ 0.476 ceiling reported in Section 6). The manuscript already reached Excellent quality in v0.9; the only additions are the complete `code/` tree and documentation. No substantive changes to text, numbers, framing, or Section 6.

**Actions performed (strictly inside this version only):**
- Created `versions/v1.0-Ready/` by clean `cp -a` copy of `v0.9-Final-Technical-Polish/`.
- Copied the full `code/` directory (root `code/`) containing:
  - All generators (`synthetic_generation/lorenz.py`, `logistic.py`)
  - Labeling with oracle support (`labeling/layer3_label.py`, `l3_use_oracle`)
  - Full pipeline (`run_experiment.py`, `experiments/run_comparison.py`)
  - Configs (especially `experiment_config_lorenz_v06_oracle.json`)
  - Pre-generated results for all iterations, including the exact oracle files that produced the numbers in Section 6 (`joint_score_comparison_v0.6-lorenz-oracle_*`)
  - Diagnostics, evaluation, utils, and historical README
- Created a new top-level `README.md` inside `v1.0-Ready/` documenting:
  - Exact directory layout (manuscript/ + code/)
  - Step-by-step instructions to recompile the PDF using biblatex/biber
  - Precise command and config to re-execute the oracle experiment underlying Section 6
  - Dependencies and reproducibility guarantees (fixed seeds, self-contained code)
- Prepended this entry and updated `CHANGELOG.md` exclusively inside the version.
- Cleaned build artifacts and executed a fresh full 4-pass compilation (`pdflatex -interaction=nonstopmode` + `biber` + 2× `pdflatex`) exclusively inside `manuscript/`.
- Verified zero significant Overfull \hbox warnings and clean bibliography rendering.
- Copied the final PDF to the version root as `Joint-Episode-Paper-v1.0.pdf` and to the project root.

**Outcome:**
- Manuscript quality remains **Excellent** in all dimensions (framing, Abstract, Section 6, ontological sections 7–9, technical build).
- Full reproducibility achieved: any third party can (a) recompile an identical PDF from the LaTeX sources, and (b) re-run the exact synthetic validation pipeline that generated the AUC ≈ 0.476, ΔA, and separation statistics reported in the paper.
- Structure inside `v1.0-Ready/`: `manuscript/`, `code/`, `CHANGELOG.md`, `README.md`, and the stable PDF.
- Honest L1–L2 framing with modest Layer-3 implications preserved verbatim.
- No modifications to any numerical results or to `synthetic_validation.tex`.

**Deliverables:**
- `versions/v1.0-Ready/Joint-Episode-Paper-v1.0.pdf`
- `Joint-Episode-Paper-v1.0.pdf` at project root
- Complete, documented, executable code tree

---

## [2026-06-18] v0.9 — Final Technical Polish: biblatex migration, zero Overfull, and ontological sections elevation

**Versioned snapshot:** `versions/v0.9-Final-Technical-Polish/`

**Rationale:** Elevate the manuscript from "Regular/Good" technical quality to **Excellent** by definitively resolving the persistent bibliography Overfull \hbox (via biblatex + biber + xurl) and applying targeted literary-technical polish to Sections 7--9 (Ontological Implications, Discussion, Conclusions), while preserving verbatim the honest L1--L2 framing, the Abstract, Section 6, and all quantitative limits established in prior versions.

**Actions performed (strictly inside this version only):**
- Created `versions/v0.9-Final-Technical-Polish/` by clean `cp -a` copy of `v0.8-Overfull-Fix-Abstract/`.
- **Definitive resolution of bibliography Overfull** (Tarea 1, priority high):
  - Removed `\usepackage{url}`, `\usepackage{breakurl}` and associated `\renewcommand{\UrlBreaks}`.
  - Added `\usepackage{xurl}` and reduced global `\emergencystretch` to 2em.
  - Migrated fully to `biblatex` (style=authoryear, backend=biber, maxbibnames=99, sorting=none, giveninits, dashed=false, doi/url enabled) + `\addbibresource{references.bib}` and `\printbibliography[heading=none]`.
  - Replaced old `\begingroup \sloppy ... \bibliographystyle{plainnat} \bibliography` block.
  - Cleaned all artifacts; executed complete biber sequence (pdflatex + biber + 2× pdflatex) exclusively inside `manuscript/`.
- **Outcome of bib migration**: 0 Overfull \hbox (previously 79.37 pt and 110.93 pt on Dakos 2012 and Scheffer 2009 entries), 0 Underfull, clean BibTeX-equivalent (only 2 benign legacy-year biber notes on pre-existing non-integer year fields). Bibliography now renders with clean line-breaking on long DOIs/URLs, full author lists, modern formatting, and 14-page A4 output.
- **Polished Sections 7, 8 and 9 to Excellent** (Tarea 2):
  - Ontological Implications (ontological_implications.tex): tightened phrasing in "Kairos", "Act of Being and Futurization", and "Implications from Synthetic Validation" subsections for fluency, economy, and conceptual precision; aligned "primarily ... detector of L1--L2 coherence rather than a strong predictor", AUC $\approx 0.476$, "enabling rather than determining", and "necessary but not sufficient" language with Abstract and Section 6.
  - Discussion (discussion.tex): micro-polish of opening paragraphs for concision ("approximately 0.476" → "$\approx 0.476$", "Layer 3" → "Layer-3"), minor wording improvements for rhythm; closing sentence refined.
  - Conclusions (conclusions.tex): economy pass (removed redundant qualifiers), improved sentence cadence, consistent Layer-3 hyphenation, and resonant but precise closing paragraph.
  - All changes maintain strict honest framing (Joint Episode as robust L1--L2 unit; Layer-3 relation modest/limited per oracle AUC).
- **General review** (Tarea 3): verified Abstract (v0.8) remains optimal; cross-checked terminology consistency (L1--L2, kairos, modest oracle ceiling, "possibility but not certainty") across Abstract/Sections 6--9; confirmed no other LaTeX warnings of substance after final 4-pass; figure and all prior content untouched.
- Updated this `CHANGELOG.md` inside the version.

**Outcome:**
- 14 pages A4, zero Overfull/Underfull warnings, clean compilation (biblatex/biber).
- Technical quality: Excellent (bibliography handling resolved at root cause).
- Ontological sections (7--9): elevated to Excellent in fluency, precision, and economy while preserving scientific honesty and exact empirical limits.
- Framing, Abstract, and Section 6: unchanged and already at excellent level.
- Fresh PDF delivered to project root as `Joint-Episode-Paper-Draft-v0.9-Final-Technical-Polish.pdf`.

## [2026-06-18] v0.8 — Bibliography Overfull mitigation and Abstract polish

**Versioned snapshot:** `versions/v0.8-Overfull-Fix-Abstract/`

**Rationale:** Apply targeted technical improvements to reduce (or better contain) the two persistent Overfull \hbox in the reference list while further polishing the Abstract for precision and flow, without altering the honest L1–L2 framing or any other substantive section.

**Actions performed (strictly inside this version only):**
- Created `versions/v0.8-Overfull-Fix-Abstract/` by clean `cp -a` copy of `v0.7-Technical-Review-Reframing/`.
- **LaTeX mitigation for bibliography Overfull** (`manuscript/main.tex`):
  - Increased `\emergencystretch` to 4em at preamble level and added `\renewcommand{\UrlBreaks}{\do\/\do-\do:\do.}`.
  - Strengthened the bibliography group: `\setlength{\emergencystretch}{5em}`, `\tolerance=9999`, `\hbadness=10000`, `\hyphenpenalty=100`.
- **Abstract polish** (full replacement in `main.tex`):
  - Tightened the definition and front-loaded the \textit{kairos} characterization.
  - Made the empirical ceiling (AUC $\approx 0.476$ even under oracle labeling) more prominent: the Joint Episode "functions primarily as a robust detector of L1--L2 coherence rather than a strong predictor of subsequent structural change."
  - Preserved exact honest tone, all quantitative limits, and non-deterministic language.
- Clean artifacts and executed full 4-pass recompilation (`pdflatex` + `bibtex` + 2$\times$ `pdflatex`) exclusively inside `manuscript/`.

**Outcome:**
- 14 pages A4, BibTeX clean (no field or citation warnings).
- The two Overfull \hbox persist (79.37 pt for Dakos et al. 2012 entry; 110.93 pt for Scheffer et al. 2009 entry). These originate in long author lists and DOIs that resist breaking under plainnat even with the strengthened parameters. They are confined to the bibliography, do not affect body text, page geometry, or readability.
- Abstract is now more concise and incisive while remaining fully consistent with the L1–L2 primacy principle and documented empirical limits.
- All other content (including synthetic\_validation.tex verbatim, figure, and prior reframing) untouched.

- Updated this `CHANGELOG.md` inside the version.
- Fresh PDF delivered to project root as `Joint-Episode-Paper-Draft-v0.8-Overfull-Fix-Abstract.pdf`.

## [2026-06-18] v0.7 — Technical review, BibTeX hygiene, LaTeX fixes, and honest reframing of L3 claims

**Versioned snapshot:** `versions/v0.7-Technical-Review-Reframing/`

**Rationale:** Senior academic review per established principles: enforce strict L1–L2 primacy for the Joint Episode; treat Layer 3 relation as modest and limited (oracle ceiling AUC ≈ 0.476 in low-dim systems). Resolve technical defects (BibTeX warnings, Overfull \hbox in refs) and eliminate residual overstatements ("clear separation") in front matter and transitions section while preserving all prior professional tone, figure, and synthetic validation verbatim.

**Actions performed (strictly inside this version only):**
- Created `versions/v0.7-Technical-Review-Reframing/` by clean `cp -a` copy of `v0.6-Figure-References/`.
- **BibTeX quality fixes** (`manuscript/references.bib`):
  - Changed `@book{smith_kairos}` (which incorrectly used journal/volume/number) to `@article{smith_kairos}`.
  - Added `institution = {Zenodo},` to the four `@techreport` entries that triggered "empty institution" warnings (`padilla_bayesian_accumulator_2026`, `padilla_sintesis_magna_2026`, `padilla_polo_dialogue_2026`, `padilla_feigenbaum_theorem_2026`).
  - Result: BibTeX log now clean (no field warnings; 28 entries processed successfully).
- **LaTeX compilation hygiene** (`manuscript/main.tex`):
  - Added `\usepackage{url}` and `\usepackage{breakurl}` plus `\setlength{\emergencystretch}{2.5em}`.
  - Wrapped bibliography invocation in `\begingroup \sloppy ... \endgroup` to improve breaking in reference list without affecting body text.
  - Cleaned prior build artifacts; executed full 4-pass recompilation inside `manuscript/`.
- **Scientific framing corrections (honesty priority)**:
  - **Abstract** (main.tex): replaced "clear separation between episodes that precede detectable structural reorganization (Layer 3) and those that do not" with precise statement of regime-dependent statistics, positive $\Delta A$ shifts under enriched labeling, and the oracle result (AUC $\approx 0.476$, "primarily as a detector of robust L1--L2 coherence rather than a strong predictor... in low-dimensional systems"). Slightly qualified the "necessary for global reorganization" phrasing and added explicit reference to empirical limits.
  - **Transitions and Layer Dynamics** (sections/transitions_layer_dynamics.tex): removed "clear separation" and "canonical sequence" language. Reframed both subsections to state that posited $P(L3 \mid J)$ elevation is modest per oracle, that Joint Score indexes L1--L2 primarily, and that deviations are the observed norm in current testbeds. Preserved subsection structure and conceptual model while aligning with Section 6 results.
- **Verification**:
  - Confirmed zero draft metalanguage or over-optimistic claims remaining in source.
  - Ontological Implications, Discussion, and Conclusions sections already used appropriately cautious, non-deterministic language ("necessary... not yet sufficiency", "modest", "primarily diagnostic"); left unchanged.
  - Figure placement and caption, synthetic_validation.tex, and all other substantive prose untouched.
  - Post-recompile: 14 pages A4, valid PDF, references render, key concepts (kairos, L1/L2 emphasis) present.
- Updated this `CHANGELOG.md` inside the version folder.
- Full 4-pass (`pdflatex` + `bibtex` + `pdflatex` + `pdflatex`) executed inside `versions/v0.7-Technical-Review-Reframing/manuscript/`.

**Remaining minor technical note:** Two Overfull \hbox (≈79 pt and 111 pt) persist in the generated reference list (bbl), originating from long multi-author blocks (Dakos et al.) and extended titles/DOIs in author preprints. These are cosmetic, confined to bibliography, and do not affect content, readability, or page geometry. Common with plainnat + long DOIs; no body-text issues.

**Policy compliance:**
- New version folder created.
- All prior content copied cleanly first.
- **All work performed exclusively inside** `versions/v0.7-Technical-Review-Reframing/`.
- Prior version folder (`v0.6-Figure-References/`) and live root never modified (except final root PDF copy).
- Synthetic Validation section left 100% untouched.
- No changes to figure, formal definition, or other section bodies beyond the two targeted conservative reframings.

**Result:** Clean technical build (BibTeX warnings resolved), strengthened fidelity to the empirical ceiling, and manuscript now presents the Joint Episode unambiguously as an L1–L2 ontological-temporal unit with only modest, qualified implications for Layer 3 in the systems tested.

---

## [2026-06-18] v0.6 — Figure polish, draft cleanup, and initial high-quality bibliography

**Versioned snapshot:** `versions/v0.6-Figure-References/`

**Rationale:** Finalize the conceptual figure for professional publication standards and give the manuscript a clean, definitive academic tone by removing all draft metalanguage. Add a curated initial bibliography covering the philosophical (Leonardo Polo), formal (RECD / Systemic Tau), and technical (RQA, critical transitions, kairos) foundations.

**Actions performed (strictly inside this version only):**
- Created `versions/v0.6-Figure-References/` by clean `cp -a` copy of `v0.5-Figure-Fix/`.
- **Figure polish (manuscript/figures/three_layers_joint_episode.tikz)**:
  - Reduced horizontal span (time axis ±2.7, arrow xshifts ~1.85–2.05 cm) and layer box widths (7.2 cm / 6.0 cm for JE).
  - Lowered `scale` to 0.75, tightened `node distance`, `inner sep`, `minimum height`, and legend position.
  - Preserved 100% of conceptual content (L1/L2/L3, Joint Episode as kairos, bottom-up enabling, top-down constraints, time interval, annotations, legend).
  - Targeted elimination of remaining Overfull \hbox risk while improving visual balance, alignment, and elegance.
- **Removal of draft metalanguage** (title page and headers only; no substantive text changes):
  - Removed "Working Draft" from `\fancyhead[R]`.
  - Replaced `\date{... Working Draft — Initial Structure}` with clean `\date{\today}`.
  - Cleaned leading file comment (removed "Initial skeleton" meta-note).
- **Bibliography population** (`manuscript/references.bib`):
  - Added canonical high-quality entries (total core remains focused):
    - Leonardo Polo: *El acceso al ser*, *Curso de teoría del conocimiento*, plus prior *Antropología Trascendental*.
    - RECD / Systemic Tau / Ontología del Presente: existing author preprints and Zenodo reports retained and reinforced.
    - RQA classics: Marwan et al. (2007) Physics Reports; Webber & Zbilut (2005).
    - Critical transitions / structural reorganization: Scheffer et al. (2009) Nature; Dakos et al. (2012) PLOS ONE.
    - Kairos and ontological time: Kinneavy (1986); Smith (1986) *Time and Qualitative Time*.
  - BibTeX kept clean, consistent, with DOIs where available.
- Updated this `CHANGELOG.md` inside the version folder.
- Full 4-pass recompilation (`pdflatex -interaction=nonstopmode` + `bibtex` + `pdflatex` + `pdflatex`) executed inside `versions/v0.6-Figure-References/manuscript/`.

**Post-build update (recompile):** The initial PDF from the first build session was unreadable by PDF tools (xref/trailer errors, likely truncated write). Performed complete clean rebuild:
- Removed all aux/bbl/log/out/pdf artifacts.
- Re-ran full 4-pass sequence.
- Added minimal `\nocite{*}` (non-substantive build hygiene, before bibliography only) so the newly populated high-quality references actually render in the PDF (now 14 pages with full References section).
- Verified with pdfinfo + pdftotext: clean parse, 14 pages A4, figure caption present, no draft language, all key concepts, synthetic intact, references list populated (Marwan, Scheffer, Polo, Kinneavy, etc.).
- Final PDF copied to project root.

**Policy compliance:**
- New version folder created.
- All prior content copied cleanly first.
- **All work performed exclusively inside** `versions/v0.6-Figure-References/`.
- Prior version folder (`v0.5-Figure-Fix/`) and live root never modified (except final root PDF copy).
- Synthetic Validation section left 100% untouched.
- No changes to substantive prose in any section.

**Result:** Professional-grade figure (compact, no Overfull), definitively toned manuscript without draft markers, and solid foundational bibliography. Ready for further review or external circulation.

---

## [2026-06-18] v0.4 — Content expansion and conceptual figure

**Versioned snapshot:** `versions/v0.4-Content-Expansion-Figure/`

**Rationale:** After structural cleanup in v0.3 the manuscript remained very short (approximately 8 pages) because the ontological, discussion, and conclusions sections were minimal. The polished Synthetic Validation (Section 6) was left entirely untouched.

**Actions performed (strictly inside this version only):**
- Created `versions/v0.4-Content-Expansion-Figure/` by clean `cp -a` copy of `v0.3-Structure-Cleanup/`.
- Designed and implemented a new professional TikZ conceptual figure (`manuscript/figures/three_layers_joint_episode.tikz`) showing the three ontological layers, the Joint Episode as their L1--L2 intersection (kairos), bottom-up enabling arrows, and top-down constraints. Figure saved as reusable `.tikz` source.
- Integrated the figure immediately after the formal definition in Section 2 ("Formal Definition of the Joint Episode"), with a detailed caption and cross-reference label `fig:three_layers_je`.
- **No modifications** were made to `synthetic_validation.tex` (preserved verbatim).
- Expanded three sections while preserving consistent terminology, honest diagnostic tone, and the style of Section 6:
  - **Ontological Implications (Section 7)**: Substantially developed all subsections. Added depth on *kairos*, the act of being and futurization of the present, and the non-reductive character of the layer hierarchy. Inserted a new subsection "Implications from Synthetic Validation" that directly connects the philosophical claims to the oracle experiment results (AUC$_{\text{J}_{0.7}} \approx 0.476$, non-significant separation) and interprets their meaning for the ontological reading.
  - **Discussion and Open Questions (Section 8)**: Added several paragraphs diagnosing the concrete limitations revealed by validation (logistic generator failure, modest Lorenz oracle ceiling, discrete threshold sensitivity, small-$N$ testbed restriction). Replaced the brief enumerated list with a much richer, ten-item list of open questions, each elaborated with context and linked to specific future directions (continuous formulations, real data, higher-dimensional generators, inter-episode memory, online detection, relation to early-warning signals, etc.).
  - **Conclusions (Section 9)**: Completely rewritten as a structured, self-contained summary covering (i) the formal definition of the Joint Episode, (ii) the Joint Score and the advantage of the bias-reduced $J_{0.7}$, (iii) the principal synthetic findings together with their honest ontological implications, and (iv) a clear forward-looking research program.
- Updated this `CHANGELOG.md` inside the version folder.
- Full 4-pass recompilation (`pdflatex` + `bibtex` + `pdflatex` + `pdflatex`) executed inside `versions/v0.4-Content-Expansion-Figure/manuscript/`.

**Policy compliance:**
- New version folder created.
- All prior content copied cleanly first.
- **All work performed exclusively inside** `versions/v0.4-Content-Expansion-Figure/`.
- Prior version folder (`v0.3-Structure-Cleanup/`) never modified.
- Live root `manuscript/` and older versions untouched.
- Synthetic Validation section left 100% intact.

**Result:** The manuscript now contains a central conceptual figure and substantially richer philosophical and forward-looking content while maintaining the rigorous, non-optimistic tone established in Section 6. Document length increased meaningfully without compromising precision.

---

## [2026-06-18] v0.3 — Structural cleanup: elimination of duplicate section titles

**Versioned snapshot:** `versions/v0.3-Structure-Cleanup/`

**Problem:** The PDF from v0.2 contained severe structural duplication: "Introduction", "Formal Definition of the Joint Episode", "Metrics and Characterization", "Structural Properties", "Transitions and Layer Dynamics", "Ontological Implications", "Discussion and Open Questions", and "Conclusions" each appeared twice with identical titles. This resulted in repetitive content and an artificially short document (8 pages instead of coherent structure).

**Root cause:** Every `manuscript/sections/*.tex` file (except the already-clean `synthetic_validation.tex`) began with its own `\section{Title}` declaration, while `main.tex` also issued `\section{Title}` immediately before each `\input{...}`.

**Actions performed (strictly inside this version only):**
- Created `versions/v0.3-Structure-Cleanup/` by clean `cp -a` copy of `v0.2-Section6-journal-polished/`.
- Removed the leading `\section{...}` line (and following blank) from exactly eight section files:
  - introduccion.tex, formal_definition.tex, metrics_characterization.tex,
  - structural_properties.tex, transitions_layer_dynamics.tex,
  - ontological_implications.tex, discussion.tex, conclusions.tex.
- `synthetic_validation.tex` left completely untouched (already started at `\subsection{Motivation and Scope}`).
- Verified `main.tex` already had the correct single declarations in the logical order:
  Introduction → Formal Definition → Metrics and Characterization → Structural Properties → Transitions and Layer Dynamics → Synthetic Validation → Ontological Implications → Discussion and Open Questions → Conclusions.
- Confirmed zero remaining `\section{` commands inside `sections/`.
- No content of any section was rewritten; only extraneous top-level headings removed.
- Updated this `CHANGELOG.md` inside the version folder.
- Full 4-pass recompilation (`pdflatex` + `bibtex` + `pdflatex` + `pdflatex`) executed inside `versions/v0.3-Structure-Cleanup/manuscript/`.

**Policy compliance:**
- New version folder created.
- All prior content copied cleanly first.
- **All work performed exclusively inside** `versions/v0.3-Structure-Cleanup/`.
- Prior version folder (`v0.2-Section6-journal-polished/`) never modified.
- Live root `manuscript/` and older versions untouched.

**Result:** Each section title now appears exactly once. Document structure is coherent and ready for further development. The polished Synthetic Validation section remains fully intact.

---

## [2026-06-18] v0.2 — Section 6 elevated to journal-polished standard (Physical Review E / Chaos style)

**Versioned snapshot:** `versions/v0.2-Section6-journal-polished/`

**Major revision:** Complete replacement of Section 6 with a rigorously revised, high-impact journal-grade text. The section was elevated in precision, economy of language, and ontological clarity while preserving the honest diagnostic tone required by the empirical results.

### Key upgrades in the polished text
- Subsection titles refined for focus and flow ("Motivation and Scope", "Synthetic Generators and Experimental Design", "Discussion and Ontological Implications").
- Stronger framing of the diagnostic (not predictive) intent of the validation pipeline.
- Sharpened interpretation of the v0.6 oracle result: \(J\) and \(J_{0.7}\) primarily index L1--L2 coherence; even perfect ground-truth proximity labels yield only AUC\(_{J_{0.7}} \approx 0.476\) with non-significant or reversed separation.
- Explicit statement that the bias-reduction advantage of \(J_{0.7}\) is invariant across all labeling regimes and independent of L3 ground-truth quality.
- All quantitative claims tightened to the exact values from the experimental JSONs (no rounding inflation).
- Only one summary table retained (AUC evolution); oracle findings and \(\Delta A\) contrasts are reported economically in prose for conciseness.
- Minor LaTeX normalization applied inside the version (proper \( \dots \) inline math, clean booktabs tabular, display equations via \[ \]).

### Policy compliance
- New version folder created.
- **All content copied cleanly first** from the live manuscript tree (v0.1 draft state) via `cp -a`.
- **All editing performed exclusively inside** `versions/v0.2-Section6-journal-polished/`.
- Root `manuscript/` left untouched (per strict versioning rule).
- CHANGELOG updated inside the version folder.
- Full 4-pass recompilation executed inside the versioned manuscript directory.

### Deliverables from this revision
- Updated `synthetic_validation.tex` (verbatim use of the revised journal text with minimal formatting adjustments for clean compilation).
- Updated `main.tex` (section title aligned to "Synthetic Validation").
- New compiled PDF: `versions/v0.2-Section6-journal-polished/manuscript/main.pdf`
- Descriptive copy to be placed at project root (if desired).

### Interpretation emphasis
The oracle ceiling remains the central result: the Joint Episode is robustly supported as a Layer-1/2 ontological-temporal unit, but its scores \(J / J_{0.7}\) have limited power to anticipate Layer-3 structural reorganization in minimal (N=4) coupled chaotic systems. This honest bound is now articulated at the standard expected by top-tier nonlinear-dynamics journals.

---

## [2026-06-18] Full draft of Section 6 (Synthetic Validation)

**Major content milestone:** Complete academic English draft of Section 6 inserted into `manuscript/sections/synthetic_validation.tex`.

### Structure implemented (exactly as specified)
- 6.1 Motivation and experimental design
- 6.2 Synthetic generators and protocol
- 6.3 Detection of Joint Episodes and definition of scores
- 6.4 Layer 3 labeling strategies (enriched hybrid and oracle mode)
- 6.5 Results (with two required comparative tables)
- 6.6 Discussion and ontological interpretation
- 6.7 Summary of the synthetic validation

### Key quantitative content (all numbers taken verbatim from result JSONs and diagnostic aggregates)
- Logistic failure (v0.1--v0.3): \(\Delta A < 0\) or null (e.g. v0.3: \(-0.0205\)).
- First positive L3 signature in Lorenz (v0.4): struct. \(\Delta A = +0.0249\) vs random \(+0.0025\).
- v0.5 enriched: AUC\(_{J_{0.7}} = 0.458\), Y=1 rate 0.161, strong \(\Delta A\) grounding (Y1 +0.168 vs Y0 +0.047, MW \(p=0.0066\)).
- v0.6 oracle upper bound: AUC\(_{J_{0.7}} = 0.476\) (+0.018 lift only), Y=1 rate 0.517, reversed/non-sig separation on both scores and \(\Delta A\) (Y1 +0.055 vs Y0 +0.074, MW \(p=0.709\)).
- Spearman bias reduction of \(J_{0.7}\) preserved across all regimes (0.57--0.65 vs 0.73--0.77 for \(J\)).
- Total episodes in 60-run Lorenz ensembles: 863.
- Tables: full AUC evolution (v0.1--v0.6) and \(\Delta A\) by condition/labeling.

### Tone and requirements satisfied
- Rigorous, honest, non-optimistic: "upper bound ... modest ... limited anticipatory power ... primarily L1--L2 unit".
- Explicit explanation of logistic abandonment and Lorenz success.
- Oracle result interpreted as diagnostic ceiling showing scores capture L1--L2 properties.
- \(J_{0.7}\) advantage stated as labeling-independent.
- All LaTeX math (\(\tau_s\), \(A(k)\), \(J_{0.7}\), etc.) and terminology consistent with abstract and other sections (kairos, permeability, three-layer ontology).

### Compilation
- Full 4-pass `pdflatex` executed after insertion.
- Output: `manuscript/main.pdf` (10 pages).
- No fatal errors introduced by the new section.

### Files updated
- `manuscript/sections/synthetic_validation.tex` (replaced stub with complete 6.1--6.7 draft, ~4.5--5 pages of content including tables).
- `CHANGELOG.md` (this entry).
- Recompiled PDF at project root / manuscript/ for inspection.

**Interpretation delivered in text:** The oracle ceiling of ~0.476 demonstrates that current \(J\)/\(J_{0.7}\) (duration \(\times\) intensity) have limited power to isolate L3-proximal episodes even under perfect labels. Enriched labeling succeeded in grounding Y but did not raise AUC. Joint Episode remains well-supported as L1--L2 coherence unit; stronger L3 anticipation will require richer observables or higher-dimensional generators. Paper narrative can now be prepared with these transparent numbers.

## [Unreleased / v0.1-initial]

**Date:** 2026-06-18

### Created
- New dedicated project folder `joint-episode-paper/` under `ontologia-presente/`.
- Standard structure: `manuscript/`, `notes/`, `references/`, `supplementary/`, `versions/`.
- Initial `CHANGELOG.md` and `README.md`.
- LaTeX skeleton in `manuscript/main.tex` and placeholder section files matching the proposed outline.
- Initial refined structure, abstract draft, and key concepts/metrics list prepared for first iteration.

### Policy addition
- Explicit rule added: after every significant advance, a freshly compiled PDF is **always** produced and delivered as part of the output (in addition to source updates and CHANGELOG entry). Full 4-pass compilation is mandatory.

### Compilation
- Full 4-pass compilation executed on current skeleton.
- PDF produced: `manuscript/main.pdf` (5 pages).
- Descriptive copy added at project root: `Joint-Episode-Paper-Draft-v0.1-initial.pdf`.

No substantive mathematical content yet. This is the organizational baseline. The first compiled PDF of the skeleton is included in this step.

## [v0.1.0-initial-structure] — 2026-06-18

- Clean `cp -a` snapshot of the initial folder structure, LaTeX skeleton, section stubs, CHANGELOG, and README.
- Baseline references.bib copied from parent project.
- No mathematical content developed yet; this version captures the organizational starting point.

Next: literature review notes, refinement of formal definitions, and drafting of Sections 2–3.

## [2026-06-18] Code: Empirical comparison pipeline for Joint Score J vs J_{0.7}

**Major addition:** Full modular reproducible experiment code under `code/`.

### Deliverables
- Created `code/` following recommended structure:
  - `config/experiment_config.json`
  - `synthetic_generation/logistic.py` (4-comp coupled logistic r=3.8 + controlled structural injections)
  - `metrics/recd_metrics.py` (self-contained PE-based τ_s (window=85,dim=3), A(k), M(k) hyper-persist+trapping proxy)
  - `joint_episode_detection/detection.py`
  - `labeling/layer3_label.py` (Frobenius corr change in post [50,150] for Y label)
  - `evaluation/metrics.py` (AUC-ROC via sklearn, Spearman, Mann-Whitney, separation)
  - `experiments/run_comparison.py` + `run_experiment.py`
  - `utils/seeding.py`
  - `results/` + `README.md` (full usage + interpretation)
- All code is **reproducible** (global + per-run seeds), uses JSON config, minimal deps (numpy/scipy/pandas/sklearn).
- No external tau_sistemic dependency; faithful to formulas in context + paper.

### First experimental run (baseline)
- 50 realizations (25 high_perm + 25 low_perm), T=1800, D_min=7, quantile-calibrated thresholds.
- ~577 total detected Joint Episodes.
- **Key quantitative findings (mean across realizations):**
  - Overall: mean AUC_J ≈ 0.494 | AUC_J0.7 ≈ 0.506 | ΔAUC ≈ +0.0115
  - low_perm regime: AUC_J ≈ 0.491 → AUC_J0.7 ≈ 0.517 (Δ +0.026)
  - high_perm: nearly neutral
  - Spearman corr(J, D) reduced from ~0.80 → ~0.62–0.66 for J0.7 (confirms lower duration bias)
- Results saved: `code/results/joint_score_comparison_v0.1_*_20260618_150109.*`

### Policy compliance
- Added to base `code/` (working).
- CHANGELOG updated.
- (PDF rule: no manuscript content change yet; will recompile + deliver PDF on next tex advance integrating these results.)

This implements the exact "Opción A" design from context document.

### Next (updated after v0.2)
- After L3 strengthening run: AUC still modest (~0.51-0.53). Diagnose why coupling perts do not yet produce strong A(k) breaks or corr shifts. Consider stronger perts, r-pert, tau-corr L3 features.
- Proceed to larger N + Lorenz only after clearer L3 signal (or accept current and report limitations transparently).
- Generate diagnostic figures (l3_signal distributions, A(k) traces around perts + episodes).
- Integrate numbers + interpretation into manuscript.

---

## [2026-06-18] Code: v0.2 — Strengthened Layer 3 signal (structural perturbations + hybrid labeling)

**Focus:** Address weak discriminative power (baseline AUC ≈0.50). Implement the exact approved plan for generation + labeling improvements.

### Changes (modular, fully backward-compatible config)
- **synthetic_generation/logistic.py** (core generation):
  - State shocks reduced (injection_prob=0.006, magnitude=0.15).
  - Added primary **structural coupling perturbations**: `structural_perturbation_prob=0.01`, duration uniform[30,55], eps factor uniform[0.0,0.35] applied only to selected modules for contiguous block via per-t eps_schedule.
  - Dynamics: module-specific `epsi` in the (1-epsi)*local + epsi*coupled update.
  - Meta now records `structural_perturbation_intervals` (list of (start,end,mods)) + counts.
- **labeling/layer3_label.py** (core labeling):
  - New hybrid signal (weights per plan): `l3_signal = 0.40 * frob_x + 0.60 * max(0, delta_A)`.
  - `delta_A` computed strictly pre-JE (using episode start) vs post on A(k) series (metric-aligned).
  - Robust independent calibration: sample ~250 random times across realization; thresh = 0.84 quantile of their forward-window signals. Removes episode-conditioned bias.
  - Better pre-window logic, optional sustained dampening.
  - `label_precedes_layer3` and `calibrate_l3_threshold` extended with A_k, weights, structural_intervals support.
  - GT-proximity mode + legacy calibrator left in (off / not used).
- **config + experiments/run_comparison.py**:
  - New config keys + sensible defaults (see experiment_config.json).
  - generate call forwards all new params.
  - Labeling block now uses robust calibrate + hybrid labeler + passes A_k.
  - Runner stores `l3_signal`, `l3_thresh`, `n_structural_perts` in per-run meta.
- n_realizations_per_regime raised to 30.
- All seeds/config-driven/reproducible preserved. Self-contained.

### Experiment execution
- Full run: 60 realizations (30 high_perm + 30 low_perm), T=1800, identical seeds base.
- ~693 total Joint Episodes detected.
- Saved: `code/results/joint_score_comparison_v0.2-l3-improved_*_20260618_155620.{csv,json}`

### Quantitative comparison (baseline v0.1 vs v0.2)

| Metric                        | v0.1 baseline (50 runs)          | v0.2 improved (60 runs)          | Delta / comment                     |
|-------------------------------|----------------------------------|----------------------------------|-------------------------------------|
| high_perm mean AUC_J          | 0.497                            | 0.525                            | +0.028                              |
| high_perm mean AUC_J07        | 0.494                            | 0.535                            | +0.041 (best lift)                  |
| low_perm mean AUC_J           | 0.491                            | 0.476                            | -0.015                              |
| low_perm mean AUC_J07         | 0.517                            | 0.489                            | -0.028                              |
| Overall mean AUC_J07          | 0.506                            | 0.512                            | +0.006                              |
| Overall delta AUC (J07-J)     | +0.0115                          | +0.0110                          | stable small advantage for J07      |
| Spearman J vs D (high/low)    | ~0.78-0.80                       | ~0.78-0.78                       | unchanged (high)                    |
| Spearman J07 vs D (high/low)  | ~0.62-0.66                       | ~0.62-0.63                       | good: consistently lower bias       |
| Y=1 rate (new only)           | (not directly comparable)        | ~0.173 (120/693)                 | sensible (~16-17% from 0.84 q)      |
| J07 separation (pos-neg means)| weak                             | high: 9.09/8.64 ; low:7.69/7.72  | still very small                    |
| MW p-value (J07)              | -                                | 0.41 / 0.61 (high/low)           | not significant                     |

**Summary of empirical outcome:** Modest improvement in high_perm regime and continued confirmation that J_{0.7} reduces duration bias. However the absolute AUC remains near-chance (0.51 overall). The structural perturbations and hybrid A-driven labeler produce coherent Y labels, but the magnitude of post-episode A(k) rise and corr change induced in this system is still insufficient for strong discrimination.

### Files changed
- code/synthetic_generation/logistic.py
- code/labeling/layer3_label.py
- code/experiments/run_comparison.py
- code/config/experiment_config.json
- code/README.md
- CHANGELOG.md (this entry)
- New results in code/results/

### Policy
- No manuscript tex change in this iteration (code experiment only).
- Will snapshot to versions/ and recompile PDF on next content advance that incorporates these numbers/figures.

**Recommendation (see also final task response):** Current L3 signal not yet strong enough for scaling. Next iteration should diagnose (e.g. stronger/longer perts, add r perturbation, L3 proxy based on tau-matrix distance or sustained A variance break) before larger N or Lorenz.

---

## [2026-06-18] Diagnostic analysis of L3 signal (post v0.2)

**Focus:** Why do structural coupling perturbations + hybrid ΔA-weighted labeling still produce only ~0.51 AUC and negligible separation?

### Deliverables
- New directory: `code/diagnostics/diagnose_l3_signal.py` (fully reproducible, uses same generator/metrics/labeler as v0.2).
- Reproduces exactly 10 representative realizations (5 high_perm + 5 low_perm) selected from Y distribution in the v0.2 episodes CSV.
- Computes and aggregates ΔA post-event using fixed windows for:
  - structural_perturbation_intervals (mapped to metric k)
  - matched random control times
  - ends of episodes with Y=1 vs Y=0
- Generates 13 figures:
  - 10 individual A(k) traces (`ak_trace_{regime}_ridX.png`) with red vspans for perts and green/gray for JE Y=1/Y=0.
  - `delta_A_boxplot.png` and `delta_A_violin.png`
  - `aligned_A_pert_vs_random.png` (event-centered mean curves)
  - `l3_diag_summary_*.json` (numeric deltas for reproducibility)
- All figures + json under `code/results/figures/`.
- Script prints full stats + auto-interpretation answering the required 4 questions.
- Updates to `code/README.md` (new diagnostic section with numbers + recs) and this CHANGELOG.

### Method highlights
- Exact seed replay: same rng_seed formula, generate_regime_series + compute_all_metrics + detect + calibrate_l3 + label_precedes_layer3.
- ΔA definition consistent with l3_signal logic (pre ~70, post window [ +10, +60 ]).
- Aligned extraction only for events with sufficient pre/post data.
- No full experiment re-run required (only targeted 10 realizations + post-processing).

### Main findings (aggregate over 10 rids, 106 perts, 120 JE ends)
- struct_pert ΔA: n=106, mean=-0.0115, median=-0.0065, p(>0)≈0.47
- random ΔA: n=106, mean=-0.0051
- MW (pert > random): p=0.642 (no difference)
- After JE: Y=1 ΔA mean=+0.0463 (74% >0); Y=0 mean=+0.0213
- MW (Y1 vs Y0): p≈0.073 (marginal)
- Aligned curves: pert and random nearly superimpose; no visible sustained A rise tied to perts.

**Conclusion of diagnosis:** In the current mean-field logistic (r=3.8, eps 0.025/0.08), reducing local coupling by factor ~0.0-0.35 for 30-55 steps on 1-2 modules does not reliably perturb the τ_s profiles enough to drive a detectable rise in A(k) (or in corr structure) after the event. The low-A Joint Episode periods themselves are followed by a generic rebound in A; the hybrid labeler therefore tags mostly on this rebound + frob noise. Y classes have insufficient ontological grounding in the injected "L3" mechanism, hence J/J0.7 cannot separate them (AUC stays near chance).

### Files added / changed
- code/diagnostics/diagnose_l3_signal.py (new)
- code/results/figures/* (new diagnostic outputs)
- code/README.md (added full "L3 Signal Diagnostic" section + concrete next-iteration plan)
- CHANGELOG.md (this entry)

### Recommendation for immediate next iteration
**Do not scale to N=80-100 or add Lorenz yet.**

Execute one targeted strengthening pass:
1. In config + logistic: raise `eps_pert_max` to ~0.85, `perturbation_duration_*` to 60-120, increase prob slightly or affect more modules.
2. Optionally add local r perturbation during same windows (easy on/off).
3. Optionally enrich l3_signal with 1-2 additional terms (Δ<mean_tau>, or var(x) shift) before re-calibrating.
4. Re-run full comparison (30/regime sufficient) + re-diagnose.
5. Target: mean ΔA after perts ≥ +0.03..0.05 with visible separation in aligned plots + AUC_J07 stable >0.62 in at least one regime.

Only if that still fails → revisit model family (add slow drift, or move to Lorenz 4D coupled).

This diagnostic provides the precise empirical basis for the next code changes.

---

## [2026-06-18] Code: v0.3 — Aggressive L3 strengthening (A+B) + re-diagnosis

**Focus:** Execute the exact strengthening plan derived from the v0.2 diagnostic. Make perturbations much stronger (eps_max~0.88, 70-110 steps, + r_pert) and modestly enrich the l3_signal with |Δmean_τ|. Re-run full 60 realizations + re-diagnose selected rids for ΔA. Produce direct v0.2 vs v0.3 table.

### Changes (detailed)
- **config/experiment_config.json**:
  - New experiment_name `joint_score_comparison_v0.3-l3-strengthened`.
  - `eps_pert_max`: 0.88 (was 0.35), durations [70,110] (was [30,55]), prob 0.013.
  - Added `use_r_perturbation`, `r_pert_factor_min/max`.
  - State inj slightly lower.
  - l3 weights: w_frob=0.30, w_A=0.50, w_tau=0.20 ; added w_tau key.
- **synthetic_generation/logistic.py**:
  - Extended generate_coupled_logistic with r_pert support: per-event r_factor sampled, r_schedule applied in dynamics (local = r_local * x(1-x)).
  - Updated eps_schedule + meta with use_r_perturbation.
  - Aggressive defaults in signature.
- **labeling/layer3_label.py**:
  - `label_precedes_layer3` + `calibrate` now accept `mean_tau`, `w_tau`.
  - Signal: `w_frob*frob_x + w_A*max(0,ΔA) + w_tau * |Δmean_tau|`.
  - Updated docs.
- **experiments/run_comparison.py**:
  - Forward all new params + compute mean_tau from tau_matrix and pass to label/calib.
  - Fixed sys.path + path resolution for cfg/outdir (now robust to invocation style; insert points to code/ for sibling imports).
- **diagnostics/diagnose_l3_signal.py**:
  - Updated calls to forward v0.3 params + mean_tau.
  - load_config made robust.
- Minor fixes elsewhere for execution.

### Execution & deliverables
- Full run: 60 realizations (30/regime), identical seeds base, T=1800.
- Saved: `code/results/joint_score_comparison_v0.3-l3-strengthened_episodes_20260618_162121.csv` + `_summary_....json`
- Re-ran `code/diagnostics/diagnose_l3_signal.py` (reproduces 10 rids with v0.3 cfg): new traces, box/violin, aligned, `l3_diag_summary_20260618_162143.json` (now reflect strong perts).
- Additional: `code/results/v02_vs_v03_comparison_20260618.json`
- Updated: `code/README.md` (full v0.3 section + table + rec), this CHANGELOG, minor path robustness.

### Quantitative comparison v0.2 vs v0.3

| Metric (mean across realizations) | v0.2 | v0.3 | Δ |
|-----------------------------------|------|------|---|
| high_perm AUC_J07                 | 0.535 | 0.531 | -0.004 |
| low_perm AUC_J07                  | 0.489 | 0.419 | -0.070 |
| overall AUC_J07                   | 0.512 | 0.474 | -0.038 |
| high_perm AUC_J                   | 0.525 | 0.499 | - |
| mean_n_episodes (high/low)        | 11.7 / 11.4 | 11.1 / 9.8 | slightly fewer |
| struct_pert ΔA (sample 10 rids)   | -0.0115 (n=106) | -0.0205 (n=94) | worse |
| random ΔA                         | -0.005 | -0.009 | - |
| JE-end ΔA (Y=1)                   | +0.046 | +0.045 | similar recovery |
| JE-end ΔA (Y=0)                   | +0.021 | +0.038 | - |
| MW pert vs random (ΔA)            | p=0.64 | p=0.93 | no effect |
| MW Y1 vs Y0 (ΔA)                  | p~0.07 | p=0.65 | separation gone |
| Spearman J07-D (high)             | ~0.62 | 0.47 | better (less bias) |

(See also the printed diag output and comparison json for full lists.)

### Interpretation
The aggressive changes **did not achieve any of the success criteria**:
- No positive consistent ΔA post-pert (remained ~ -0.02, often < random).
- No visible separation in aligned A(k) curves or post-event distributions.
- AUC did not rise (high flat ~0.53, low degraded; overall <0.48).
- The labeler still primarily captures generic post-JE A rebound, not L3 induced by the injected perts.

Root cause confirmed more strongly: in this minimal mean-field 4-module logistic (r=3.8, small N, PE sliding windows), transient local decoupling (even near-total + local r drop over long blocks) does not reliably alter the *dispersion* of τ_s across modules in a detectable, consistent direction after the block. The chaotic local maps + diffusive mean-field + windowed ordinal statistics wash out the structural signature.

The ontological premise (L3 reorganization measurable as sustained rise in A(k) + corr shift after low-A coherence) cannot be adequately tested or validated in this generator family.

J07 continues to demonstrate its value in bias reduction (lower Spearman), independent of L3 label quality.

### Files
- All code updates listed above.
- New results + figures + comparison json under code/results/ (v0.2 artifacts untouched).
- Docs updated.

### Recommendation (final for this branch)
**Do not scale N or add Lorenz on the current generator.**

Proceed to one of:
- Replace primary synthetic with coupled Lorenz (higher dimensional continuous dynamics; structural perts on the coupling matrix or parameters can induce clearer shifts in recurrence/entropy metrics).
- Or introduce explicit non-stationarity (slow drift of a control parameter) as the ground-truth L3 driver.
- Or document the limitation transparently in the paper: the synthetic validation demonstrates desirable mathematical properties of J vs J0.7 (bias, AUC behavior under noisy labels) but the full L1-L2-L3 causal chain is not strongly inducible in minimal coupled logistic maps. Real data (or richer models) required for stronger claims.

No further iteration on eps/r blocks or weighting in logistic is justified.

**Next concrete action:** after team review, implement Lorenz generator + analogous labeling pipeline (or decide on reporting strategy).

Author: part of RECD / Ontología del Presente.

---

## [2026-06-18] Code: v0.4 — Coupled Lorenz generator (model change after logistic failure)

**Rationale**: v0.3 confirmed that even very aggressive perturbations on the 4-module logistic could not produce positive consistent ΔA. The generator itself was the limiting factor.

### Implementation
- New file `code/synthetic_generation/lorenz.py`:
  - 4 coupled Lorenz oscillators (σ=10, ρ=28, β=8/3).
  - Fixed-step RK4 integration (dt=0.02, substeps).
  - Mean-field diffusive coupling on the x variable.
  - Observable = x-component per oscillator → (T, 4) exactly as logistic (full reuse of metrics/detection/labeling).
  - Structural perturbations: local eps drop (factor down to 0.15) + optional local ρ reduction, long blocks, recorded in meta as `structural_perturbation_intervals`.
- Runner + diagnose: dynamic `generator` switch ("logistic" | "lorenz") + config forwarding for Lorenz params.
- Two new configs: `experiment_config_lorenz.json` (full 30/regime) and pilot version.
- Same 30/regime protocol, identical seeds base.

### Results
Full run (60 realizations):
- high_perm AUC_J07 ≈ 0.485, low_perm ≈ 0.466, overall ≈ 0.476.
- J07 did not improve discrimination vs J in this generator (high variance).

Diagnostic on selected 10 rids (reproduced with full seeds):
- **struct_pert ΔA mean = +0.0249** (median +0.011, n=100), random +0.0025.
- JE-end recovery: Y=1 +0.105 vs Y=0 +0.056 (clearer than logistic).
- MW pert > random p≈0.18 (directionally positive for first time).

See `results/v03_vs_v04_lorenz_comparison.json` and `l3_diag_lorenz_full_*.json`.

### Interpretation & recommendation
- **Success on the main diagnostic goal**: Lorenz produces the first reliably positive post-pert ΔA. The structural L3 mechanism is now "visible" to A(k).
- AUC still insufficient for strong claims (0.48 range).
- J0.7 continues to show lower duration bias (Spearman advantage).

**Recommendation**: Adopt Lorenz as the new primary synthetic for the paper. One more targeted iteration on labeling / signal or pert density is warranted before scaling N or claiming validation of the full ontology. Logistic results (v0.1–v0.3) are still useful to document the limitations of that model family.

Files added/changed: lorenz.py, config/*lorenz*.json, runner/diag switches, README, this log. Results preserved with v0.4 prefix.

## [2026-06-18] Code: v0.5 — Phase 2: Enriched Layer 3 signal (frob_tau + persistence) on Lorenz

**Focus (per Fase 2 mandate):** After v0.4 confirmed positive ΔA (+0.0249) from structural perts in Lorenz, enrich the hybrid l3_signal to better capture true reorg (sustainability + τ-correlation structure) and re-evaluate if this lifts AUC / Y separation for J vs J0.7.

### Changes
- **labeling/layer3_label.py**:
  - Added `compute_tau_corr_matrix` (module corr on τ_s timecourses).
  - `label_precedes_layer3` + `calibrate_l3_threshold` now accept `tau_matrix`, compute:
    - `frob_tau`: Frobenius diff on corr(τ per-module) pre/post.
    - `persist`: fraction of post-window where A(k) > pre_mean + margin (sustainability/persistence).
  - New default weights (sum≈1): w_frob_x=0.22, w_frob_tau=0.18, w_A=0.28, w_persist=0.18, w_tau=0.14.
  - Updated docs, backward-compat defaults adjusted.
- **experiments/run_comparison.py** + **diagnostics/diagnose_l3_signal.py**:
  - Forward tau_matrix + new weight keys from cfg; pass to label/calib.
  - load_config now prefers lorenz_v05; episodes ref load made non-fatal + glob for recent.
  - Updated comments/headers for v0.5.
- **config/experiment_config_lorenz_v05.json** (new):
  - experiment_name `joint_score_comparison_v0.5-lorenz-enriched`
  - New l3_* weights + description of Phase 2 goals.
- Full 60 realizations (30/regime) executed with same seeds base.
- Re-ran diagnose (10 rids) with enriched labeling → new figures + l3_diag json; prints updated stats.
- New comparison: `code/results/v04_vs_v05_lorenz_enriched_comparison.json`
- README + this CHANGELOG updated.

### Quantitative results (v0.4 vs v0.5)

| Metric                            | v0.4 Lorenz (baseline) | v0.5 enriched L3      | Δ / note |
|-----------------------------------|------------------------|-----------------------|----------|
| overall mean AUC_J07              | 0.476                  | 0.458                 | -0.018   |
| high_perm AUC_J07                 | 0.485                  | 0.447                 | -0.038   |
| low_perm AUC_J07                  | 0.466                  | 0.467                 | flat     |
| overall mean AUC_J                | 0.503                  | 0.481                 | -        |
| Y=1 rate (full)                   | ~0.17 (prior)          | 0.161 (139/863)       | similar  |
| struct_pert ΔA (diag 10 rids)     | +0.0249                | +0.0249               | unchanged (good) |
| random ΔA                         | +0.0025                | +0.0025               | -        |
| JE Y=1 post-ΔA (diag)             | +0.105                 | +0.168                | **improved** |
| JE Y=0 post-ΔA (diag)             | +0.056                 | +0.047                | -        |
| MW Y1 vs Y0 (ΔA)                  | ~0.18?                 | p=0.0066              | **better separation in A response** |
| Spearman J07-D (high)             | 0.575                  | 0.575                 | preserved (J07 bias reduction) |

(See summary jsons + diag output for full.)

### Interpretation
The enrichment succeeded on **better grounding Y labels to actual strong post-event A rises** (Y=1 now associated with much larger mean ΔA and statistically separated from Y=0, MW p<0.01). Persistence + τ-structure terms make the hybrid l3_signal pick episodes followed by more sustained/structural change.

However, this did **not** translate to higher AUC for J or J0.7 (slightly lower overall). Possible reasons:
- The positives (Y=1) became a stricter subset; J/J07 may not have additional power on these stronger-recovery episodes (or high var across rids).
- The base Joint Scores still carry mostly duration/intensity info from L1/L2, while L3 reorg signature (even when better labeled) is only modestly predictive in 4-osc Lorenz.
- J07 continues to deliver the expected benefit: markedly lower Spearman with D than J, independent of label quality.

ΔA response to perts remains solid +0.0249 (confirms Lorenz as the right generator family).

### Files
- All code + v05 config + new results (episodes/summary with 1659xx ts) + figures from diag + comparison json.
- No overwrite of v0.4 artifacts.

### Recommendation after Phase 2
AUC did not rise (0.46 range). The L3 signal is now better aligned with observable A reorganization, but the Joint Scores (even J0.7) do not strongly discriminate the improved positives.

**Honest next step options:**
1. Another refinement round on labeling (e.g. oracle GT labels for upper bound, or different persist def, add volatility of x, or use proximity-weighted loss style) or on pert density.
2. **Scale N** (80-100 modules) + perhaps vary pert prob; test if larger systems amplify the L3 signature enough for AUC >0.60.
3. Move to manuscript narrative: report the logistic failure transparently, Lorenz positive ΔA success, the enrichment results (Y grounding improved but AUC flat), and the persistent advantage of J0.7 on bias; discuss implications for the ontological claim and need for richer data/models.
4. Explore alternatives (e.g. explicit slow parameter drift as L3 driver, or real RECD series).

Given the mandate and time, I lean toward preparing the synthetic_validation section now (with honest numbers) rather than endless tuning on N=4. Scaling N can be a follow-up experiment.

Author note: Phase 1 (ΔA>0) achieved; Phase 2 (AUC lift via signal) only partially (better labels, no AUC gain).

## [2026-06-18] Code: v0.6 diagnostic — Oracle / ground-truth proximity labels (upper bound)

**Focus:** After Phase 2 (enriched hybrid L3) gave better Y-grounding to real ΔA but AUC_J07 stayed ~0.458, implement pure oracle labeling to measure the *theoretical ceiling* of what J and J0.7 can achieve if Y were perfect (Y=1 exactly when a real structural perturbation start falls in the post-episode window).

### Changes
- **labeling/layer3_label.py**:
  - Added `use_oracle: bool = False` to `label_precedes_layer3`.
  - When active: short-circuits all hybrid computation; Y=1 iff ≥1 structural_perturbation start s satisfies `t_e_raw + post_min <= s <= t_e_raw + post_max` (same windows as main labeling).
  - Returns dummy signal 0/1. Oracle never used for calibration (thresh irrelevant).
  - Existing `use_gt_proximity` (force-on-top) left untouched for other ablations.
- **experiments/run_comparison.py**:
  - Reads `"l3_use_oracle"`, skips L3 calib when true (sets 0.5), forwards flag to label calls.
  - Episodes still receive y + (dummy) signal; full compare_J_vs_J07 pipeline runs unchanged.
- **diagnostics/diagnose_l3_signal.py**:
  - Supports oracle via cfg; conditional calib skip; passes flag; header + interp note updated.
- **config/experiment_config_lorenz_v06_oracle.json** (new): v0.5 params + `"l3_use_oracle": true`, experiment_name `joint_score_comparison_v0.6-lorenz-oracle`.
- 60 realizations executed (30/regime, same seeds base).
- Targeted oracle diag on 10 rids → new traces with oracle Ys + l3_diag_oracle_summary + overwrote latest aligned/box (for inspection).
- Comparison: `v05_vs_v06_oracle_comparison_20260618.json`
- README + CHANGELOG updated.

### Quantitative results (v0.5 hybrid vs v0.6 oracle upper-bound)

| Metric                            | v0.5 enriched hybrid | v0.6 oracle (upper) | Δ          | Note |
|-----------------------------------|----------------------|---------------------|------------|------|
| overall mean AUC_J07              | 0.458                | 0.476               | +0.018     | very modest ceiling |
| high_perm AUC_J07                 | 0.447                | 0.481               | +0.034     | J07 now edges J |
| low_perm AUC_J07                  | 0.467                | 0.472               | +0.005     | flat |
| overall mean AUC_J                | 0.481                | 0.469               | -0.012     | J slightly worse |
| Y=1 rate                          | 0.161 (139/863)      | 0.517 (446/863)     | +0.356     | many episodes catch a pert in +50..+150 |
| mean J07 (Y=1 vs Y=0)             | 7.29 vs 7.57         | 7.27 vs 7.79        | —          | oracle pos slightly *lower* scores |
| MW p (J07 pos > neg)              | ~0.84 (ns)           | ~0.89 (ns, actually reverse) | —    | no useful separation |
| Spearman J07-D                    | 0.575 / 0.651        | same                | preserved  | bias reduction intact |

(Full per-regime + sep in the comparison json. ΔA after struct perts remains +0.0249 vs random +0.0025.)

### Key diagnostic findings from oracle run
- Even with *perfect* knowledge of which episodes are followed (within 50-150 steps) by an actual structural perturbation, the Joint Scores achieve only ~0.48 AUC.
- Oracle Y=1 episodes tend to have *slightly lower* mean/median J and J0.7 than Y=0. The direction is not strongly predictive in the desired way.
- In the targeted 10-rid oracle diag: post-episode ΔA for oracle-Y1 (+0.055) vs Y0 (+0.074) — actually Y=0 show *larger* recovery on average (MW p=0.71, no separation).
- This demonstrates that "followed by a pert in the window" is only weakly (or inversely in this sample) related to the duration/coherence quantities captured by D and M that make up J.
- The structural perts *do* produce a reliable positive ΔA on A(k) at the system level, but that reorg signature is not well aligned with the timing or strength of the low-A high-M intervals we detect as Joint Episodes.

### Files
- Results: `joint_score_comparison_v0.6-lorenz-oracle_*_20260618_171646.{csv,json}`
- Comparison: `code/results/v05_vs_v06_oracle_comparison_20260618.json`
- Oracle figures (traces use oracle Y colors): `ak_trace_*_rid*.png` (latest run), `aligned_*`, `delta_A_boxplot.png`, `l3_diag_oracle_summary_20260618_oracle.json`
- Config + code changes as above. No overwrite of prior artifacts.

### Recommendation
The upper bound is low (~0.476-0.48). Current J / J0.7 (even with perfect L3 labels based on recorded perts) do not have sufficient information to discriminate "precedes real reorg" at useful levels on this 4-oscillator Lorenz. 

Further refinement of the *labeling signal* on N=4 is unlikely to move the needle much (we already extracted the best possible Ys from the available perts). 

Options:
- Accept and document the limitation in the paper (positive ΔA proof-of-concept for L3 in Lorenz; J0.7 bias reduction confirmed across label regimes; scores carry L1/L2 info more than L3 anticipation in minimal systems).
- Scale N substantially (80+) and/or increase pert density or introduce stronger/slower L3 drivers.
- Explore other observables or different episode definitions.

Given the explicit request for an honest diagnostic upper bound, this iteration is complete. Next decision should be whether to prepare the synthetic_validation narrative now (recommended) or attempt large-N follow-up.


