# Joint Episode Paper — Empirical Comparison Code

Modular, reproducible implementation of the synthetic experiment comparing:

- Original Joint Score: \( J = D \times \overline{M} \)
- Proposed: \( J_{0.7} = D^{0.7} \times \overline{M} \)

Goal: Determine which has superior discriminative power for Joint Episodes that precede detectable Layer 3 (structural reorganization) in controlled synthetic systems.

## Structure

```
code/
├── config/
│   └── experiment_config.json     # All key parameters (seed, T, thresholds, windows, etc.)
├── synthetic_generation/
│   └── logistic.py                # 4-component coupled logistic + controlled injections
├── metrics/
│   └── recd_metrics.py            # τ_s (PE-based), A(k), M(k) — self-contained
├── joint_episode_detection/
│   └── detection.py               # Maximal interval detection + calibration
├── labeling/
│   └── layer3_label.py            # Post-episode Frobenius corr change → binary label Y
├── evaluation/
│   └── metrics.py                 # AUC-ROC, Spearman, Mann-Whitney, group stats
├── experiments/
│   └── run_comparison.py          # Full pipeline runner (multi-realization)
├── utils/
│   └── seeding.py                 # Reproducibility helpers
├── results/                       # Auto-created CSVs + JSON summaries
├── run_experiment.py              # Convenience entry point
└── README.md
```

## Key Parameters (see config)

- Coupled logistic r=3.8, 4 modules
- Regimes: high_perm (eps≈0.08), low_perm (eps≈0.025)
- τ window=85, PE dim=3
- D_min=7
- Post-episode L3 window: 50–150 steps
- Thresholds: quantile-based per realization (regime calibrated)
- Reproducible via global seed + per-run seeds

## Running the Experiment

```bash
# From joint-episode-paper/
python code/run_experiment.py

# With custom config
python code/run_experiment.py --config code/config/experiment_config.json --outdir results
```

Outputs:
- Per-run episode-level table: `<name>_episodes_YYYYMMDD_HHMMSS.csv`
- Aggregated summary JSON with mean AUCs, deltas, correlations by regime + overall

## Reproducibility

- Fixed top-level seed in config
- Each realization uses deterministic offset seed
- All RNG via numpy.random.Generator or global after set_global_seed

## First Results (baseline run)

See the latest `results/*_summary_*.json` after execution. Typical columns of interest:
- `mean_auc_J` vs `mean_auc_J07`
- `delta_auc_mean`
- `mean_spearman_*` (lower absolute value better for reduced D-bias)

## L3 Signal Improvements (v0.2 run — 2026-06-18)

Major iteration focused exclusively on strengthening Layer 3 generation + labeling per approved plan.

### Changes implemented
- **synthetic_generation/logistic.py**:
  - State shocks down-weighted (prob 0.006, mag 0.15).
  - Added **primary structural coupling perturbations**: with `structural_perturbation_prob`, duration sampled [30,55], `eps_pert` factor [0.0, 0.35] applied locally to 1-2 modules for a block of steps (effective local eps = nominal * factor). This directly modifies interaction structure.
  - Meta now includes `structural_perturbation_intervals` and `n_structural_perts`.
- **labeling/layer3_label.py**:
  - Hybrid `l3_signal = 0.40*frob_x + 0.60*max(0, delta_A)` (delta_A from A(k) pre-strictly-before-JE vs post).
  - Robust calibration: ~250 random candidate times sampled across the series (independent of detected episodes); thresh = 0.84 quantile of signals.
  - Pre-windows placed using episode start to avoid overlap with low-A region.
  - `label_precedes_layer3` now accepts `A_k`, weights, `structural_intervals`.
  - Legacy episode-centered calibrator kept (commented use); GT-proximity mode available (off by default).
- Config + runner: new JSON keys, forward params, use new calibrator, store `l3_signal` on episodes.
- Reproducible, 30 realizations/regime.

