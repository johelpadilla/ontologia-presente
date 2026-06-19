"""
labeling/layer3_label.py
Label whether a detected Joint Episode precedes a detectable Layer 3 (structural reorganization).

v0.5 Phase 2 (enriched L3 on Lorenz after v0.4 positive-ΔA confirmation):
- Hybrid signal now includes:
    * frob_x (corr x)
    * frob_tau (corr of per-module τ_s trajectories)  [NEW]
    * delta_A (rise in A=std(τ))
    * persist (fraction of post A elevated vs pre baseline)  [NEW: sustainability/persistence]
    * |delta_mean_tau|
- Weights (proposed, sum to ~1): 0.22 / 0.18 / 0.28 / 0.18 / 0.14
- Robust random-candidate quantile calibration (0.84) independent of episodes.
- Pre windows strict before JE start.
- Backward compatible defaults + legacy use_sustained dampener.

v0.6 micro-iter (oracle diagnostic):
- Added pure `use_oracle=True` mode (for upper-bound only): Y=1 iff at least one structural_perturbation start falls in [t_e + post_min, t_e + post_max].
- Completely bypasses hybrid l3_signal when oracle active.
- Same post windows as enriched labeling for direct comparability.
- Oracle mode is diagnostic only (never default); used to compute theoretical max AUC achievable with current J / J0.7 scores under perfect GT proximity labels.

Goal: extract stronger, more specific signal of actual structural reorg from the Lorenz perts,
improving Y=1 vs Y=0 separation for Joint Score evaluation while preserving J0.7 advantages.
Also: establish upper bound on what perfect L3 labels can extract from present scores.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy.stats import pearsonr


def compute_corr_matrix(x_seg: np.ndarray) -> np.ndarray:
    """x_seg: (t, n_mod) -> (n_mod, n_mod) corr"""
    if x_seg.shape[0] < 5:
        return np.eye(x_seg.shape[1])
    c = np.corrcoef(x_seg.T)
    c = np.nan_to_num(c, nan=0.0)
    return c


def frobenius_diff(c1: np.ndarray, c2: np.ndarray) -> float:
    return float(np.linalg.norm(c1 - c2, ord="fro"))


def compute_tau_corr_matrix(tau_seg: np.ndarray) -> np.ndarray:
    """tau_seg: (N_modules, t_len) -> (N,N) corr between modules' τ trajectories in window."""
    if tau_seg.shape[1] < 4:
        return np.eye(tau_seg.shape[0])
    c = np.corrcoef(tau_seg)
    c = np.nan_to_num(c, nan=0.0)
    return c


