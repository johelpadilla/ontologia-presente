"""
synthetic_generation/logistic.py
4-component coupled logistic map with controlled structural change injections.

Standard diffusive coupling form (mean-field):
  x_i(t+1) = (1-eps_i) * r * x_i(t)*(1-x_i(t)) + eps_i * coupled_mean

Injections now have two components:
- Reduced-weight state shocks (additive kicks) for continuity.
- PRIMARY: structural coupling perturbations (temporary local reduction of eps for 1-2 modules
  over a block of steps). This directly alters interaction structure and is more likely
  to produce detectable Layer 3 signatures in A(k) and correlations.
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
    # State shocks (kept for backward/continuity but down-weighted)
    injection_prob: float = 0.004,
    injection_magnitude: float = 0.12,
    use_injections: bool = True,
    # PRIMARY structural injections: temporary local coupling (eps) perturbations
    structural_perturbation_prob: float = 0.013,
    perturbation_duration_min: int = 70,
    perturbation_duration_max: int = 110,
    eps_pert_min: float = 0.0,
    eps_pert_max: float = 0.88,
    use_structural_perturbations: bool = True,
    # Optional local r perturbation during same structural blocks (stronger effect)
    use_r_perturbation: bool = True,
    r_pert_factor_min: float = 0.88,
    r_pert_factor_max: float = 0.95,
) -> Tuple[np.ndarray, Dict]:
    """
    Generate multivariate time series from coupled logistic map.
    Returns x of shape (T, N), and metadata dict with injection_times,
    structural_perturbation_intervals (list of (start, end, modules)), params.

    Structural perturbations (PRIMARY L3 mechanism v0.3+):
    - Temporary local reduction of coupling eps (factor 0 to eps_pert_max~0.88) for selected modules.
    - Optional simultaneous local reduction of r (r_local = r * [0.88-0.95]) on same modules/blocks
      to induce stronger, more detectable shifts in local dynamics and subsequent A(k).
    - Longer blocks (70-110) + slightly higher prob to ensure more events and impact.
    - State shocks kept very low weight.

    This is designed to produce clear, consistent positive ΔA post-pert (target mean > +0.03).
    """
    rng = get_rng(seed) if seed is not None else np.random.default_rng()

    x = np.zeros((T, n_modules))
    x[0] = rng.uniform(0.1, 0.9, size=n_modules)

    injection_times: List[int] = []
    structural_intervals: List[Tuple[int, int, List[int]]] = []

    # Pre-sample structural coupling perturbation events (PRIMARY L3 mechanism)
    # Each: (start_time, duration, eps_factor, r_factor, list_of_modules)
    pert_events: List[Tuple[int, int, float, float, List[int]]] = []
    if use_structural_perturbations and structural_perturbation_prob > 0:
        t = 0
        while t < T - perturbation_duration_max - 1:
            if rng.random() < structural_perturbation_prob:
                dur = int(rng.integers(perturbation_duration_min, perturbation_duration_max + 1))
                n_mods = int(rng.integers(1, 3))  # 1-2 modules; can bias to 2 if needed
                mods = rng.choice(n_modules, size=n_mods, replace=False).tolist()
                eps_factor = float(rng.uniform(eps_pert_min, eps_pert_max))
                r_factor = 1.0
                if use_r_perturbation:
                    r_factor = float(rng.uniform(r_pert_factor_min, r_pert_factor_max))
                start_t = t + 1
                pert_events.append((start_t, dur, eps_factor, r_factor, mods))
                structural_intervals.append((start_t, start_t + dur, mods))
                t += dur  # space events
            else:
                t += 1

    # Build per-t schedules (T, N) - default nominal, override during perts
    eps_schedule = np.full((T, n_modules), eps, dtype=float)
    r_schedule = np.full((T, n_modules), r, dtype=float)
    for start_t, dur, eps_factor, r_factor, mods in pert_events:
        end_t = min(T, start_t + dur)
        for m in mods:
            eps_schedule[start_t:end_t, m] = eps * eps_factor
            if use_r_perturbation:
                r_schedule[start_t:end_t, m] = r * r_factor

    for t in range(T - 1):
        xt = x[t]
        mean_coupled = np.mean(xt)
        for i in range(n_modules):
            # use time/module-specific r and eps during perturbation windows
            ri = r_schedule[t, i]
            epsi = eps_schedule[t, i]
            local = ri * xt[i] * (1 - xt[i])
            coupled = ri * mean_coupled * (1 - mean_coupled)
            x[t+1, i] = (1 - epsi) * local + epsi * coupled
            # small additive noise
            x[t+1, i] += rng.normal(0, noise)

        # Reduced-weight state shocks (additive kicks) - secondary
        if use_injections and rng.random() < injection_prob:
            n_shock = rng.integers(1, 3)
            mods = rng.choice(n_modules, size=n_shock, replace=False)
            for m in mods:
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
        "structural_perturbation_intervals": structural_intervals,
        "n_structural_perts": len(structural_intervals),
        "use_structural_perturbations": use_structural_perturbations,
        "use_r_perturbation": use_r_perturbation,
        "n_r_perts": len([e for e in pert_events if e[3] < 0.999]) if use_r_perturbation else 0,
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