### Results comparison (baseline v0.1 50 runs vs v0.2 60 runs)
See table in CHANGELOG and the two summary JSONs in `results/`.

Key observations:
- Modest AUC lift especially in high_perm (J07 ~0.49 → 0.535).
- J07 continues to show substantially lower Spearman corr with D (reduced duration bias).
- Y=1 rate ~0.17 (sensible from quantile calibration).
- Separation (pos vs neg means on J07) remains small; MW tests not yet significant.
- Overall AUC still ~0.51 (target >0.60 not reached).

### Interpretation
Structural perturbations fire and the hybrid labeler produces more ontologically coherent Y (tied to rise in A after coherence window). However, in this mean-field 4-module logistic the "structural" effect on subsequent A(k) and correlations is still too weak/noisy to yield strong discriminative power for the Joint Scores. 

## Dependencies

numpy, scipy, pandas, scikit-learn, matplotlib (for diagnostics).

Full list of imports used across modules: the above + json, pathlib, datetime, typing.

No external RECD package required — fully self-contained for this study.

## Relation to Paper

This code directly supports Section 6 (Synthetic Validation) and the mathematical characterization of the Joint Score (Section 3). Results will be used to select/justify \( J_{0.7} \) (or retain J) and to report quantitative separation.

## L3 Signal Diagnostic (post-v0.2, 2026-06-18)

**Goal:** Understand why coupling perturbations + hybrid labeling still yielded AUC ≈ 0.51 and weak pos/neg separation.

### Method
- Selected 10 representative realizations (5 high_perm + 5 low_perm) with mix of Y=0/1 counts.
- Reproduced exactly using same seeds/config (generate + metrics + detect + label).
- For each: extracted full A(k), structural_perturbation_intervals, episodes with attached Y.
- Computed ΔA = mean(A post [t+10,t+60]) − mean(pre) for:
  - Actual structural perts (mapped to metric k)
  - Matched number of random control times
  - Ends of Joint Episodes with Y=1 and Y=0
- Generated:
  - 10 individual A(k) traces with pert spans (red) and JE intervals (green=Y1 / gray=Y0).
  - Summary boxplot + violin of ΔA by category.
  - Aligned average A(k) curves (event-centered) for perts vs random.

Results + figures: `code/results/figures/` (ak_trace_*.png, delta_A_boxplot.png, delta_A_violin.png, aligned_A_pert_vs_random.png, l3_diag_summary_*.json)

### Key quantitative findings
- Structural perts (n=106 across sample): mean ΔA = −0.0115 (median −0.0065), p(ΔA>0)≈0.47. No reliable upward shift.
- Matched random: mean ΔA = −0.0051. Difference non-significant (MW p=0.64).
- After JE ends: natural recovery (ΔA >0) — Y=1 episodes: mean +0.0463 (74% positive); Y=0: +0.0213. Separation weak (MW p≈0.073).
- Aligned means confirm: no clear sustained A jump after perts; random and pert curves nearly overlap.

### Interpretation
The structural perturbations (local eps reduction factor 0–0.35 for 30–55 steps on 1–2 modules) do not produce consistent, detectable increases in A(k) (antisynchronization of τ_s) in this 4-module mean-field logistic (r=3.8). 

The hybrid labeler ends up mostly capturing the natural rebound of A after any low-A period (plus noise from frob_x), rather than a perturbation-driven reorganization. Because perts and the JE low-A windows are temporally independent, Y labels are only weakly tied to the injected "Layer 3" events. Result: classes remain hard to separate with J or J_{0.7}.

Traces show A(k) is noisy with frequent short excursions; low-A episodes are visible but post-episode rise is generic, not specific to "preceded by pert".

### Concrete recommendations for next iteration (before scaling)
1. **Strengthen perturbations significantly** (primary):
   - Increase `eps_pert_max` to 0.7–0.95 (near-zero or zero coupling on affected modules).
   - Longer blocks: [60, 110] or [80,150].
   - Affect 2–3 modules simultaneously more often.
   - Optional: also apply brief local r-perturbation (e.g. r_local = r * 0.92) on same modules/times for stronger signature.
