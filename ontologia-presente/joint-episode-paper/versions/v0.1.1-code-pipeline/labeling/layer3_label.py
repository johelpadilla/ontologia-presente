"""
labeling/layer3_label.py
Label whether a detected Joint Episode precedes a detectable Layer 3 (structural reorganization).

Operational definition:
  For episode ending at t_e (in metric time), look in post window [t_e + post_min, t_e + post_max]
  (mapped back to original time if needed).

  Compute correlation matrix (Pearson) of the raw x in pre and post segments (short windows).
  Detect if Frobenius norm of difference exceeds a quantile threshold of observed changes.

  Simpler robust proxy used: change in average pairwise |corr| or ||C_post - C_pre||_F > thresh.
"""

import numpy as np
from typing import Dict, List, Tuple
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


def label_precedes_layer3(
    episode: Dict,
    x: np.ndarray,
    metric_to_raw_offset: int,
    post_min: int = 50,
    post_max: int = 150,
    l3_thresh: float = 0.35,
    min_seg_len: int = 20,
) -> Tuple[bool, float]:
    """
    episode: dict with 'end' (metric index)
    x: raw series (T_raw, N)
    metric_to_raw_offset: how many steps the metric arrays lag the raw (usually tau_window-1)
    Returns (y_label, frobenius_change)
    """
    end_metric = episode["end"]
    # map to raw time
    t_e_raw = end_metric + metric_to_raw_offset

    T, N = x.shape
    start_post = min(T - 1, t_e_raw + post_min)
    end_post = min(T, t_e_raw + post_max + 1)

    # pre segment: just before episode or fixed length before t_e
    pre_start = max(0, t_e_raw - 60)
    pre_end = max(min_seg_len, t_e_raw - 5)

    if end_post - start_post < min_seg_len or pre_end - pre_start < min_seg_len:
        return False, 0.0

    c_pre = compute_corr_matrix(x[pre_start:pre_end])
    c_post = compute_corr_matrix(x[start_post:end_post])

    frob = frobenius_diff(c_pre, c_post)

    y = 1 if frob >= l3_thresh else 0
    return bool(y), frob


def calibrate_l3_threshold(x: np.ndarray, metric_offset: int, episodes: List[Dict],
                           post_min=50, post_max=150, quantile: float = 0.85) -> float:
    """Compute a data-driven threshold from observed post-episode changes."""
    changes = []
    for ep in episodes:
        _, f = label_precedes_layer3(
            ep, x, metric_offset,
            post_min=post_min, post_max=post_max,
            l3_thresh=0.0  # force compute
        )
        changes.append(f)
    if len(changes) < 3:
        return 0.30  # sensible default
    return float(np.quantile(changes, quantile))