def label_precedes_layer3(
    episode: Dict,
    x: np.ndarray,
    metric_to_raw_offset: int,
    A_k: Optional[np.ndarray] = None,
    mean_tau: Optional[np.ndarray] = None,
    tau_matrix: Optional[np.ndarray] = None,
    post_min: int = 50,
    post_max: int = 150,
    w_frob: float = 0.22,
    w_frob_tau: float = 0.18,
    w_A: float = 0.28,
    w_persist: float = 0.18,
    w_tau: float = 0.14,
    l3_thresh: float = 0.0,
    min_seg_len: int = 20,
    use_sustained: bool = False,
    structural_intervals: Optional[List[Tuple[int, int, List[int]]]] = None,
    use_gt_proximity: bool = False,
    gt_lead_max: int = 150,
    use_oracle: bool = False,
) -> Tuple[bool, float]:
    """
    Label whether a Joint Episode precedes detectable Layer 3 (structural reorganization).

    Enriched hybrid signal (v0.5 Phase 2, Lorenz focus):
        frob_x   = Frobenius norm of corr(x) change pre vs post
        frob_tau = Frobenius on corr(τ_s per-module trajectories) pre vs post   [NEW]
        delta_A  = mean(A_post) - mean(A_pre)
        persist  = fraction of post A(k) that stays elevated vs pre baseline   [NEW: sustainability]
        delta_mtau = mean(mean_tau_post) - mean(mean_tau_pre)
        l3_signal = w_frob*frob_x + w_frob_tau*frob_tau + w_A*max(0,delta_A) + w_persist*persist + w_tau*abs(delta_mtau)

    Default weights (sum~1): 0.22 frob_x + 0.18 frob_tau + 0.28 A + 0.18 persist + 0.14 tau.
    Y=1 iff l3_signal >= thresh (calibrated on random candidates).

    Pre window uses episode start to avoid low-A contamination.

    use_oracle (v0.6 diagnostic, upper bound only):
        When True: completely ignore hybrid signal. Y=1 if and only if at least one
        structural perturbation interval starts inside the post-window [t_e_raw + post_min, t_e_raw + post_max].
        Uses exactly the same post windows as the enriched labeler for apples-to-apples comparison.
        Returns signal=1.0 or 0.0 as proxy. Intended solely for computing theoretical max AUC
        of J / J0.7 under perfect ground-truth proximity labels. Do not use for main paper results.
    """
    end_metric = episode["end"]
    start_metric = episode.get("start", max(0, end_metric - 20))
    t_e_raw = end_metric + metric_to_raw_offset
    t_s_raw = start_metric + metric_to_raw_offset

    # --- PURE ORACLE / GROUND-TRUTH MODE (diagnostic upper bound) ---
    # Y decided exclusively by existence of a structural pert start in post-window.
    # Bypass all hybrid signal computation.
    if use_oracle and structural_intervals is not None:
        post_start = t_e_raw + post_min
        post_end = t_e_raw + post_max
        y = 0
        for s, e, _mods in structural_intervals:
            if post_start <= s <= post_end:
                y = 1
                break
        return bool(y), (1.0 if y else 0.0)

    T, N = x.shape
    start_post = min(T - 1, t_e_raw + post_min)
    end_post = min(T, t_e_raw + post_max + 1)

    # Pre window: strictly before the Joint Episode starts (avoid low-A contamination)
    pre_len = 70
    pre_end = max(min_seg_len, t_s_raw - 8)
    pre_start = max(0, pre_end - pre_len)

    if end_post - start_post < min_seg_len or pre_end - pre_start < min_seg_len:
        return False, 0.0

    c_pre = compute_corr_matrix(x[pre_start:pre_end])
    c_post = compute_corr_matrix(x[start_post:end_post])
    frob_x = frobenius_diff(c_pre, c_post)

    # delta_A and delta_mean_tau using metric indices (aligned to A_k / mean_tau)
    delta_a = 0.0
    delta_mtau = 0.0
    a_pre_start = a_pre_end = a_post_start = a_post_end = 0
    if A_k is not None and len(A_k) > 10:
        a_pre_end = max(0, start_metric - 3)
        a_pre_start = max(0, a_pre_end - 70)
        a_post_start = min(len(A_k) - 1, end_metric + max(2, post_min // 1))
        a_post_end = min(len(A_k), end_metric + (post_max // 1) + 3)
        if a_post_end > a_post_start + 4 and a_pre_end > a_pre_start + 4:
            mean_pre = float(np.mean(A_k[a_pre_start : a_pre_end + 1]))
            mean_post = float(np.mean(A_k[a_post_start : a_post_end]))
            delta_a = mean_post - mean_pre

    if mean_tau is not None and len(mean_tau) > 10:
        mt_pre_end = max(0, start_metric - 3)
        mt_pre_start = max(0, mt_pre_end - 70)
        mt_post_start = min(len(mean_tau) - 1, end_metric + max(2, post_min // 1))
        mt_post_end = min(len(mean_tau), end_metric + (post_max // 1) + 3)
        if mt_post_end > mt_post_start + 4 and mt_pre_end > mt_pre_start + 4:
            mtau_pre = float(np.mean(mean_tau[mt_pre_start : mt_pre_end + 1]))
            mtau_post = float(np.mean(mean_tau[mt_post_start : mt_post_end]))
            delta_mtau = mtau_post - mtau_pre

    # NEW: frob_tau on τ_s correlation structure (N modules' τ timecourses)
    frob_tau = 0.0
    if tau_matrix is not None and getattr(tau_matrix, 'ndim', 0) == 2 and tau_matrix.shape[1] > 10:
        tp_pre_end = a_pre_end + 1
        if (a_pre_end > a_pre_start + 4) and (a_post_end > a_post_start + 4):
            tau_pre = tau_matrix[:, a_pre_start:tp_pre_end]
            tau_post = tau_matrix[:, a_post_start:a_post_end]
            if tau_pre.shape[1] >= 3 and tau_post.shape[1] >= 3:
                ctau_pre = compute_tau_corr_matrix(tau_pre)
                ctau_post = compute_tau_corr_matrix(tau_post)
                frob_tau = frobenius_diff(ctau_pre, ctau_post)

    # NEW: persistence fraction (how much of post-window A stays elevated vs pre level)
    persist = 0.0
    a_pre_m = 0.0
    if A_k is not None and len(A_k) > 10 and a_post_end > a_post_start + 2:
        a_pre_m = float(np.mean(A_k[max(0, a_pre_start):a_pre_end + 1])) if a_pre_end > a_pre_start else float(np.mean(A_k[:a_pre_end+1]))
        post_vals = A_k[a_post_start:a_post_end]
        margin = 0.01
        persist = float(np.mean(post_vals > (a_pre_m + margin)))

    # Composite enriched signal (v0.5 Phase 2 weights)
    signal = (w_frob * frob_x +
              w_frob_tau * frob_tau +
              w_A * max(0.0, delta_a) +
              w_persist * persist +
              w_tau * abs(delta_mtau))

    # Optional legacy sustained dampener (kept for compat; enriched uses positive persist term above)
    if use_sustained and A_k is not None and delta_a > 0 and a_post_end > a_post_start + 5:
        post_vals = A_k[a_post_start:a_post_end]
        frac = float(np.mean((post_vals - a_pre_m) > max(0.008, 0.2 * max(0.0, delta_a))))
        if frac < 0.30:
            signal *= 0.65

    y = 1 if signal >= l3_thresh else 0

    # Optional ground-truth proximity using recorded structural perturbation intervals (for diagnostics/ablations)
    # Default: OFF. When enabled, any structural event starting in the post window forces Y=1.
    if use_gt_proximity and structural_intervals:
        for s, e, _mods in structural_intervals:
            if t_e_raw + post_min <= s <= t_e_raw + gt_lead_max:
                y = 1
                signal = max(signal, l3_thresh + 1e-3)
                break

    return bool(y), float(signal)


def calibrate_l3_threshold(
    x: np.ndarray,
    metric_offset: int,
    episodes: Optional[List[Dict]] = None,
    A_k: Optional[np.ndarray] = None,
    mean_tau: Optional[np.ndarray] = None,
    tau_matrix: Optional[np.ndarray] = None,
    n_samples: int = 250,
    post_min: int = 50,
    post_max: int = 150,
    w_frob: float = 0.22,
    w_frob_tau: float = 0.18,
    w_A: float = 0.28,
    w_persist: float = 0.18,
    w_tau: float = 0.14,
    quantile: float = 0.84,
    seed: Optional[int] = 1234,
) -> float:
    """
    Robust data-driven threshold using random candidate times sampled across the realization
    (independent of detected Joint Episodes). This is the recommended calibrator.

    Supports enriched v0.5 signal (frob_tau + persist).
    Returns the quantile of the hybrid l3_signal distribution.

    Note: when running in pure oracle mode, calibration is skipped (thresh irrelevant; Y decided by GT proximity alone).
    """
    signals: List[float] = []
    rng = np.random.default_rng(seed)
    T = x.shape[0]
    max_cand = max(20, (len(A_k) if A_k is not None else T) - post_max - 5)
    n_samp = min(n_samples, max_cand)
    if n_samp < 5:
        return 0.28

    candidates = rng.choice(max_cand, size=n_samp, replace=False)
    for c in candidates:
        # minimal fake episode at candidate time (end-focused)
        fake = {"start": max(0, int(c) - 4), "end": int(c)}
        _, sig = label_precedes_layer3(
            fake, x, metric_offset, A_k=A_k, mean_tau=mean_tau, tau_matrix=tau_matrix,
            post_min=post_min, post_max=post_max,
            w_frob=w_frob, w_frob_tau=w_frob_tau, w_A=w_A, w_persist=w_persist, w_tau=w_tau,
            l3_thresh=0.0
        )
        signals.append(sig)

    if len(signals) < 5:
        return 0.28
    return float(np.quantile(np.asarray(signals), quantile))


# Backward-compatible thin wrapper (uses old episode-centered sampling; not recommended)
def calibrate_l3_threshold_legacy(x: np.ndarray, metric_offset: int, episodes: List[Dict],
                                  post_min=50, post_max=150, quantile: float = 0.85) -> float:
    """Legacy (biased) calibrator kept for reference. Prefer calibrate_l3_threshold."""
    signals = []
    for ep in episodes:
        _, s = label_precedes_layer3(
            ep, x, metric_offset,
            post_min=post_min, post_max=post_max,
            l3_thresh=0.0
        )
        signals.append(s)
    if len(signals) < 3:
        return 0.30
    return float(np.quantile(signals, quantile))
