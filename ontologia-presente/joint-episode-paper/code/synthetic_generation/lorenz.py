"""
synthetic_generation/lorenz.py

4 coupled Lorenz oscillators with mean-field diffusive coupling on the x-variable.

Standard parameters: sigma=10, rho=28, beta=8/3.

Coupling form (diffusive on x):
  dx_i = sigma*(y_i - x_i) + eps_i * (mean_x - x_i)
  dy_i = x_i*(rho_i - z_i) - y_i
  dz_i = x_i*y_i - beta*z_i

Primary mechanism for Layer 3: structural perturbations that temporarily
reduce local coupling eps (and optionally rho) on 1-2 oscillators for
contiguous blocks of samples. This directly alters interaction structure.

The returned observable is the x-component of each oscillator (shape T, n_modules),
which is the standard choice for permutation-entropy / recurrence studies.
This preserves full compatibility with the rest of the Joint Episode pipeline
(metrics, detection, labeling).

Meta includes "structural_perturbation_intervals" exactly as in the logistic generator.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.seeding import get_rng


def _lorenz_deriv(state: np.ndarray, eps: np.ndarray, rho: np.ndarray,
                  sigma: float, beta: float) -> np.ndarray:
    """
    state: (N, 3) current [x, y, z] for N oscillators
    eps, rho: (N,) effective parameters for this instant
    Returns dstate/dt : (N, 3)
    """
    x = state[:, 0]
    y = state[:, 1]
    z = state[:, 2]
    mean_x = np.mean(x)

    dx = sigma * (y - x) + eps * (mean_x - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return np.stack([dx, dy, dz], axis=1)


def _rk4_step(state: np.ndarray, eps: np.ndarray, rho: np.ndarray,
              sigma: float, beta: float, dt: float) -> np.ndarray:
    """One RK4 step."""
    k1 = _lorenz_deriv(state, eps, rho, sigma, beta)
    k2 = _lorenz_deriv(state + 0.5 * dt * k1, eps, rho, sigma, beta)
    k3 = _lorenz_deriv(state + 0.5 * dt * k2, eps, rho, sigma, beta)
    k4 = _lorenz_deriv(state + dt * k3, eps, rho, sigma, beta)
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)


def generate_coupled_lorenz(
    T: int = 2000,
    n_modules: int = 4,
    sigma: float = 10.0,
    rho: float = 28.0,
    beta: float = 8.0 / 3.0,
    eps: float = 0.1,
    dt: float = 0.02,
    substeps: int = 10,
    noise: float = 0.001,
    seed: Optional[int] = None,
    # State noise / kicks (kept very low)
    injection_prob: float = 0.002,
    injection_magnitude: float = 0.3,
    use_injections: bool = False,
    # PRIMARY: structural coupling (and rho) perturbations
    structural_perturbation_prob: float = 0.012,
    perturbation_duration_min: int = 60,
    perturbation_duration_max: int = 100,
    eps_pert_min: float = 0.0,
    eps_pert_max: float = 0.15,   # strong reduction of coupling
    use_structural_perturbations: bool = True,
    # Optional simultaneous local rho perturbation (analogous to previous r_pert)
    use_rho_perturbation: bool = True,
    rho_pert_factor_min: float = 0.70,
    rho_pert_factor_max: float = 0.92,
) -> Tuple[np.ndarray, Dict]:
    """
    Generate T samples from N coupled Lorenz oscillators.

    Returns:
        x: (T, n_modules)  -- the x-component of each oscillator (the observable)
        meta: dict with structural_perturbation_intervals etc. (same contract as logistic)
    """
    rng = get_rng(seed) if seed is not None else np.random.default_rng()

    # State: (N, 3)
    state = np.zeros((n_modules, 3))
    # Initial conditions near the attractor (rough)
    state[:, 0] = rng.uniform(-10, 10, n_modules)   # x
    state[:, 1] = rng.uniform(-15, 15, n_modules)   # y
    state[:, 2] = rng.uniform(10, 30, n_modules)    # z

    structural_intervals: List[Tuple[int, int, List[int]]] = []

    # Pre-sample structural events in *sample* time (discrete k)
    pert_events: List[Tuple[int, int, float, float, List[int]]] = []
    if use_structural_perturbations and structural_perturbation_prob > 0:
        k = 0
        while k < T - perturbation_duration_max - 1:
            if rng.random() < structural_perturbation_prob:
                dur = int(rng.integers(perturbation_duration_min, perturbation_duration_max + 1))
                n_mods = int(rng.integers(1, 3))
                mods = rng.choice(n_modules, size=n_mods, replace=False).tolist()
                eps_factor = float(rng.uniform(eps_pert_min, eps_pert_max))
                rho_factor = 1.0
                if use_rho_perturbation:
                    rho_factor = float(rng.uniform(rho_pert_factor_min, rho_pert_factor_max))
                start_k = k + 1
                pert_events.append((start_k, dur, eps_factor, rho_factor, mods))
                structural_intervals.append((start_k, start_k + dur, mods))
                k += dur
            else:
                k += 1

    # Build per-sample schedules (T, N)
    eps_schedule = np.full((T, n_modules), eps, dtype=float)
    rho_schedule = np.full((T, n_modules), rho, dtype=float)
    for start_k, dur, ef, rf, mods in pert_events:
        end_k = min(T, start_k + dur)
        for m in mods:
            eps_schedule[start_k:end_k, m] = eps * ef
            if use_rho_perturbation:
                rho_schedule[start_k:end_k, m] = rho * rf

    # Burn-in (continuous time)
    burn_steps = 2000
    for _ in range(burn_steps):
        eff_eps = np.full(n_modules, eps)
        eff_rho = np.full(n_modules, rho)
        state = _rk4_step(state, eff_eps, eff_rho, sigma, beta, dt)

    # Main recording loop (discrete samples)
    x_out = np.zeros((T, n_modules))
    injection_times: List[int] = []

    micro_dt = dt / max(1, substeps)

    for k in range(T):
        # current effective params for this sample
        eff_eps = eps_schedule[k]
        eff_rho = rho_schedule[k]

        # Advance substeps
        for _ in range(substeps):
            state = _rk4_step(state, eff_eps, eff_rho, sigma, beta, micro_dt)

        # Record x component
        x_out[k] = state[:, 0].copy()

        # Very occasional small kicks (optional, disabled by default)
        if use_injections and rng.random() < injection_prob:
            n_shock = rng.integers(1, 3)
            mods = rng.choice(n_modules, size=n_shock, replace=False)
            for m in mods:
                kick = rng.uniform(0.5, 1.5) * injection_magnitude * (1 if rng.random() > 0.5 else -1)
                state[m, 0] += kick
            injection_times.append(k)

        # Light observation noise
        if noise > 0:
            x_out[k] += rng.normal(0, noise, n_modules)

    meta = {
        "T": T,
        "n_modules": n_modules,
        "sigma": sigma,
        "rho": rho,
        "beta": beta,
        "eps": eps,
        "dt": dt,
        "substeps": substeps,
        "noise": noise,
        "injection_times": np.array(injection_times),
        "use_injections": use_injections,
        "structural_perturbation_intervals": structural_intervals,
        "n_structural_perts": len(structural_intervals),
        "use_structural_perturbations": use_structural_perturbations,
        "use_rho_perturbation": use_rho_perturbation,
        "seed": seed,
    }
    return x_out, meta


def generate_regime_series(
    regime: str = "high_perm",
    T: int = 2000,
    n_modules: int = 4,
    eps_high: float = 0.18,
    eps_low: float = 0.04,
    **kwargs
) -> Tuple[np.ndarray, Dict]:
    """
    Convenience wrapper matching the logistic API.
    'high_perm' -> stronger coupling (lower typical A)
    'low_perm'  -> weaker coupling
    """
    eps = eps_high if regime == "high_perm" else eps_low
    x, meta = generate_coupled_lorenz(
        T=T, n_modules=n_modules, eps=eps, **kwargs
    )
    meta["regime"] = regime
    meta["eps"] = eps
    return x, meta