2. **Enrich l3_signal**:
   - Add term(s) for change in mean τ level, or Frobenius on the tau_matrix itself, or post variance of x.
   - Or use a "sustained rise" fraction more aggressively.
3. Consider adding a controlled "oracle" label mode (Y=1 if structural interval overlaps post-window) purely for upper-bound diagnostics.
4. Only after A/B try: increase N to 80–100 and/or introduce Lorenz generator.

Do not scale yet. The current logistic + pert strength is insufficient to test the ontological claim rigorously.

See full printed report + figures from `code/diagnostics/diagnose_l3_signal.py`.

## Next Steps (see also main paper roadmap)

After diagnostic:
- Iterate once more on pert strength + l3_signal enrichment using same logistic (target: clear mean ΔA >0.03–0.05 after perts, AUC lift to 0.62+).
- Only then: scale N + add Lorenz.
- Sensitivity sweeps on new params.
- Export key figures to manuscript/figures/ and integrate numbers into synthetic_validation.tex.
- Version snapshot + PDF.

---

## v0.3 — Aggressive strengthening (A+B) executed 2026-06-18 (post-diagnostic)

### Changes implemented
- **synthetic_generation/logistic.py**:
  - `eps_pert_max` 0.35 → **0.88** (local coupling near zero on affected modules).
  - `perturbation_duration` 30-55 → **70-110**.
  - `structural_perturbation_prob` ~0.013; still 1-2 modules per event.
  - Added **local r perturbation** (`use_r_perturbation=True`, factor [0.88,0.95]) applied to same modules/blocks → stronger local dynamics shift.
  - State injections kept minimal (prob 0.004, mag 0.12).
- **labeling/layer3_label.py**:
  - Enriched signal: `0.30*frob_x + 0.50*relu(ΔA) + 0.20*|Δmean_τ|` (delta_mean_tau on system avg τ_s).
  - Weights updated; calibration robust unchanged.
- Config + runner + diagnose: new keys forwarded, path fixes for direct execution, full repro.
- 30 realizations/regime executed with new params → `joint_score_comparison_v0.3-l3-strengthened_*_20260618_162121.{csv,json}`

### Comparative results (v0.2 vs v0.3)

| Metric                        | v0.2 (baseline after hybrid) | v0.3 (aggressive perts + Δτ) | Comment |
|-------------------------------|------------------------------|------------------------------|---------|
| high_perm mean AUC_J07        | 0.535                        | 0.531                        | flat    |
| low_perm mean AUC_J07         | 0.489                        | 0.419                        | worse   |
| overall mean AUC_J07          | 0.512                        | 0.474                        | no lift |
| mean ΔA after struct_pert     | -0.0115                      | -0.0205                      | still negative, p>0~0.37 |
| mean ΔA random control        | -0.005                       | -0.009                       | similar |
| mean ΔA after JE (Y=1 / Y=0)  | +0.046 / +0.021              | +0.045 / +0.038              | recovery generic; separation collapsed |
| Spearman J07 vs D (high)      | ~0.62                        | 0.47                         | improved (less bias) |
| n_struct perts (sample 10 rids) | ~106                         | 94                           | comparable |

Full comparison + raw deltas: `code/results/v02_vs_v03_comparison_20260618.json`

Figures (now reflecting v0.3 perts): `code/results/figures/` (ak_trace_*, delta_A_*, aligned_* , new l3_diag json)

### Key interpretation
- Despite very aggressive decoupling (eps_local ~0.1 * nominal for 70-110 steps + r drop), **post-pert ΔA remains near zero or negative**, statistically indistinguishable from random times.
- The hybrid labeler (even enriched) continues to tag primarily on the **natural A(k) rebound** that follows *any* low-A Joint Episode, not on perturbation-induced reorganization. Y=1 and Y=0 have nearly identical post-episode ΔA distributions.
- In this 4-module mean-field logistic (r=3.8), local coupling/r drops do not translate into reliable, consistent increases in cross-module τ_s dispersion (A(k)) after the event. Chaotic mixing + sliding PE windows (85) likely wash out the signature.
- J07 still shows lower duration bias (good), but the underlying Y labels lack sufficient "true positive" grounding for the L3 claim → AUC stuck <0.53.

