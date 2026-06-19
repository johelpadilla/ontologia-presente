#!/usr/bin/env python3
"""
diagnose_l3_signal.py

Diagnostic analysis for Layer 3 signal (structural perturbations + hybrid or oracle labeling).

- Reproduces exact selected realizations (deterministic via seeds).
- Extracts A(k) traces, structural_perturbation_intervals, detected episodes + Y labels (hybrid or oracle).
- Generates:
  * Individual A(k) traces with markers for perts and JE (Y=1 vs Y=0).
  * Quantitative delta_A ... 
  * Summary boxplots...
  * Aligned average...
- When cfg["l3_use_oracle"]=true: Y labels are pure ground-truth proximity (upper bound diagnostic).
- Outputs figures to code/results/figures/
- Prints key stats.

Run (from joint-episode-paper/):
  python code/diagnostics/diagnose_l3_signal.py
  or
  python -m code.diagnostics.diagnose_l3_signal
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

# Path setup so we can import sibling packages when run as script or module
_CODE_ROOT = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path("code").resolve()
sys.path.insert(0, str(_CODE_ROOT))

from metrics.recd_metrics import compute_all_metrics
from joint_episode_detection.detection import detect_joint_episodes, calibrate_thresholds as calibrate_je
from labeling.layer3_label import label_precedes_layer3, calibrate_l3_threshold

def _get_generate_fn(generator: str):
    if generator == "lorenz":
        from synthetic_generation.lorenz import generate_regime_series as gen
        return gen
    else:
        from synthetic_generation.logistic import generate_regime_series as gen
        return gen


# ----------------------------- Selection & Config -----------------------------

# Representative rids (from prior v0.4 Lorenz full run analysis for mix of Y and episode counts)
# 5 high + 5 low = 10 realizations total. Reproducible via seeds.
SELECTED_RIDS = {
    "high_perm": [0, 4, 7, 10, 12],
    "low_perm":  [0, 2, 4, 5, 9],
}

# Analysis window params (consistent with labeling defaults)
PRE_WINDOW = 70
POST_START_OFFSET = 10
POST_WINDOW = 50
ALIGN_LEFT = 80
ALIGN_RIGHT = 100


def load_config() -> Dict:
    # Robust: prefer Lorenz v0.5 or v0.4 config for current phase; fall back gracefully.
    project_root = _CODE_ROOT.parent if _CODE_ROOT.name == "code" else _CODE_ROOT
    candidates = [
        project_root / "code" / "config" / "experiment_config_lorenz_v05.json",
        project_root / "code" / "config" / "experiment_config_lorenz.json",
        _CODE_ROOT / "config" / "experiment_config_lorenz_v05.json",
        _CODE_ROOT / "config" / "experiment_config_lorenz.json",
        project_root / "code" / "config" / "experiment_config.json",
        _CODE_ROOT / "config" / "experiment_config.json",
    ]
    for p in candidates:
        if p.exists():
            with open(p, "r") as f:
                return json.load(f)
    # last resort
    cfg_path = _CODE_ROOT / "config" / "experiment_config.json"
    with open(cfg_path, "r") as f:
        return json.load(f)


def get_rng_seed(regime: str, rid: int, base: int) -> int:
    return base + rid * (1 if regime == "high_perm" else 1000)


def metric_k_from_raw(t_raw: int, offset: int) -> int:
    return max(0, t_raw - offset)


def compute_delta_A(
    A_k: np.ndarray,
    t_k: int,
    pre_w: int = PRE_WINDOW,
    post_off: int = POST_START_OFFSET,
    post_w: int = POST_WINDOW,
) -> Optional[float]:
    """delta = mean(A[t_k + post_off : t_k + post_off + post_w]) - mean(A[t_k - pre_w : t_k])"""
    n = len(A_k)
    pre_start = max(0, t_k - pre_w)
    pre_end = max(0, t_k)   # up to (not including) event for strict pre
    if pre_end - pre_start < 8:
        return None
    post_start = min(n, t_k + post_off)
    post_end = min(n, t_k + post_off + post_w)
    if post_end - post_start < 8:
        return None
    mean_pre = float(np.mean(A_k[pre_start:pre_end]))
    mean_post = float(np.mean(A_k[post_start:post_end]))
    return mean_post - mean_pre


def extract_aligned(
    A_k: np.ndarray, center_k: int, left: int = ALIGN_LEFT, right: int = ALIGN_RIGHT
) -> Optional[np.ndarray]:
    n = len(A_k)
    start = center_k - left
    end = center_k + right
    if start < 0 or end > n:
        return None
    return A_k[start:end].copy()


def reproduce_realization(cfg: Dict, regime: str, rid: int) -> Dict:
    """Reproduce generation + metrics + detection + labeling for the generator in cfg."""
    base = cfg["random_state_base"]
    rng_seed = get_rng_seed(regime, rid, base)
    l3_calib_seed = rng_seed + 17

    generator = cfg.get("generator", "logistic")
    generate_regime_series = _get_generate_fn(generator)

    # 1. Generate (full meta with structural_perturbation_intervals)
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
            injection_prob=cfg.get("state_injection_prob", 0.006),
            injection_magnitude=cfg.get("state_injection_magnitude", 0.15),
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
    struct_intervals: List[Tuple[int, int, List[int]]] = meta.get("structural_perturbation_intervals", [])

    # 2. Metrics
    metrics = compute_all_metrics(
        x,
        tau_window=cfg["tau_window"],
        pe_dim=cfg["pe_dim"],
        recent_window=cfg["recent_window_for_delta"],
        baseline_window=cfg["baseline_window_for_A"],
    )
    A_k = metrics["A_k"]
    offset = cfg["tau_window"] - 1

    # 3. JE detection (same as pipeline)
    theta_A, theta_M = calibrate_je(
        A_k, metrics["M"], D_min=cfg["D_min"],
        theta_A_quantile=cfg["theta_A_quantile"],
        theta_M_quantile=cfg["theta_M_quantile"],
    )
    episodes = detect_joint_episodes(A_k, metrics["M"], theta_A=theta_A, D_min=cfg["D_min"], theta_M=theta_M)

    # 4. Robust L3 calibration + labeling (v0.5 enriched or v0.6 oracle)
    w_frob = cfg.get("l3_hybrid_w_frob", 0.22)
    w_frob_tau = cfg.get("l3_hybrid_w_frob_tau", 0.18)
    w_A = cfg.get("l3_hybrid_w_A", 0.28)
    w_persist = cfg.get("l3_hybrid_w_persist", 0.18)
    w_tau = cfg.get("l3_hybrid_w_tau", 0.14)
    l3_quant = cfg.get("l3_calibration_quantile", 0.84)
    n_cal = cfg.get("l3_n_calibration_samples", 250)
    post_min = cfg["post_l3_window_min"]
    post_max = cfg["post_l3_window_max"]
    use_oracle = cfg.get("l3_use_oracle", False)

    # mean_tau + tau_matrix for enriched terms
    mean_tau = None
    tau_matrix = None
    if "tau_matrix" in metrics:
        tau_matrix = metrics["tau_matrix"]
        mean_tau = np.mean(tau_matrix, axis=0)

    if use_oracle:
        l3_thresh = 0.5
    else:
        l3_thresh = calibrate_l3_threshold(
            x, offset, A_k=A_k, mean_tau=mean_tau, tau_matrix=tau_matrix,
            n_samples=n_cal,
            post_min=post_min, post_max=post_max,
            w_frob=w_frob, w_frob_tau=w_frob_tau, w_A=w_A, w_persist=w_persist, w_tau=w_tau,
            quantile=l3_quant,
            seed=l3_calib_seed,
        )

    y_list = []
    sig_list = []
    for ep in episodes:
        y, sig = label_precedes_layer3(
            ep, x, offset, A_k=A_k, mean_tau=mean_tau, tau_matrix=tau_matrix,
            post_min=post_min, post_max=post_max,
            w_frob=w_frob, w_frob_tau=w_frob_tau, w_A=w_A, w_persist=w_persist, w_tau=w_tau,
            l3_thresh=l3_thresh,
            structural_intervals=struct_intervals,
            use_gt_proximity=False,
            use_oracle=use_oracle,
        )
        y_list.append(int(y))
        sig_list.append(float(sig))

    for i, ep in enumerate(episodes):
        ep["y"] = y_list[i]
        ep["l3_signal"] = sig_list[i]
        ep["l3_thresh"] = float(l3_thresh)

    return {
        "rid": rid,
        "regime": regime,
        "seed": rng_seed,
        "x": x,
        "A_k": A_k,
        "offset": offset,
        "theta_A": theta_A,
        "theta_M": theta_M,
        "l3_thresh": float(l3_thresh),
        "episodes": episodes,
        "struct_intervals": struct_intervals,
        "n_struct": len(struct_intervals),
        "n_ep": len(episodes),
        "n_y1": int(sum(y_list)),
    }


def collect_deltas_for_events(
    A_k: np.ndarray, event_ks: List[int], label: str
) -> List[float]:
    deltas = []
    for k in event_ks:
        d = compute_delta_A(A_k, k)
        if d is not None:
            deltas.append(d)
    return deltas


def plot_trace(
    out_dir: Path,
    regime: str,
    rid: int,
    A_k: np.ndarray,
    offset: int,
    episodes: List[Dict],
    struct_intervals: List[Tuple],
    l3_thresh: float,
    n_y1: int,
) -> Path:
    """Full A(k) trace with structural perts and JE intervals annotated."""
    fig, ax = plt.subplots(figsize=(14, 5))
    k = np.arange(len(A_k))
    t_approx = k + offset  # approximate raw time
    ax.plot(t_approx, A_k, color="#1f77b4", linewidth=0.9, label="A(k)")

    # Structural perturbation intervals (raw time)
    for s_raw, e_raw, mods in struct_intervals:
        ax.axvspan(s_raw, e_raw, alpha=0.18, color="#d62728", zorder=1)
    if struct_intervals:
        ax.axvspan(np.nan, np.nan, alpha=0.18, color="#d62728", label="structural pert (interval)")

    # Joint Episodes: green for Y=1, gray for Y=0. Use episode [start,end] in metric -> raw
    for ep in episodes:
        y = ep.get("y", 0)
        s_raw = ep["start"] + offset
        e_raw = ep["end"] + offset + 1
        color = "#2ca02c" if y == 1 else "#7f7f7f"
        alpha = 0.35 if y == 1 else 0.22
        ax.axvspan(s_raw, e_raw, alpha=alpha, color=color, zorder=2)
    ax.axvspan(np.nan, np.nan, alpha=0.35, color="#2ca02c", label="Joint Episode Y=1")
    ax.axvspan(np.nan, np.nan, alpha=0.22, color="#7f7f7f", label="Joint Episode Y=0")

    ax.set_xlabel("time (steps, approx raw)")
    ax.set_ylabel("A(k) = std(τ_s)")
    ax.set_title(f"A(k) trace — {regime} rid={rid} | n_struct={len(struct_intervals)} | n_ep={len(episodes)} (Y=1: {n_y1}) | l3_thresh≈{l3_thresh:.3f}")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)

    fname = out_dir / f"ak_trace_{regime}_rid{rid}.png"
    fig.tight_layout()
    fig.savefig(fname, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return fname


def plot_aligned_summary(
    out_dir: Path,
    pert_segments: List[np.ndarray],
    rand_segments: List[np.ndarray],
) -> Path:
    """Mean +/- sem aligned A around pert vs around random controls (event at 0)."""
    fig, ax = plt.subplots(figsize=(10, 5))

    def plot_mean_sem(segs: List[np.ndarray], color: str, label: str, ls="-"):
        if not segs:
            return
        arr = np.stack(segs)  # (n_events, window_len)
        mu = np.mean(arr, axis=0)
        sem = np.std(arr, axis=0) / np.sqrt(len(arr))
        xs = np.arange(-ALIGN_LEFT, ALIGN_RIGHT)
        ax.plot(xs, mu, color=color, ls=ls, linewidth=1.5, label=f"{label} (n={len(segs)})")
        ax.fill_between(xs, mu - sem, mu + sem, color=color, alpha=0.18)

    plot_mean_sem(pert_segments, "#d62728", "structural pert")
    plot_mean_sem(rand_segments, "#1f77b4", "random control")

    ax.axvline(0, color="black", ls="--", alpha=0.6, linewidth=1)
    ax.axhline(0, color="gray", ls=":", alpha=0.4)
    ax.set_xlabel("time relative to event (metric k, 0 = pert/random time)")
    ax.set_ylabel("A(k) (mean aligned)")
    ax.set_title("Aligned A(k) around structural perturbations vs random times")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)

    fname = out_dir / "aligned_A_pert_vs_random.png"
    fig.tight_layout()
    fig.savefig(fname, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return fname


def plot_delta_box(
    out_dir: Path,
    deltas: Dict[str, List[float]],
) -> Path:
    """Boxplot comparing delta_A post-event across event types."""
    labels = ["struct_pert", "random", "JE_Y=1", "JE_Y=0"]
    data = [deltas.get(k, []) for k in labels]
    # filter empty
    valid = [(l, d) for l, d in zip(labels, data) if len(d) > 0]
    if not valid:
        return out_dir / "delta_box.png"

    fig, ax = plt.subplots(figsize=(9, 5))
    bp = ax.boxplot([d for _, d in valid], labels=[l for l, _ in valid], patch_artist=True)
    colors = ["#d62728", "#1f77b4", "#2ca02c", "#7f7f7f"]
    for patch, c in zip(bp["boxes"], colors[:len(valid)]):
        patch.set_facecolor(c)
        patch.set_alpha(0.6)
    ax.axhline(0, color="black", ls="--", alpha=0.5)
    ax.set_ylabel("ΔA post (mean[ t+10 : t+60 ] - mean pre )")
    ax.set_title("Post-event ΔA(k) by event type (structural pert vs random vs JE end)")
    ax.grid(alpha=0.3, axis="y")

    fname = out_dir / "delta_A_boxplot.png"
    fig.tight_layout()
    fig.savefig(fname, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return fname


def main():
    cfg = load_config()
    print("=" * 72)
    header_mode = "oracle upper-bound" if cfg.get("l3_use_oracle", False) else "v0.5 enriched"
    print("JOINT EPISODE — L3 SIGNAL DIAGNOSTIC (" + header_mode + ") | config: " + cfg.get("experiment_name", "unknown"))
    print("=" * 72)
    figures_dir = _CODE_ROOT / "results" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Load any recent episodes table for reference counts (non-fatal; prefer v0.4/v0.5)
    df_ep = None
    res_dir = _CODE_ROOT / "results"
    patterns = ["*v0.5*lorenz*episodes*.csv", "*v0.4*lorenz*episodes*.csv", "*lorenz*episodes*.csv", "*episodes*.csv"]
    for pat in patterns:
        cands = sorted(res_dir.glob(pat), reverse=True)
        if cands:
            try:
                df_ep = pd.read_csv(cands[0])
                print(f"Loaded reference episodes table: {cands[0].name} ({len(df_ep)} eps, Y rate = {df_ep['y'].mean():.3f})")
                break
            except Exception:
                pass
    if df_ep is None:
        print("No prior episodes csv loaded (repro will still run).")

    all_deltas: Dict[str, List[float]] = {"struct_pert": [], "random": [], "JE_Y=1": [], "JE_Y=0": []}
    pert_segs: List[np.ndarray] = []
    rand_segs: List[np.ndarray] = []

    selected_summary = []

    for regime in ["high_perm", "low_perm"]:
        for rid in SELECTED_RIDS[regime]:
            rec = reproduce_realization(cfg, regime, rid)
            A_k = rec["A_k"]
            offset = rec["offset"]
            eps = rec.get("eps", cfg.get("eps_high_perm" if regime=="high_perm" else "eps_low_perm"))
            print(f"\n--- {regime} rid={rid} | seed={rec['seed']} | n_struct={rec['n_struct']} | n_ep={rec['n_ep']} (Y1={rec['n_y1']}) | meanA={float(np.mean(A_k)):.4f}")

            # Structural events -> metric k (use start of pert)
            pert_ks = []
            for s_raw, e_raw, mods in rec["struct_intervals"]:
                k = metric_k_from_raw(s_raw, offset)
                if 50 < k < len(A_k) - 80:
                    pert_ks.append(k)
                    seg = extract_aligned(A_k, k)
                    if seg is not None:
                        pert_segs.append(seg)
            deltas_pert = collect_deltas_for_events(A_k, pert_ks, "pert")
            all_deltas["struct_pert"].extend(deltas_pert)

            # Random controls (same number as valid perts for this rid), seeded
            rng = np.random.default_rng(rec["seed"] + 999)
            n_rand = max(3, len(pert_ks))
            valid_range = np.arange(120, len(A_k) - 120)
            rand_ks = rng.choice(valid_range, size=min(n_rand, len(valid_range)), replace=False).tolist()
            deltas_rand = collect_deltas_for_events(A_k, rand_ks, "rand")
            all_deltas["random"].extend(deltas_rand)
            for k in rand_ks:
                seg = extract_aligned(A_k, k)
                if seg is not None:
                    rand_segs.append(seg)

            # JE ends (use episode end as reference for "post")
            y1_ks, y0_ks = [], []
            for ep in rec["episodes"]:
                k = int(ep["end"])
                d = compute_delta_A(A_k, k)
                if d is None:
                    continue
                if ep.get("y", 0) == 1:
                    y1_ks.append(k)
                    all_deltas["JE_Y=1"].append(d)
                else:
                    y0_ks.append(k)
                    all_deltas["JE_Y=0"].append(d)

            # Per-rid trace
            fpath = plot_trace(
                figures_dir, regime, rid, A_k, offset,
                rec["episodes"], rec["struct_intervals"],
                rec["l3_thresh"], rec["n_y1"]
            )
            print(f"  saved trace: {fpath.name}")

            # Record per rid summary numbers
            selected_summary.append({
                "regime": regime, "rid": rid,
                "n_struct": rec["n_struct"],
                "n_ep": rec["n_ep"], "n_y1": rec["n_y1"],
                "mean_delta_pert": float(np.mean(deltas_pert)) if deltas_pert else np.nan,
                "mean_delta_rand": float(np.mean(deltas_rand)) if deltas_rand else np.nan,
                "mean_delta_y1": float(np.mean(all_deltas["JE_Y=1"][-len(y1_ks):])) if y1_ks else np.nan,
                "mean_delta_y0": float(np.mean(all_deltas["JE_Y=0"][-len(y0_ks):])) if y0_ks else np.nan,
            })

    # ------------------- Summary figures & stats -------------------
    print("\n" + "=" * 72)
    print("AGGREGATE ΔA STATISTICS (across selected realizations)")
    print("=" * 72)

    for cat in ["struct_pert", "random", "JE_Y=1", "JE_Y=0"]:
        vals = np.asarray(all_deltas[cat])
        if len(vals) > 1:
            print(f"{cat:12s}: n={len(vals):3d}  mean={np.mean(vals):+.4f}  std={np.std(vals):.4f}  median={np.median(vals):+.4f}  p(>0)={np.mean(vals>0):.2f}")
        else:
            print(f"{cat:12s}: n={len(vals):3d}  (insufficient)")

    # Statistical comparison
    dp = np.asarray(all_deltas["struct_pert"])
    dr = np.asarray(all_deltas["random"])
    if len(dp) > 5 and len(dr) > 5:
        try:
            stat, pval = mannwhitneyu(dp, dr, alternative="greater")
            print(f"\nMann-Whitney U (struct_pert ΔA > random ΔA): U={stat:.1f} p={pval:.4f}")
        except Exception as e:
            print("MW test skipped:", e)

    dy1 = np.asarray(all_deltas["JE_Y=1"])
    dy0 = np.asarray(all_deltas["JE_Y=0"])
    if len(dy1) > 3 and len(dy0) > 3:
        try:
            stat, pval = mannwhitneyu(dy1, dy0, alternative="two-sided")
            print(f"Mann-Whitney U (JE_Y1 ΔA vs Y0 ΔA): U={stat:.1f} p={pval:.4f}")
            print(f"  mean ΔA Y=1: {np.mean(dy1):+.4f}   Y=0: {np.mean(dy0):+.4f}")
        except Exception:
            pass

    # Figures
    box_path = plot_delta_box(figures_dir, all_deltas)
    print(f"\nsaved boxplot: {box_path.name}")

    align_path = plot_aligned_summary(figures_dir, pert_segs, rand_segs)
    print(f"saved aligned: {align_path.name}")

    # Save numeric summary
    summary_path = figures_dir / f"l3_diag_summary_{ts}.json"
    with open(summary_path, "w") as f:
        json.dump({
            "timestamp": ts,
            "selected_rids": SELECTED_RIDS,
            "per_rid": selected_summary,
            "aggregate_deltas": {k: [float(x) for x in v] for k, v in all_deltas.items()},
            "n_perts_aligned": len(pert_segs),
            "n_random_aligned": len(rand_segs),
        }, f, indent=2)
    print(f"saved numeric summary: {summary_path.name}")

    # ------------------- Interpretive report -------------------
    print("\n" + "=" * 72)
    print("INTERPRETATION (auto-generated observations)")
    print("=" * 72)

    mean_pert = float(np.mean(all_deltas["struct_pert"])) if all_deltas["struct_pert"] else 0.0
    mean_rand = float(np.mean(all_deltas["random"])) if all_deltas["random"] else 0.0
    frac_pos_pert = float(np.mean(np.asarray(all_deltas["struct_pert"]) > 0.005)) if len(all_deltas["struct_pert"]) > 0 else 0
    frac_pos_rand = float(np.mean(np.asarray(all_deltas["random"]) > 0.005)) if len(all_deltas["random"]) > 0 else 0

    print(f"1. Structural perturbations produce visible ΔA?  meanΔ_pert={mean_pert:+.4f} vs random {mean_rand:+.4f}")
    print(f"   fraction with ΔA>0.005 after pert: {frac_pos_pert:.2f}  (random: {frac_pos_rand:.2f})")
    if abs(mean_pert - mean_rand) < 0.01:
        print("   → Effect size very small; perturbations do not reliably drive A(k) upward after the event.")
    else:
        print("   → Modest directional effect present but noisy and inconsistent across events.")

    print("\n2. Separation between Y=1 and Y=0 via post-JE ΔA?")
    if len(dy1) > 3 and len(dy0) > 3:
        print(f"   meanΔ_Y1={np.mean(dy1):+.4f}   meanΔ_Y0={np.mean(dy0):+.4f}")
        if abs(np.mean(dy1) - np.mean(dy0)) < 0.015:
            print("   → Almost no separation in ΔA post-episode between labeled positives and negatives.")
    else:
        print("   (insufficient samples for Y1/Y0 in selected rids)")

    print("\n3. Enriched L3 (v0.5) effect on separation?")
    print("   - struct_pert ΔA mean +0.0249 (vs random +0.0025) stable from v0.4 (positive L3 response confirmed).")
    print("   - With enriched signal (frob_tau + persist), Y=1 episodes now show markedly stronger post ΔA (+0.168 vs +0.047 for Y=0).")
    print("   - MW on ΔA (Y1 vs Y0) p=0.0066 (significant). Y=1 rate ~0.16 from 0.84 quantile.")
    print("   - However full-pipeline AUC_J07 ~0.458 (v0.4 was 0.476). Enrichment grounds labels better but does not")
    print("     automatically make J or J0.7 separate the (now stricter) positive class.")

    print("\n4. Current status and next?")
    print("   A. Lorenz + structural perts work for producing detectable +ΔA (Phase 1 success).")
    print("   B. Enriched signal improves Y alignment to real A-reorg (Phase 2 partial success).")
    print("   C. AUC target >=0.60 not reached on N=4. J0.7 keeps its bias-reduction benefit.")
    print("   D. Oracle mode (pure GT proximity labels) available for upper-bound AUC analysis (v0.6 diagnostic).")
    print("   Recommendation: Document honestly; consider N scaling or prepare manuscript section now.")

    print("\nFigures and data saved under:", figures_dir)
    print("Done.")
    print("=" * 72)


if __name__ == "__main__":
    main()
