"""
experiments/run_comparison.py
Main experiment runner for J vs J_0.7 comparison on coupled (logistic or Lorenz) synthetic data.

Supports:
- Enriched hybrid L3 labeling (v0.5)
- Pure oracle / ground-truth proximity labeling for upper-bound diagnostics (v0.6+): set "l3_use_oracle": true in config.

Usage (from project root or code/):
  python -m code.experiments.run_comparison
  or
  python code/experiments/run_comparison.py --config code/config/experiment_config.json
"""

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
import pandas as pd

# local imports (run as module or adjust path)
import sys
from pathlib import Path
# Insert the code/ directory so sibling packages (utils, synthetic_generation, ...) are importable as top-level
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.seeding import set_global_seed, get_rng
from metrics.recd_metrics import compute_all_metrics
from joint_episode_detection.detection import detect_joint_episodes, calibrate_thresholds as calibrate_je
from labeling.layer3_label import label_precedes_layer3, calibrate_l3_threshold
from evaluation.metrics import compare_J_vs_J07

# Generator is chosen dynamically from config (logistic or lorenz)
def _get_generate_fn(generator: str):
    if generator == "lorenz":
        from synthetic_generation.lorenz import generate_regime_series as gen
        return gen
    else:
        from synthetic_generation.logistic import generate_regime_series as gen
        return gen


def load_config(path: str) -> Dict:
    with open(path, "r") as f:
        return json.load(f)


