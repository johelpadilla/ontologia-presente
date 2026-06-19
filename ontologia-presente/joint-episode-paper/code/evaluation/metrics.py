"""
evaluation/metrics.py
Compute performance metrics to compare J and J_0.7 .

- AUC-ROC (using sklearn)
- Spearman correlation of score with D
- Group separation stats (mean, median per class)
- Optional Mann-Whitney U (scipy)
"""

import numpy as np
from typing import Dict, List, Tuple
from scipy.stats import spearmanr, mannwhitneyu
from sklearn.metrics import roc_auc_score


def compute_auc(y_true: np.ndarray, scores: np.ndarray) -> float:
    """Safe AUC. Returns nan if degenerate."""
    y = np.asarray(y_true).astype(int)
    s = np.asarray(scores).astype(float)
    if len(np.unique(y)) < 2:
        return np.nan
    try:
        return float(roc_auc_score(y, s))
    except Exception:
        return np.nan


def evaluate_scores(
    episodes: List[Dict],
    y_labels: List[int],
    score_key: str = "J"
) -> Dict[str, float]:
    """
    episodes: list of episode dicts containing 'J', 'J_07', 'D'
    y_labels: 0/1 list aligned
    """
    if len(episodes) == 0 or len(y_labels) == 0:
        return {"auc": np.nan, "spearman_D": np.nan, "n": 0}

    scores = np.array([ep[score_key] for ep in episodes])
    D = np.array([ep["D"] for ep in episodes])
    y = np.array(y_labels)

    auc = compute_auc(y, scores)
    try:
        rho, _ = spearmanr(scores, D)
    except Exception:
        rho = np.nan

    # separation
    pos = scores[y == 1]
    neg = scores[y == 0]
    sep = {
        "mean_pos": float(np.mean(pos)) if len(pos) else np.nan,
        "mean_neg": float(np.mean(neg)) if len(neg) else np.nan,
        "median_pos": float(np.median(pos)) if len(pos) else np.nan,
        "median_neg": float(np.median(neg)) if len(neg) else np.nan,
    }

    # Mann-Whitney if possible
    try:
        if len(pos) > 0 and len(neg) > 0:
            u_stat, p = mannwhitneyu(pos, neg, alternative="greater")
            mw = {"u_stat": float(u_stat), "p": float(p)}
        else:
            mw = {"u_stat": np.nan, "p": np.nan}
    except Exception:
        mw = {"u_stat": np.nan, "p": np.nan}

    return {
        "auc": auc,
        "spearman_D": float(rho),
        "n_pos": int(np.sum(y)),
        "n_neg": int(len(y) - np.sum(y)),
        "n": len(y),
        **sep,
        "mw_u": mw["u_stat"],
        "mw_p": mw["p"],
    }


def compare_J_vs_J07(
    episodes: List[Dict],
    y_labels: List[int]
) -> Dict:
    res_J = evaluate_scores(episodes, y_labels, "J")
    res_J07 = evaluate_scores(episodes, y_labels, "J_07")
    return {
        "J": res_J,
        "J_07": res_J07,
        "delta_auc": (res_J07["auc"] - res_J["auc"]) if not np.isnan(res_J07["auc"]) and not np.isnan(res_J["auc"]) else np.nan,
        "delta_spearman": (res_J07["spearman_D"] - res_J["spearman_D"]) if not np.isnan(res_J07.get("spearman_D", np.nan)) else np.nan,
    }
