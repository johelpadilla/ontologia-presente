"""
recd_metrics.py
Self-contained implementation of core RECD-derived metrics for the Joint Episode study.

- Systemic Tau τ_s(k) per module via normalized permutation entropy (Bandt-Pompe style)
  matching parameters from prior work: TAU_WINDOW=85, dim=3
- A(k): antisynchronization = std(τ_s across modules at each aligned time)
- M(k): simplified critical mass using hyper-persistence z-score of recent τ_s + trapping proxy

All functions are pure, vectorized where practical, and seeded externally.
"""

import numpy as np
import math
from itertools import permutations
from typing import Dict, Tuple, Optional
import pandas as pd


def compute_permutation_entropy(ts: np.ndarray, dim: int = 3, lag: int = 1) -> float:
    """
    Compute normalized permutation entropy (disorder) for a 1D time series segment.
    Returns value in [0, 1] where 1 = maximum disorder.
    """
    ts = np.asarray(ts, dtype=float)
    n = len(ts)
    if n < dim * lag:
        return 1.0  # treat as fully disordered if too short

    # Collect ordinal patterns
    pattern_count: Dict[Tuple[int, ...], int] = {}
    n_patterns = 0
    for i in range(n - (dim - 1) * lag):
        vec = ts[i : i + dim * lag : lag]
        # Rank with stable tie-breaking (argsort on values + small noise for determinism not needed)
        ranks = tuple(np.argsort(np.argsort(vec)))  # double argsort gives stable ranks 0..dim-1
        # Better: use tuple of indices after sorting
        order = tuple(np.argsort(vec))
        pattern_count[order] = pattern_count.get(order, 0) + 1
        n_patterns += 1

    if n_patterns == 0:
        return 1.0

    # Shannon entropy
    pe = 0.0
    for cnt in pattern_count.values():
        p = cnt / n_patterns
        pe -= p * np.log(p)

    max_pe = math.log(math.factorial(dim))
    disorder = pe / max_pe if max_pe > 0 else 1.0
    return float(np.clip(disorder, 0.0, 1.0))


def compute_tau_s(series: np.ndarray, window: int = 85, dim: int = 3, lag: int = 1) -> np.ndarray:
    """
    Compute τ_s(k) for a single component series using sliding windows.
    τ_s = 3.0 + 19.0 * (1 - disorder)^1.6
    Returns array of length len(series) - window + 1
    """
    series = np.asarray(series, dtype=float)
    n = len(series)
    if n < window:
        # pad or return single value
        disorder = compute_permutation_entropy(series, dim=dim, lag=lag)
        tau = 3.0 + 19.0 * (1.0 - disorder) ** 1.6
        return np.array([tau])

    taus = np.zeros(n - window + 1)
    for i in range(n - window + 1):
        seg = series[i : i + window]
        disorder = compute_permutation_entropy(seg, dim=dim, lag=lag)
        tau = 3.0 + 19.0 * (1.0 - disorder) ** 1.6
        taus[i] = tau
    return taus


def compute_tau_matrix(x: np.ndarray, window: int = 85, dim: int = 3, lag: int = 1) -> np.ndarray:
    """
    x : (T, N_modules) raw time series matrix (or (N, T) ? convention: we'll use (T, N) and transpose inside)
    Returns tau_matrix of shape (N_modules, n_tau) aligned to the end of each window.
    """
    x = np.asarray(x)
    if x.ndim == 1:
        x = x[:, np.newaxis]
    if x.shape[0] < x.shape[1]:  # heuristic: if T < N treat as (N,T)
        x = x.T
    T, N = x.shape
    taus_list = []
    min_len = None
    for i in range(N):
        ts = x[:, i]
        tau_i = compute_tau_s(ts, window=window, dim=dim, lag=lag)
        taus_list.append(tau_i)
        if min_len is None or len(tau_i) < min_len:
            min_len = len(tau_i)
    # Trim all to same length (last windows)
    taus_list = [t[-min_len:] for t in taus_list]
    tau_mat = np.vstack(taus_list)  # (N, n_tau)
    return tau_mat