### Recommendation (explicit)
**Do NOT scale to N=80-100 + Lorenz yet.**

This iteration definitively shows that further tweaks on this exact synthetic generator are unlikely to produce the required L3 signal strength (positive consistent ΔA, Y separation that AUC can exploit).

Promising directions for next phase (choose one):
1. **Model change**: move primary synthetic generator to coupled Lorenz (4D or 8D) with analogous structural perturbations on coupling parameters (more continuous state space, richer τ_s response possible).
2. Or introduce explicit slow parameter drift / non-stationary regime switches as the "L3" driver (instead of transient blocks).
3. Accept limitation and report in paper: "in minimal coupled logistic the structural L3 effect on A(k) is too weak for reliable pre/post labeling; results demonstrate the metric properties (J0.7 bias reduction) but cannot strongly validate the full L1-L2-L3 ontology in this family."

Re-run diagnostics or sensitivity on current code only for completeness/ablation; do not invest more cycles chasing AUC on this generator.

See also root CHANGELOG.md for full entry. 

Author: part of the RECD / Ontología del Presente program.

---

## v0.4 — Coupled Lorenz (model change) — 2026-06-18

**Generator**: new `synthetic_generation/lorenz.py` (4 oscillators, RK4, mean-field coupling on x, return x-component as observable for full pipeline compatibility).

**Structural perts**: eps_pert_max=0.15 (strong local decoupling) + optional local rho reduction [0.70-0.92], durations 60-100.

**Results (60 realizations)**:
- First time we obtain **positive mean ΔA after structural perts**: +0.0249 (n=100 events on 10 rids) vs random +0.0025.
- Post-JE recovery separation improved: Y=1 +0.105 vs Y=0 +0.056.
- AUC still low: overall J07 ~0.476 (high 0.485, low 0.466). J07 did not outperform J on discrimination in this run.

**Comparison summary** (see `results/v03_vs_v04_lorenz_comparison.json`):

| Version          | overall AUC_J07 | mean ΔA (struct pert) |
|------------------|-----------------|-----------------------|
| v0.2 logistic    | 0.512           | -0.0115               |
| v0.3 strong log. | 0.474           | -0.0205               |
| **v0.4 Lorenz**  | 0.476           | **+0.0249**           |

**Interpretation**: The switch to Lorenz fixed the core diagnostic failure (no positive ΔA). The L3 mechanism is now observable. However the current labeling + scores do not yet turn that signal into high AUC.

**Next recommendation**: Keep Lorenz. Enrich the l3_signal further or tighten the labeling criteria, or run with higher pert density. Do not go back to logistic for the main validation.

Full results: `joint_score_comparison_v0.4-lorenz_*_20260618_163547.*` + updated figures.

## v0.5 — Phase 2: Enriched L3 signal (frob_tau + persistence) — 2026-06-18

**Generator**: Lorenz (unchanged from v0.4). Focus: improve *label quality* (not pert strength).

**L3 signal changes** (`labeling/layer3_label.py`):
- `frob_x` + `|Δmean_τ|` + relu(ΔA) retained.
- **New**: `frob_tau` = Frobenius on correlation matrix of per-module τ_s trajectories (pre vs post).
- **New**: `persist` = fraction of post-window steps where A(k) remains elevated above pre baseline (sustainability).
- Weights rebalanced (0.22/0.18/0.28/0.18/0.14). Robust calib unchanged.
- Full forward in runner + diagnostics.

**Run**: 60 realizations (30/regime), prefix `v0.5-lorenz-enriched`, using dedicated `experiment_config_lorenz_v05.json`.

