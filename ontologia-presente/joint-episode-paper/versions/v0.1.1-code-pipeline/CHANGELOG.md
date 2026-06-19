# CHANGELOG — The Joint Episode as an Ontological-Temporal Unit

All changes are logged here. Significant content milestones are snapshotted to `versions/` via clean copies (cp -a).

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

### Next
- Tune L3 detector / injection strength / M definition for stronger signal (current AUC near chance indicates room for refinement of synthetic L3 manifestation).
- Run larger N (80+), add sensitivity, add Lorenz generator.
- Integrate stats + figures into manuscript Section 6 + metrics section.
- After next content, produce new compiled PDF + version snapshot.
