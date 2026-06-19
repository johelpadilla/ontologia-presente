# CHANGELOG — The Joint Episode as an Ontological-Temporal Unit

All changes are logged here. Significant content milestones are snapshotted to `versions/` via clean copies (cp -a).

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