**Key results** (see `results/v04_vs_v05_lorenz_enriched_comparison.json` + summary):

| Metric                  | v0.4 Lorenz | v0.5 enriched |
|-------------------------|-------------|---------------|
| overall AUC_J07         | 0.476       | 0.458         |
| high AUC_J07            | 0.485       | 0.447         |
| low AUC_J07             | 0.466       | 0.467         |
| Y=1 rate                | ~0.17       | 0.161         |
| struct_pert ΔA (diag)   | +0.0249     | +0.0249 (stable) |
| Y=1 post ΔA (diag 10r)  | +0.105      | **+0.168**    |
| Y=0 post ΔA             | +0.056      | +0.047        |
| MW Y1≠Y0 on ΔA          | weak        | **p=0.0066**  |

**Interpretation**:
- Enrichment **worked for grounding**: Y=1 now tags episodes followed by clearly stronger and more sustained A recovery (visible in aligned/box, MW significant).
- **Did not lift AUC**: slightly lower. The stricter Y=1 set may be harder for current J/J0.7 to separate, or the L3 effect size in N=4 Lorenz is still modest relative to episode variability.
- J0.7 Spearman-with-D advantage **fully preserved** (independent of L3 quality).

**Recommendation (end of Phase 2)**:
Positive ΔA achieved and now better-labeled. AUC not >0.55. Honest path: document transparently in paper (logistic limits, Lorenz ΔA success + label enrichment result), preserve J0.7 for its bias-reduction property, and consider (a) scaling N or (b) write-up without claiming strong predictive validation yet. Another micro-iteration on signal possible but diminishing returns likely on N=4.

Updated: `layer3_label.py`, configs, run/diag, README, CHANGELOG, new results + comparison json + fresh figures from diag run.

## v0.6 diagnostic micro-iteration — Oracle GT labels (upper bound) — 2026-06-18

**Purpose (post-Phase 2):** Quantify the theoretical max AUC of J / J0.7 under *perfect* L3 labels derived directly from the ground-truth structural perturbation times (Y=1 only when a pert start falls in the exact post-window used by labeling).

**Implementation**:
- New flag `use_oracle` in `label_precedes_layer3` (early return, bypasses hybrid entirely).
- Runner skips calib and uses oracle Ys when enabled.
- Same post_min/post_max (50/150) for comparability.
- Dedicated config `experiment_config_lorenz_v06_oracle.json`.
- Diag updated to support oracle Ys in traces/stats.
- 60 realizations run, prefix `v0.6-lorenz-oracle`.

**Results vs v0.5** (see `results/v05_vs_v06_oracle_comparison_20260618.json`):

| Metric               | v0.5 hybrid | v0.6 oracle (upper) | Comment |
|----------------------|-------------|---------------------|---------|
| overall AUC_J07      | 0.458       | 0.476               | +0.018 (small) |
| high J07 AUC         | 0.447       | 0.481               | J07 > J here |
| Y=1 rate             | 0.161       | 0.517               | ~half episodes "catch" a pert post |
| mean J07 (Y1 / Y0)   | 7.29 / 7.57 | 7.27 / 7.79         | oracle Y1 actually lower on avg |
| MW (J07 Y1>Y0)       | ns          | ns (reverse dir)    | no discriminative power |
| Spearman J07-D       | preserved   | preserved           | J0.7 advantage independent of labels |

**Oracle diag observation (10 rids)**: Even oracle Y=1 episodes show *no better* post-ΔA than Y=0 (+0.055 vs +0.074, p=0.71).

**Honest conclusion**: The upper bound on current scores + this generator/pert design is ~0.48 AUC. J and J0.7 (built from D and M) carry little information about "will be followed closely by a recorded structural reorg". This is a strong diagnostic signal for the paper.

Recommendation: prepare narrative / synthetic section now rather than more N=4 tuning. Scaling or richer L3 drivers are separate future experiments.

