# The Joint Episode as an Ontological-Temporal Unit

**Full title:** The Joint Episode as an Ontological-Temporal Unit: Mathematical Characterization, Structural Properties, and Transitions in Complex Systems

> A mathematically precise ontological-temporal unit for complex systems.  
> Joint Episode = maximal interval of sustained low antisynchrony containing critical-mass intensification of local persistence (*kairos*).

This repository contains the complete stable release (v1.0) of the paper together with the full, reproducible Python code that generated every quantitative result reported in Section 6.

## Key Result (honest framing)

Even under **oracle labeling** (perfect knowledge of which episodes are followed by structural perturbations), the best Joint Score achieves only

**AUC ≈ 0.476** (low-dimensional Lorenz, N=4).

The Joint Episode is therefore presented as a **robust detector of L1–L2 coherence** rather than a strong predictor of Layer-3 reorganization. Layer-3 implications are modest and explicitly bounded by the empirical ceiling.

## Stable Release — v1.0-Ready

| Artifact                        | Location |
|---------------------------------|----------|
| **Final PDF**                   | [`Joint-Episode-Paper-v1.0.pdf`](./Joint-Episode-Paper-v1.0.pdf) (14 pp A4) |
| **Full sources + code**         | [`versions/v1.0-Ready/`](./versions/v1.0-Ready/) |
| **Manuscript (LaTeX)**          | `versions/v1.0-Ready/manuscript/` |
| **Reproducible experiments**    | `versions/v1.0-Ready/code/` (includes oracle v0.6 config + results) |

All previous development snapshots are preserved immutably under `versions/`.

## Quick Start — Reproduce Everything

### 1. Rebuild the PDF (biblatex + biber)

```bash
cd versions/v1.0-Ready/manuscript

rm -f *.aux *.bbl *.blg *.log *.out *.run.xml *.bcf

pdflatex -interaction=nonstopmode main.tex
biber main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Result: identical 14-page A4 document, zero Overfull warnings.

### 2. Reproduce the Section 6 experiments (oracle diagnostic)

The critical result (AUC ≈ 0.476) was generated with:

```bash
# From the joint-episode-paper directory
python code/run_experiment.py \
  --config code/config/experiment_config_lorenz_v06_oracle.json \
  --outdir code/results
```

- Fixed seed `20260618`
- 60 realizations (30 high-perm + 30 low-perm)
- Pure oracle labeling mode
- Full output: episode tables + summary JSONs (already present in `code/results/`)

Diagnostic figures can be regenerated with `code/diagnostics/diagnose_l3_signal.py`.

**Dependencies:** `numpy`, `scipy`, `pandas`, `scikit-learn`, `matplotlib` (optional).

## Repository Structure

```
joint-episode-paper/
├── Joint-Episode-Paper-v1.0.pdf          # Stable deliverable
├── README.md
├── CHANGELOG.md
├── .gitignore
├── code/                                 # Complete Python pipeline (reproducible)
│   ├── synthetic_generation/ (lorenz + logistic)
│   ├── labeling/ (incl. oracle mode)
│   ├── metrics/, detection/, evaluation/
│   ├── experiments/ + run_experiment.py
│   ├── config/ (incl. v06 oracle config)
│   └── results/ (exact data behind Section 6)
├── manuscript/                           # Current working LaTeX (sources only)
├── versions/
│   └── v1.0-Ready/                       # Canonical stable snapshot
│       ├── manuscript/ (clean sources + main.pdf)
│       ├── code/ (identical reproducible copy)
│       ├── Joint-Episode-Paper-v1.0.pdf
│       └── README.md
└── ... (older snapshots for full audit trail)
```

## Versioning Policy

- Every significant advance creates a new `versions/vX-Name/` via `cp -a`.
- All editing and the mandatory 4-pass compilation happen **only** inside the new version directory.
- The root `manuscript/` and `code/` are convenience copies of the latest stable.
- This guarantees perfect traceability.

## Citation & Context

This work is part of the **RECD (Registro de Estructura y Coherencia Dinámica) / Systemic Tau** and **Ontología del Presente** research program.

Author: Dr. Johel Padilla Villalba

For the broader project see the parent repository:  
https://github.com/johelpadilla/ontologia-presente

## License

The manuscript text and figures are released under CC-BY 4.0 (or the license stated in the parent project).  
The Python code is released under the MIT License (see code/README.md for details).

---

**Current status:** Stable (v1.0-Ready) — Excellent scientific framing + technical quality + full reproducibility. 

The oracle ceiling (AUC ≈ 0.476) is the central, rigorously obtained empirical result. All numbers and code are provided so that anyone can verify and extend the work.