def save_results(results: Dict, out_dir: Path, prefix: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    # episode table
    if "episode_table" in results and len(results["episode_table"]) > 0:
        df = pd.DataFrame(results["episode_table"])
        df.to_csv(out_dir / f"{prefix}_episodes_{ts}.csv", index=False)
    # summary
    with open(out_dir / f"{prefix}_summary_{ts}.json", "w") as f:
        json.dump(results["summary"], f, indent=2, default=float)
    print(f"Saved results to {out_dir} with prefix {prefix}_{ts}")


def run_single_realization(
    cfg: Dict,
    regime: str,
    realization_id: int,
    base_seed: int,
) -> Dict[str, Any]:
    """Run one full synthetic + metrics + detection + labeling pipeline."""
    rng_seed = base_seed + realization_id * (1 if regime == "high_perm" else 1000)
    set_global_seed(rng_seed)

    generator = cfg.get("generator", "logistic")
    generate_regime_series = _get_generate_fn(generator)

    # 1. Generate
    if generator == "lorenz":
        x, meta = generate_regime_series(
            regime=regime,
            T=cfg["T"],
            n_modules=cfg["n_modules"],
            eps_high=cfg.get("eps_high_perm", 0.18),
            eps_low=cfg.get("eps_low_perm", 0.04),
            noise=cfg["noise_level"],
            seed=rng_seed,
            dt=cfg.get("lorenz_dt", 0.02),
            substeps=cfg.get("lorenz_substeps", 10),
            sigma=cfg.get("lorenz_sigma", 10.0),
            rho=cfg.get("lorenz_rho", 28.0),
            beta=cfg.get("lorenz_beta", 8.0/3.0),
            injection_prob=cfg.get("state_injection_prob", 0.002),
            injection_magnitude=cfg.get("state_injection_magnitude", 0.3),
            use_injections=cfg.get("use_structural_injections", False),
            structural_perturbation_prob=cfg.get("structural_perturbation_prob", 0.012),
            perturbation_duration_min=cfg.get("perturbation_duration_min", 60),
            perturbation_duration_max=cfg.get("perturbation_duration_max", 100),
            eps_pert_min=cfg.get("eps_pert_min", 0.0),
            eps_pert_max=cfg.get("eps_pert_max", 0.15),
            use_structural_perturbations=cfg.get("use_structural_perturbations", True),
            use_rho_perturbation=cfg.get("use_rho_perturbation", True),
            rho_pert_factor_min=cfg.get("rho_pert_factor_min", 0.70),
            rho_pert_factor_max=cfg.get("rho_pert_factor_max", 0.92),
        )
    else:
        x, meta = generate_regime_series(
            regime=regime,
            T=cfg["T"],
            n_modules=cfg["n_modules"],
            r=cfg["r"],
            eps_high=cfg["eps_high_perm"],
            eps_low=cfg["eps_low_perm"],
            noise=cfg["noise_level"],
            seed=rng_seed,
            injection_prob=cfg.get("state_injection_prob", cfg.get("injection_probability", 0.004)),
            injection_magnitude=cfg.get("state_injection_magnitude", cfg.get("injection_magnitude", 0.12)),
            use_injections=cfg.get("use_structural_injections", True),
            structural_perturbation_prob=cfg.get("structural_perturbation_prob", 0.013),
            perturbation_duration_min=cfg.get("perturbation_duration_min", 70),
            perturbation_duration_max=cfg.get("perturbation_duration_max", 110),
            eps_pert_min=cfg.get("eps_pert_min", 0.0),
            eps_pert_max=cfg.get("eps_pert_max", 0.88),
            use_structural_perturbations=cfg.get("use_structural_perturbations", True),
            use_r_perturbation=cfg.get("use_r_perturbation", True),
            r_pert_factor_min=cfg.get("r_pert_factor_min", 0.88),
            r_pert_factor_max=cfg.get("r_pert_factor_max", 0.95),
        )

    # 2. Metrics
    metrics = compute_all_metrics(
        x,
        tau_window=cfg["tau_window"],
        pe_dim=cfg["pe_dim"],
        recent_window=cfg["recent_window_for_delta"],
        baseline_window=cfg["baseline_window_for_A"],
    )
    A_k = metrics["A_k"]
    M = metrics["M"]
    tau_matrix = metrics["tau_matrix"]
    n_k = len(A_k)
    metric_offset = cfg["tau_window"] - 1  # rough lag

    # 3. Calibrate thresholds per realization (regime dependent)
    theta_A, theta_M = calibrate_je(
        A_k, M, D_min=cfg["D_min"],
        theta_A_quantile=cfg["theta_A_quantile"],
        theta_M_quantile=cfg["theta_M_quantile"],
    )

    # 4. Detect episodes
    episodes = detect_joint_episodes(A_k, M, theta_A=theta_A, D_min=cfg["D_min"], theta_M=theta_M)

    # 5. Label (v0.5 enriched hybrid or v0.6 oracle diagnostic)
    w_frob = cfg.get("l3_hybrid_w_frob", 0.22)
    w_frob_tau = cfg.get("l3_hybrid_w_frob_tau", 0.18)
    w_A = cfg.get("l3_hybrid_w_A", 0.28)
    w_persist = cfg.get("l3_hybrid_w_persist", 0.18)
    w_tau = cfg.get("l3_hybrid_w_tau", 0.14)
    l3_quantile = cfg.get("l3_calibration_quantile", 0.84)
    n_calib = cfg.get("l3_n_calibration_samples", 250)
    use_sust = cfg.get("l3_use_sustained", False)
    use_gt = cfg.get("l3_use_ground_truth_proximity", False)
    use_oracle = cfg.get("l3_use_oracle", False)

    # Compute mean_tau + full tau_matrix (N, n_k) for delta + frob_tau + persist
    mean_tau = None
    tau_matrix = None
    if "tau_matrix" in metrics:
        tau_matrix = metrics["tau_matrix"]
        mean_tau = np.mean(tau_matrix, axis=0)

    # Robust calibration using random candidates (independent of episodes)
    # Skip for pure oracle mode (Y decided by GT proximity alone; thresh irrelevant)
    if use_oracle:
        l3_thresh = 0.5
    else:
        l3_thresh = calibrate_l3_threshold(
            x, metric_offset, A_k=A_k,
            mean_tau=mean_tau,
            tau_matrix=tau_matrix,
            n_samples=n_calib,
            post_min=cfg["post_l3_window_min"],
            post_max=cfg["post_l3_window_max"],
            w_frob=w_frob, w_frob_tau=w_frob_tau, w_A=w_A, w_persist=w_persist, w_tau=w_tau,
            quantile=l3_quantile,
            seed=rng_seed + 17,
        )

    y_list = []
    sig_list = []
    struct_intervals = meta.get("structural_perturbation_intervals", [])
    for ep in episodes:
        y, sig = label_precedes_layer3(
            ep, x, metric_offset, A_k=A_k,
            mean_tau=mean_tau,
            tau_matrix=tau_matrix,
            post_min=cfg["post_l3_window_min"],
            post_max=cfg["post_l3_window_max"],
            w_frob=w_frob, w_frob_tau=w_frob_tau, w_A=w_A, w_persist=w_persist, w_tau=w_tau,
            l3_thresh=l3_thresh,
            use_sustained=use_sust,
            structural_intervals=struct_intervals,
            use_gt_proximity=use_gt,
            use_oracle=use_oracle,
        )
        y_list.append(int(y))
        sig_list.append(sig)

    # attach labels and signal
    for i, ep in enumerate(episodes):
        ep["y"] = y_list[i]
        ep["l3_signal"] = sig_list[i]
        ep["l3_thresh"] = float(l3_thresh)

    # 6. Evaluation per realization
    comp = compare_J_vs_J07(episodes, y_list)

    out = {
        "realization_id": realization_id,
        "regime": regime,
        "seed": rng_seed,
        "n_episodes": len(episodes),
        "theta_A": theta_A,
        "theta_M": theta_M,
        "l3_thresh": float(l3_thresh),
        "comparison": comp,
        "episodes": episodes,
        "meta": {
            "n_injections": int(len(meta.get("injection_times", []))),
            "n_structural_perts": int(meta.get("n_structural_perts", 0)),
            "eps": meta.get("eps"),
            "use_structural_perturbations": meta.get("use_structural_perturbations", False),
        }
    }
    return out


def aggregate_results(all_runs: List[Dict]) -> Dict:
    """Aggregate across realizations."""
    summary = {
        "n_total_realizations": len(all_runs),
        "by_regime": {},
    }

    for regime in ["high_perm", "low_perm"]:
        runs = [r for r in all_runs if r["regime"] == regime]
        if not runs:
            continue
        aucs_J = [r["comparison"]["J"]["auc"] for r in runs if not np.isnan(r["comparison"]["J"]["auc"])]
        aucs_J07 = [r["comparison"]["J_07"]["auc"] for r in runs if not np.isnan(r["comparison"]["J_07"]["auc"])]
        sp_J = [r["comparison"]["J"]["spearman_D"] for r in runs]
        sp_J07 = [r["comparison"]["J_07"]["spearman_D"] for r in runs]

        n_ep = [r["n_episodes"] for r in runs]

        summary["by_regime"][regime] = {
            "n_realizations": len(runs),
            "mean_n_episodes": float(np.mean(n_ep)),
            "mean_auc_J": float(np.nanmean(aucs_J)),
            "mean_auc_J07": float(np.nanmean(aucs_J07)),
            "std_auc_J": float(np.nanstd(aucs_J)),
            "std_auc_J07": float(np.nanstd(aucs_J07)),
            "mean_spearman_J": float(np.nanmean(sp_J)),
            "mean_spearman_J07": float(np.nanmean(sp_J07)),
            "delta_auc_mean": float(np.nanmean([r["comparison"]["delta_auc"] for r in runs if not np.isnan(r["comparison"]["delta_auc"])])),
        }

    # overall
    all_comp = [r["comparison"] for r in all_runs]
    summary["overall_mean_auc_J"] = float(np.nanmean([c["J"]["auc"] for c in all_comp]))
    summary["overall_mean_auc_J07"] = float(np.nanmean([c["J_07"]["auc"] for c in all_comp]))
    summary["overall_delta_auc"] = float(np.nanmean([c["delta_auc"] for c in all_comp]))

    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config/experiment_config.json",
                        help="Path to JSON config relative to code/ or absolute")
    parser.add_argument("--outdir", type=str, default="results",
                        help="Directory for results (relative to code/ or abs)")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]  # joint-episode-paper/
    code_dir = project_root / "code"
    # Support invocation both as --config code/config/... (from project root) and config/... (from code/)
    cfg_arg = Path(args.config)
    if not cfg_arg.is_absolute():
        if len(cfg_arg.parts) > 0 and cfg_arg.parts[0] == "code":
            cfg_path = project_root / cfg_arg
        else:
            cfg_path = code_dir / cfg_arg
    else:
        cfg_path = cfg_arg
    cfg = load_config(str(cfg_path))

    out_arg = Path(args.outdir)
    if not out_arg.is_absolute():
        if len(out_arg.parts) > 0 and out_arg.parts[0] == "code":
            out_dir = project_root / out_arg
        else:
            out_dir = code_dir / out_arg
    else:
        out_dir = out_arg

    print("=" * 70)
    print("JOINT EPISODE - J vs J0.7 COMPARISON EXPERIMENT")
    print(f"Config: {cfg_path}")
    print(f"Realizations per regime: {cfg['n_realizations_per_regime']}")
    print(f"T={cfg['T']}, D_min={cfg['D_min']}")
    print("=" * 70)

    set_global_seed(cfg["seed"])
    base_seed = cfg["random_state_base"]

    all_runs: List[Dict] = []
    episode_table_rows: List[Dict] = []

    start_time = time.time()

    for regime in ["high_perm", "low_perm"]:
        print(f"\n=== Regime: {regime} ===")
        for rid in range(cfg["n_realizations_per_regime"]):
            res = run_single_realization(cfg, regime, rid, base_seed)
            all_runs.append(res)

            # flatten some for table
            for ep in res["episodes"]:
                row = {
                    "regime": regime,
                    "rid": rid,
                    "D": ep["D"],
                    "mean_M": ep["mean_M"],
                    "J": ep["J"],
                    "J_07": ep["J_07"],
                    "y": ep.get("y", 0),
                    "theta_A": res["theta_A"],
                    "theta_M": res["theta_M"],
                }
                episode_table_rows.append(row)

            if (rid + 1) % 5 == 0 or rid == cfg["n_realizations_per_regime"] - 1:
                print(f"  completed {rid+1}/{cfg['n_realizations_per_regime']} | episodes last={res['n_episodes']}")

    summary = aggregate_results(all_runs)

    results = {
        "config": cfg,
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "episode_table": episode_table_rows,
        "n_total_episodes": len(episode_table_rows),
    }

    # Save
    if cfg.get("save_summary", True) or cfg.get("save_episode_table", True):
        save_results(results, out_dir, cfg["experiment_name"])

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print(json.dumps(summary, indent=2))
    print(f"\nElapsed: {elapsed:.1f}s")
    print("=" * 70)

    return results


if __name__ == "__main__":
    main()
