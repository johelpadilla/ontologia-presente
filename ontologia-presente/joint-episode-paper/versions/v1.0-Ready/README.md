# Joint Episode Paper — v1.0-Ready (Stable Release)

**Full title:** The Joint Episode as an Ontological-Temporal Unit: Mathematical Characterization, Structural Properties, and Transitions in Complex Systems

This is the **stable, fully reproducible** snapshot of the paper. It contains the final LaTeX manuscript (Excellent technical and scientific quality) together with the complete Python codebase that generated all quantitative results reported in Section 6 (Synthetic Validation), particularly the oracle diagnostic run (v0.6) on the Lorenz attractor that established the AUC ≈ 0.476 ceiling.

## Core Scientific Framing (unchanged, honest)

The Joint Episode is defined and validated primarily as a robust **L1–L2 coherence / kairos unit** (local τ_s intensification + sustained low antisynchrony window). 

In low-dimensional Lorenz (N=4 oscillators), even with perfect oracle labeling of episodes followed by structural perturbations (Layer 3), the bias-reduced score J_{0.7} reaches only AUC ≈ 0.476 — statistically near chance and directionally non-predictive in the tested regime. The manuscript therefore presents the Joint Episode as a detector of strong L1–L2 relational conditions that raise the *possibility, but not the certainty*, of Layer-3 reorganization. Layer-3 implications remain modest, system-dependent, and explicitly bounded by the empirical ceiling.

All numbers, Section 6 text, Abstract, and ontological sections (7–9) are preserved exactly as in v0.9.

## Version Structure

```
v1.0-Ready/
├── manuscript/
│   ├── main.tex                 # Final sources (biblatex + biber)
│   ├── references.bib
│   ├── sections/                # All 9 sections (synthetic_validation.tex untouched)
│   ├── figures/
│   └── main.pdf                 # Fresh build after 4-pass
├── code/                        # Complete reproducible experiment pipeline
│   ├── config/
│   │   ├── experiment_config_lorenz_v06_oracle.json   # Exact config for Sec 6 oracle
│   │   └── ... (prior v0.4–v0.5 configs)
│   ├── synthetic_generation/    # lorenz.py (RK4, 4 coupled) + logistic.py
│   ├── metrics/recd_metrics.py  # τ_s (PE), A(k), M(k)
│   ├── joint_episode_detection/
│   ├── labeling/layer3_label.py # Enriched hybrid + pure oracle mode (use_oracle)
│   ├── experiments/run_comparison.py
│   ├── run_experiment.py        # Convenience launcher
│   ├── diagnostics/diagnose_l3_signal.py
│   ├── results/                 # Pre-generated: *v0.6-lorenz-oracle* + all prior runs
│   ├── evaluation/
│   ├── utils/
│   └── README.md                # Detailed historical run notes
├── CHANGELOG.md
├── README.md                    # This file
└── Joint-Episode-Paper-v1.0.pdf # Stable deliverable PDF (14 pp A4)
```

## Reproducing the Manuscript (PDF)

All compilation must be performed inside the versioned manuscript directory.

```bash
cd /path/to/joint-episode-paper/versions/v1.0-Ready/manuscript

# Clean previous artifacts
rm -f *.aux *.bbl *.blg *.log *.out *.toc *.run.xml *.bcf

# Full 4-pass with biblatex/biber (mandatory)
pdflatex -interaction=nonstopmode main.tex
biber main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

The resulting `main.pdf` is the authoritative build. Copy it to the version root or project root as `Joint-Episode-Paper-v1.0.pdf`.

Expected: 14 pages A4, zero Overfull \hbox (bibliography or body), clean biber run (minor legacy year notes only, non-impacting).

## Reproducing the Experiments (Section 6 — Oracle v0.6 on Lorenz)

The key quantitative result (AUC_{J_{0.7}} ≈ 0.476 under oracle labeling) was produced by the following exact invocation:

```bash
# From the joint-episode-paper/ directory (or v1.0-Ready/)
python code/run_experiment.py \
    --config code/config/experiment_config_lorenz_v06_oracle.json \
    --outdir code/results
```

- Uses fixed global seed `20260618` + per-realization offsets (60 realizations total: 30 high_perm + 30 low_perm).
- Generator: 4 coupled Lorenz oscillators (σ=10, ρ=28, β=8/3), RK4 dt=0.02.
- Structural perturbations recorded; oracle mode sets Y=1 exactly when a perturbation start falls in the post-episode window [50,150] steps.
- Outputs timestamped CSVs/JSONs with per-episode J, J_{0.7}, y labels, and aggregate AUC / ΔA / Spearman / Mann-Whitney statistics.
- Pre-generated oracle results live in `code/results/joint_score_comparison_v0.6-lorenz-oracle_*_20260618_171646.{csv,json}` (and comparison JSON).

To reproduce diagnostics / figures from any run (e.g., A(k) traces, ΔA distributions):

```bash
python code/diagnostics/diagnose_l3_signal.py \
    --config code/config/experiment_config_lorenz_v06_oracle.json
```

All intermediate experiment versions (v0.1–v0.5) are preserved with their configs and results for full audit trail.

## Dependencies

- Python 3.9+
- numpy, scipy, pandas, scikit-learn
- matplotlib (only for diagnostics/figures)
- No external RECD / Tau Sistémico package required — fully self-contained implementation faithful to the paper formulas.

Install example:

```bash
pip install numpy scipy pandas scikit-learn matplotlib
```

## Running from Different Locations

The runner inserts `code/` into sys.path, so the following all work:

- `python code/run_experiment.py --config code/config/...`
- `cd code; python run_experiment.py --config config/...`
- `python -m code.experiments.run_comparison --config ...` (with adjustments)

See also `code/README.md` for deeper historical iteration notes.

## Verification of Reproducibility

After re-running the oracle config you should recover (within floating-point tolerance):

- Overall mean AUC_{J_{0.7}} ≈ 0.476
- Y=1 rate ≈ 0.517
- Preserved Spearman advantage of J_{0.7} vs. raw J (lower duration bias)
- Positive mean post-perturbation ΔA on A(k) (≈ +0.0249 in Lorenz diagnostics)
- No strong separation of J/J_{0.7} between oracle-Y=1 and Y=0 (confirms modest predictive power)

These match the numbers integrated verbatim into Section 6.

## Policy & Integrity Notes

- This version was created by clean `cp -a` of `v0.9-Final-Technical-Polish/`.
- The `code/` tree was copied in full from the root `code/` that produced the reported results.
- **No substantive changes** were made to manuscript text, numerical results, or Section 6.
- All work (README, CHANGELOG, final recompile) performed exclusively inside `versions/v1.0-Ready/`.
- Framing remains strictly honest: Joint Episode as L1–L2 detector; Layer-3 relation is a possibility bounded by the oracle ceiling.

## Deliverables

- `manuscript/main.tex` + all sections/figures (final state)
- Complete `code/` pipeline (reproducible)
- `Joint-Episode-Paper-v1.0.pdf` (root + version)
- Updated `CHANGELOG.md` and this `README.md`

For the full project history see the parent `CHANGELOG.md` and prior `versions/*/CHANGELOG.md`.

---

**Stable release date:** 2026-06-18  
**Status:** Excellent (manuscript) + 100% reproducible (code + data for Sec 6)  
Author: Dr. Johel Padilla Villalba — Ontología del Presente (Tau Sistémico) Research Program
