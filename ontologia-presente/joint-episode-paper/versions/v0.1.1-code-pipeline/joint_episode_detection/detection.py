"""
joint_episode_detection/detection.py
Detection of Joint Episodes from A(k) and M(k) series.

A Joint Episode is a maximal interval [t_start, t_end] (indices into the metric arrays)
satisfying:
  - A(k) < theta_A for all k in interval
  - length >= D_min
  - exists k in interval with M(k) >= theta_M

Returns list of episodes with start, end (in metric time), D, mean_M, J, J07, etc.
"""

import numpy as np
from typing import List, Dict, Tuple


def detect_joint_episodes(
    A_k: np.ndarray,
    M: np.ndarray,
    theta_A: float,
    D_min: int = 7,
    theta_M: float = 1.2,
) -> List[Dict]:
    """
    Return list of episode dicts.
    Each: {'start': int, 'end': int, 'D': int, 'mean_M': float, 'max_M': float, 'J': float, 'J_07': float}
    Time indices refer to the arrays passed (0-based into A_k / M).
    """
    n = len(A_k)
    if len(M) != n:
        # align: use min length
        n = min(len(A_k), len(M))
        A_k = A_k[:n]
        M = M[:n]

    episodes = []
    i = 0
    while i < n:
        if A_k[i] < theta_A:
            # start of potential episode
            j = i
            while j < n and A_k[j] < theta_A:
                j += 1
            D = j - i
            if D >= D_min:
                seg_M = M[i:j]
                mean_M = float(np.mean(seg_M))
                max_M = float(np.max(seg_M))
                if max_M >= theta_M:  # or np.any(seg_M >= theta_M)
                    J = D * mean_M
                    J07 = (D ** 0.7) * mean_M
                    episodes.append({
                        "start": int(i),
                        "end": int(j - 1),
                        "D": int(D),
                        "mean_M": mean_M,
                        "max_M": max_M,
                        "J": float(J),
                        "J_07": float(J07),
                    })
            i = j
        else:
            i += 1
    return episodes


def calibrate_thresholds(A_k: np.ndarray, M: np.ndarray, D_min: int,
                         theta_A_quantile: float = 0.35, theta_M_quantile: float = 0.80) -> Tuple[float, float]:
    """
    Simple regime-calibrated thresholds.
    theta_A : quantile of A
    theta_M : quantile of M (applied to system M)
    """
    theta_A = float(np.quantile(A_k, theta_A_quantile))
    theta_M = float(np.quantile(M, theta_M_quantile))
    return theta_A, theta_M