def compute_antisynchronization(tau_matrix: np.ndarray) -> np.ndarray:
    """
    A(k) = std( τ_s across modules ) for each aligned time index k.
    tau_matrix: (N_modules, n_k)
    """
    if tau_matrix.ndim != 2:
        raise ValueError("tau_matrix must be (N, n_k)")
    return np.std(tau_matrix, axis=0)


def compute_hyper_persistence_z(tau_i: np.ndarray, recent_window: int = 80) -> np.ndarray:
    """
    Hyper-persistence z-score for one module: (tau_i - rolling_mean) / rolling_std
    """
    s = pd.Series(tau_i)
    mu = s.rolling(window=recent_window, min_periods=1).mean().values
    sigma = s.rolling(window=recent_window, min_periods=1).std().fillna(1e-8).values + 1e-8
    z = (tau_i - mu) / sigma
    return z


def compute_trapping_proxy(tau_i: np.ndarray, high_tau_quantile: float = 0.7) -> np.ndarray:
    """
    Simple trapping duration proxy: run-length of 'high persistence' segments.
    """
    thresh = np.quantile(tau_i, high_tau_quantile) if len(tau_i) > 10 else np.mean(tau_i)
    is_high = tau_i >= thresh
    durations = np.zeros_like(tau_i, dtype=float)
    cur = 0
    for j in range(len(is_high)):
        if is_high[j]:
            cur += 1
        else:
            cur = 0
        durations[j] = cur
    # normalize roughly
    return durations / (np.max(durations) + 1e-8) if np.max(durations) > 0 else durations


def compute_M_i(tau_matrix: np.ndarray, recent_window: int = 80, w_persist: float = 0.6, w_trap: float = 0.4) -> np.ndarray:
    """
    Per-module M_i(k) using hyper-persist z + trapping proxy.
    Returns (N, n_k)
    """
    N, n_k = tau_matrix.shape
    M = np.zeros_like(tau_matrix)
    for i in range(N):
        z = compute_hyper_persistence_z(tau_matrix[i], recent_window=recent_window)
        trap = compute_trapping_proxy(tau_matrix[i])
        # Clip extreme z for stability
        z = np.clip(z, -4, 6)
        M[i] = w_persist * z + w_trap * trap
    return M


def compute_system_M(M_i: np.ndarray) -> np.ndarray:
    """
    Aggregate system-level critical mass: max over modules at each k (presence of at least one strong intensification).
    Alternative: mean of positive contributions. We use max for 'exists k* M>= '
    """
    return np.max(M_i, axis=0)


def compute_all_metrics(x: np.ndarray,
                        tau_window: int = 85,
                        pe_dim: int = 3,
                        recent_window: int = 80,
                        baseline_window: int = 200) -> Dict[str, np.ndarray]:
    """
    Full pipeline from raw x (T, N) to A(k), M(k) aligned.
    Returns dict with:
      'tau_matrix', 'A_k', 'A_baseline', 'M_i', 'M'
      lengths are shorter due to windows.
    """
    tau_matrix = compute_tau_matrix(x, window=tau_window, dim=pe_dim)
    A_k = compute_antisynchronization(tau_matrix)

    # baseline for reference (used in labeling/detection sometimes)
    if len(A_k) >= 2:
        A_base = pd.Series(A_k).rolling(window=min(baseline_window, len(A_k)), min_periods=1).mean().values
    else:
        A_base = np.full_like(A_k, np.mean(A_k))

    M_i = compute_M_i(tau_matrix, recent_window=recent_window)
    M = compute_system_M(M_i)

    return {
        'tau_matrix': tau_matrix,
        'A_k': A_k,
        'A_baseline': A_base,
        'M_i': M_i,
        'M': M,
        'n_tau': len(A_k)
    }
