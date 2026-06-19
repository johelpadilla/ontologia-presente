"""
synthetic_generation/logistic.py
4-component coupled logistic map with controlled structural change injections.

Standard diffusive coupling form:
  x_i(t+1) = (1-eps) * r * x_i(t)*(1-x_i(t)) + (eps / (N-1)) * sum_{j!=i} r * x_j(t)*(1-x_j(t))

Injections: with small probability, apply a shock to 1 or 2 modules (additive or multiplicative) to induce structural reorganization.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.seeding import get_rng


def generate_coupled_logistic(
    T: int = 2000,
    n_modules: int = 4,
    r: float = 3.8,
    eps: float = 0.05,
    noise: float = 0.001,
    seed: Optional[int] = None,
    injection_prob: float = 0.01,
    injection_magnitude: float = 0.25,
    use_injections: bool = True,
) -> Tuple[np.ndarray, Dict]:
    """
    Generate multivariate time series from coupled logistic map.
    Returns x of shape (T, N), and metadata dict with injection_times, params.
    """
    rng = get_rng(seed) if seed is not None else np.random.default_rng()

    x = np.zeros((T, n_modules))
    x[0] = rng.uniform(0.1, 0.9, size=n_modules)

    injection_times: List[int] = []

    for t in range(T - 1):
        xt = x[t]
        mean_coupled = np.mean(xt)
        for i in range(n_modules):
            local = r * xt[i] * (1 - xt[i])
            # diffusive mean-field style
            coupled = r * mean_coupled * (1 - mean_coupled)
            x[t+1, i] = (1 - eps) * local + eps * coupled
            # small additive noise
            x[t+1, i] += rng.normal(0, noise)

        # structural injection (shock to simulate change)
        if use_injections and rng.random() < injection_prob:
            # pick 1 or 2 modules to shock
            n_shock = rng.integers(1, 3)
            mods = rng.choice(n_modules, size=n_shock, replace=False)
            for m in mods:
                # multiplicative or additive kick that can alter attractor locally
                kick = rng.uniform(0.8, 1.2) * injection_magnitude * (1 if rng.random() > 0.5 else -1)
                x[t+1, m] = np.clip(x[t+1, m] + kick, 0.01, 0.99)
            injection_times.append(t + 1)

        # clip to valid logistic domain
        x[t+1] = np.clip(x[t+1], 0.001, 0.999)

    meta = {
        "T": T,
        "n_modules": n_modules,
        "r": r,
        "eps": eps,
        "noise": noise,
        "injection_times": np.array(injection_times),
        "use_injections": use_injections,
        "seed": seed,
    }
    return x, meta


def generate_regime_series(
    regime: str = "high_perm",
    T: int = 2000,
    n_modules: int = 4,
    r: float = 3.8,
    eps_high: float = 0.08,
    eps_low: float = 0.025,
    **kwargs
) -> Tuple[np.ndarray, Dict]:
    """
    Convenience: select eps according to regime name.
    'high_perm' -> stronger coupling (lower typical A)
    'low_perm'  -> weaker coupling
    """
    eps = eps_high if regime == "high_perm" else eps_low
    x, meta = generate_coupled_logistic(
        T=T, n_modules=n_modules, r=r, eps=eps, **kwargs
    )
    meta["regime"] = regime
    meta["eps"] = eps
    return x, meta
