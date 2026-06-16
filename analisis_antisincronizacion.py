#!/usr/bin/env python3
"""
analisis_antisincronizacion.py

Análisis de antisincronización en experimentos sintéticos controlados
usando como proxy la desviación estándar de τ_s entre componentes.

Sistemas analizados:
  1. Mapa logístico acoplado (r=3.8) con inyecciones de acoplamiento
     (baseline del test de ruido: 121 picos estructurales)
  2. Atractor de Lorenz con inyecciones de rho
     (123 picos estructurales)

Proxy de antisincronización:
  - Para cada tiempo k: antisinc[k] = std( τ_s[componentes, k] )
  - Mayor desviación estándar = mayor antisincronización (menor sincronía global)

Pipeline (idéntico al usado para generar los picos):
  - RECD (TAU_WINDOW=85, EMBEDDING_DIM=3)
  - Hiper-persistencia > 1.0
  - RQA Config B
  - Detección refinada de picos estructurales (require_rqa=True)

Análisis por sistema:
  - Serie temporal completa de antisincronización
  - Media en ventanas ±50 alrededor de cada pico estructural vs baseline (resto de la serie)
  - Media en 100 pasos previos a cada pico
  - Dirección del cambio (sube/baja cerca de picos)
  - Correlación (Spearman) entre nivel de antisincronización en el pico y el adelanto (lead) a inyecciones
  - Test Mann-Whitney sobre distribuciones de medias de ventana (picos vs controles aleatorios)

Salida:
  resultados_antisincronizacion/
    - resumen_antisincronizacion.csv (tabla comparativa)
    - fig*_antisinc_*.png (timelines, boxplots, scatter lead vs anti, comparación)
    - antisinc_series_*.csv (series completas por sistema, opcional)

Ejecución:
    python3 analisis_antisincronizacion.py
"""

import os
import math
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d
from scipy.integrate import odeint

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Parámetros comunes del pipeline RECD + RQA Config B (idénticos en ambos experimentos)
COMMON = {
    "TAU_WINDOW": 85,
    "COH_WINDOW": 90,
    "PEAK_Q": 0.60,
    "PESO_GAMMA_WINDOW": 50,
    "STRUCTURAL_PERCENTILE": 94,
    "STRUCTURAL_MIN_DIST": 35,
    "PEAK_MIN_DIST": 18,
    "EMBEDDING_DIM": 3,

    # Hiper-persistencia
    "HYPER_PERSISTENCE_THRESHOLD": 1.0,
    "HYPER_RECENT_WINDOW": 20,

    # RQA Config B
    "RQA_WINDOW": 25,
    "RQA_EPS_PERCENTILE": 10,
    "RQA_MIN_LINE_LENGTH": 2,
    "LAM_THRESHOLD": 0.80,
    "TT_THRESHOLD": 3.4,
    "LAM_ACCEL_THRESHOLD": 0.055,
    "TT_ACCEL_THRESHOLD": 0.38,

    "RQA_SCORE_LAM_W": 0.45,
    "RQA_SCORE_TT_W": 0.30,
    "RQA_SCORE_ACCEL_W": 0.25,
}

# Generador y metadatos - MAPA LOGÍSTICO r=3.8 (el que produjo 121 picos estructurales)
LOGISTIC = {
    "system": "logistic",
    "r": 3.8,
    "coupling": 0.02,
    "n_components": 4,
    "T": 4000,
    "injections": [
        (380, 0.28, "coupling"),   # aumento fuerte de acoplamiento
        (920, 0.015, "coupling"),  # caída fuerte de acoplamiento
    ],
    "seed": 42,
}

# Generador y metadatos - ATRACTOR DE LORENZ (el que produjo 123 picos estructurales)
LORENZ = {
    "system": "lorenz",
    "n_components": 3,           # x, y, z
    "T": 5000,
    "dt": 0.02,
    "sigma": 10.0,
    "rho": 28.0,
    "beta": 8.0 / 3.0,
    "injections": [
        (1500, 35.0),   # aumento de rho
        (3200, 24.0),   # disminución de rho
    ],
    "seed": 42,
}

OUTPUT_DIR = "resultados_antisincronizacion"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# CONFIG para las funciones del pipeline (valores idénticos para ambos sistemas)
CONFIG = COMMON.copy()

sns.set_theme(style="whitegrid", rc={"figure.dpi": 110, "savefig.dpi": 140})


# =============================================================================
# GENERADORES DE DATOS SINTÉTICOS
# =============================================================================

def generate_coupled_logistic(n_comp, T, r, coupling, seed=None, injections=None):
    """Genera el mapa logístico acoplado con inyecciones (copia fiel del experimento exitoso)."""
    if seed is not None:
        np.random.seed(seed)

    X = np.zeros((T, n_comp))
    X[0] = np.random.rand(n_comp) * 0.2 + 0.4

    current_c = coupling
    current_r = r
    change_times = []

    inj_dict = {}
    if injections:
        for t, val, typ in injections:
            inj_dict[t] = (val, typ)

    for t in range(T - 1):
        if t in inj_dict:
            val, typ = inj_dict[t]
            if typ == "coupling":
                current_c = val
            elif typ == "r":
                current_r = val
            change_times.append(t)

        for i in range(n_comp):
            f_i = current_r * X[t, i] * (1 - X[t, i])
            f_coup = 0.0
            for j in range(n_comp):
                if j != i:
                    f_coup += current_r * X[t, j] * (1 - X[t, j])
            if n_comp > 1:
                f_coup /= (n_comp - 1)
            X[t + 1, i] = (1 - current_c) * f_i + current_c * f_coup

    return X, change_times


def lorenz_deriv(state, t, sigma, rho, beta):
    """Ecuaciones diferenciales del atractor de Lorenz."""
    x, y, z = state
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return [dx, dy, dz]


def generate_lorenz(T=None, dt=None, sigma=None, rho=None, beta=None,
                    seed=None, injections=None):
    """
    Genera trayectoria del atractor de Lorenz (x,y,z) con inyecciones de rho.
    (copia fiel del experimento que produjo 123 picos estructurales)
    """
    if T is None: T = LORENZ["T"]
    if dt is None: dt = LORENZ["dt"]
    if sigma is None: sigma = LORENZ["sigma"]
    if rho is None: rho = LORENZ["rho"]
    if beta is None: beta = LORENZ["beta"]

    if seed is not None:
        np.random.seed(seed)

    t = np.arange(0, T * dt, dt)
    state0 = [1.0, 1.0, 1.0]

    if not injections:
        X = odeint(lorenz_deriv, state0, t, args=(sigma, rho, beta))
        change_times = []
    else:
        inj_list = sorted(injections)
        change_times = [inj[0] for inj in inj_list]

        pieces = []
        current_state = state0
        current_t = 0.0
        current_rho = rho

        for inj_idx, new_rho in inj_list:
            t_end = inj_idx * dt
            t_piece = t[(t >= current_t) & (t < t_end)]
            if len(t_piece) > 1:
                sol = odeint(lorenz_deriv, current_state, t_piece,
                             args=(sigma, current_rho, beta))
                pieces.append(sol[:-1])
                current_state = sol[-1]
            current_rho = new_rho
            current_t = t_end

        # último segmento
        t_piece = t[t >= current_t]
        if len(t_piece) > 1:
            sol = odeint(lorenz_deriv, current_state, t_piece,
                         args=(sigma, current_rho, beta))
            pieces.append(sol)

        X = np.vstack(pieces)[:T]
        if len(X) > T:
            X = X[:T]
        elif len(X) < T:
            pad = np.tile(X[-1:], (T - len(X), 1))
            X = np.vstack([X, pad])

    if len(X) > T:
        X = X[:T]
    return X, change_times


# =============================================================================
# PIPELINE RECD + RQA CONFIG B (código reutilizado exacto)
# =============================================================================

def permutation_entropy(ts, dim=None, delay=1):
    if dim is None:
        dim = CONFIG["EMBEDDING_DIM"]
    ts = np.asarray(ts, dtype=float)
    n = len(ts) - (dim - 1) * delay
    if n < 2:
        return np.log(math.factorial(dim))
    idx = np.array([np.arange(i, i + dim * delay, delay) for i in range(n)])
    embeddings = ts[idx]
    perms = np.argsort(embeddings, axis=1)
    perm_tuples = [tuple(p) for p in perms]
    counts = Counter(perm_tuples)
    freqs = np.array(list(counts.values()), dtype=float) / n
    pe = -np.sum(freqs * np.log(freqs + 1e-12))
    return pe


def compute_local_tau_s(series, k, window=None, dim=None):
    if window is None:
        window = CONFIG["TAU_WINDOW"]
    if dim is None:
        dim = CONFIG["EMBEDDING_DIM"]
    start = max(0, k - window + 1)
    win = series[start : k + 1]
    if len(win) < dim + 3:
        return 4.0
    pe = permutation_entropy(win, dim=dim, delay=1)
    max_pe = np.log(math.factorial(dim))
    disorder = np.clip(pe / max_pe, 0.0, 1.0)
    return float(3.0 + 19.0 * (1.0 - disorder) ** 1.6)


def compute_representative(region_data):
    return np.mean(region_data, axis=1)


def compute_all_metrics(regions_data):
    """Calcula tau_s, C, rho, peso, gamma, I para todas las componentes."""
    n_reg = len(regions_data)
    T = len(regions_data[0])
    s_reps = [compute_representative(rd) for rd in regions_data]

    tau_s = np.zeros((n_reg, T))
    for i in range(n_reg):
        for k in range(T):
            tau_s[i, k] = compute_local_tau_s(s_reps[i], k)

    C = np.ones((n_reg, n_reg, T))
    for k in range(CONFIG["COH_WINDOW"], T):
        for i in range(n_reg):
            for j in range(i + 1, n_reg):
                si = s_reps[i][k - CONFIG["COH_WINDOW"] + 1 : k + 1]
                sj = s_reps[j][k - CONFIG["COH_WINDOW"] + 1 : k + 1]
                corr = np.corrcoef(si, sj)[0, 1]
                C[i, j, k] = C[j, i, k] = corr

    rho = np.zeros((n_reg, T))
    for k in range(T):
        for i in range(n_reg):
            others = [abs(C[i, j, k]) for j in range(n_reg) if j != i]
            rho[i, k] = np.mean(others) if others else 0.0

    peso = np.zeros((n_reg, T))
    gamma = np.zeros((n_reg, T))
    for i in range(n_reg):
        for k in range(T):
            peso[i, k] = tau_s[i, k]
            start = max(0, k - CONFIG["PESO_GAMMA_WINDOW"] + 1)
            win_tau = tau_s[i, start : k + 1]
            gamma[i, k] = max(0.0, tau_s[i, k] - np.median(win_tau)) + 1e-4

    I = peso * rho * gamma
    return {"tau_s": tau_s, "C": C, "rho": rho, "peso": peso,
            "gamma": gamma, "I": I, "s_reps": s_reps}


def _vertical_line_lengths(R, min_length=2):
    n = R.shape[0]
    lengths = []
    for j in range(n):
        col = R[:, j].astype(int)
        padded = np.concatenate(([0], col, [0]))
        diffs = np.diff(padded)
        starts = np.where(diffs == 1)[0]
        ends = np.where(diffs == -1)[0]
        for s, e in zip(starts, ends):
            L = e - s
            if L >= min_length:
                lengths.append(L)
    return lengths


def compute_rqa_lam_tt(series_segment, eps=None, eps_percentile=None, min_length=2):
    if eps_percentile is None:
        eps_percentile = CONFIG["RQA_EPS_PERCENTILE"]
    s = np.asarray(series_segment, dtype=float).ravel()
    n = len(s)
    if n < min_length + 1:
        return 0.0, 0.0, eps or 0.0
    dist = np.abs(s[:, None] - s[None, :])
    if eps is None:
        iu = np.triu_indices(n, k=1)
        eps = np.percentile(dist[iu], eps_percentile) if len(iu[0]) > 0 else (np.std(s) * 0.5 or 0.1)
    R = (dist <= eps).astype(int)
    v_lengths = _vertical_line_lengths(R, min_length)
    if not v_lengths:
        return 0.0, 0.0, eps
    n_v = sum(v_lengths)
    total_rp = max(np.sum(R) - n, 1)
    lam = n_v / total_rp
    tt = float(np.mean(v_lengths))
    return lam, tt, eps


def compute_rolling_rqa(tau_series, window=None, eps_percentile=None, min_length=2):
    if window is None:
        window = CONFIG["RQA_WINDOW"]
    if eps_percentile is None:
        eps_percentile = CONFIG["RQA_EPS_PERCENTILE"]
    n = len(tau_series)
    lam_arr = np.full(n, np.nan)
    tt_arr = np.full(n, np.nan)
    for i in range(window - 1, n):
        seg = tau_series[max(0, i - window + 1):i + 1]
        l, t, _ = compute_rqa_lam_tt(seg, eps_percentile=eps_percentile, min_length=min_length)
        lam_arr[i] = l
        tt_arr[i] = t
    lam_acc = np.full(n, 0.0)
    tt_acc = np.full(n, 0.0)
    for i in range(5, n):
        prev_lam = np.nanmean(lam_arr[max(0, i-5):i])
        prev_tt = np.nanmean(tt_arr[max(0, i-5):i])
        if not np.isnan(lam_arr[i]) and not np.isnan(prev_lam):
            lam_acc[i] = lam_arr[i] - prev_lam
        if not np.isnan(tt_arr[i]) and not np.isnan(prev_tt):
            tt_acc[i] = tt_arr[i] - prev_tt
    return lam_arr, tt_arr, lam_acc, tt_acc


def detect_strong_peaks_refined_rqa(metrics, rqa_measures, require_rqa=True):
    """Detección refinada + RQA (Config B) - idéntica a la usada para 121/123 picos."""
    I = metrics["I"]
    peso = metrics["peso"]
    rho = metrics["rho"]
    gamma = metrics["gamma"]
    tau_s = metrics["tau_s"]
    n_reg, T = I.shape
    lam_series, tt_series, lam_acc_series, tt_acc_series = rqa_measures

    raw = []
    for i in range(n_reg):
        p_th = np.percentile(peso[i], CONFIG["PEAK_Q"] * 100)
        r_th = np.percentile(rho[i], CONFIG["PEAK_Q"] * 100)
        g_th = np.percentile(gamma[i], CONFIG["PEAK_Q"] * 100)
        i_th = np.percentile(I[i], 75)

        for k in range(20, T - 10):
            if (peso[i, k] > p_th and rho[i, k] > r_th and
                    gamma[i, k] > g_th and I[i, k] > i_th):
                current_tau = tau_s[i, k]
                start = max(0, k - CONFIG["HYPER_RECENT_WINDOW"])
                recent_tau = tau_s[i, start : k + 1]
                hyper_level = (current_tau - np.mean(recent_tau)) / (np.std(recent_tau) + 1e-6)
                if hyper_level <= CONFIG["HYPER_PERSISTENCE_THRESHOLD"]:
                    continue
                if require_rqa:
                    lam_val = lam_series[i, k] if not np.isnan(lam_series[i, k]) else 0.0
                    tt_val = tt_series[i, k] if not np.isnan(tt_series[i, k]) else 0.0
                    lam_acc_val = lam_acc_series[i, k] if not np.isnan(lam_acc_series[i, k]) else 0.0
                    tt_acc_val = tt_acc_series[i, k] if not np.isnan(tt_acc_series[i, k]) else 0.0
                    rqa_ok = ((lam_val >= CONFIG["LAM_THRESHOLD"]) or
                              (tt_val >= CONFIG["TT_THRESHOLD"]) or
                              (lam_acc_val >= CONFIG["LAM_ACCEL_THRESHOLD"]) or
                              (tt_acc_val >= CONFIG["TT_ACCEL_THRESHOLD"]))
                    if not rqa_ok:
                        continue
                raw.append((i, k))

    by_reg = {}
    for reg, k in raw:
        by_reg.setdefault(reg, []).append(k)

    thinned = []
    for reg in sorted(by_reg.keys()):
        times = np.array(sorted(set(by_reg[reg])))
        if len(times) == 0:
            continue
        sel = [times[0]]
        for tt in times[1:]:
            if tt - sel[-1] >= CONFIG["PEAK_MIN_DIST"]:
                sel.append(tt)
        thinned.extend([(reg, int(t)) for t in sel])
    return thinned


def detect_structural_changes(C, percentile=None, min_dist=None):
    if percentile is None:
        percentile = CONFIG["STRUCTURAL_PERCENTILE"]
    if min_dist is None:
        min_dist = CONFIG["STRUCTURAL_MIN_DIST"]
    T = C.shape[2]
    dist = np.zeros(T)
    for k in range(1, T):
        dist[k] = np.linalg.norm(C[:, :, k] - C[:, :, k - 1], "fro")
    dist_smooth = uniform_filter1d(dist, size=7, mode="nearest")
    thresh = np.percentile(dist_smooth[80:], percentile)
    peaks, _ = find_peaks(dist_smooth, height=thresh, distance=min_dist)
    return peaks.tolist(), dist_smooth, thresh


def compute_leads(event_times, change_times):
    leads = []
    ch = np.array(sorted(change_times))
    for et in sorted(event_times):
        future = ch[ch > et]
        if len(future) > 0:
            leads.append(int(future[0] - et))
    return leads


# =============================================================================
# ANÁLISIS DE ANTISINCRONIZACIÓN
# =============================================================================

def compute_antisync_series(tau_s):
    """Proxy de antisincronización: desviación estándar de τ_s entre componentes en cada instante."""
    return np.std(tau_s, axis=0, ddof=0)


def get_structural_peak_times(struct_peaks):
    """Lista de tiempos k de picos estructurales (mantiene duplicados si ocurren, ordenada)."""
    return sorted([int(k) for _, k in struct_peaks])


def analyze_antisynchronization(anti, peak_times, injected_times, T, system_label):
    """
    Calcula todas las métricas de antisincronización alrededor de picos estructurales.
    Devuelve dict con estadísticas + datos para figuras.
    """
    peak_times = [int(k) for k in peak_times if 0 <= k < len(anti)]
    n_peaks = len(peak_times)

    global_mean = float(np.nanmean(anti))
    global_std = float(np.nanstd(anti))

    peak_window_means = []
    pre_100_means = []
    anti_at_peak = []
    leads = []

    for pk in peak_times:
        # Ventana ±50
        lo = max(0, pk - 50)
        hi = min(T, pk + 50)
        wmean = float(np.nanmean(anti[lo:hi]))
        peak_window_means.append(wmean)

        # 100 pasos previos
        lo_pre = max(0, pk - 100)
        pmean = float(np.nanmean(anti[lo_pre:pk])) if pk > lo_pre else float(anti[pk])
        pre_100_means.append(pmean)

        anti_at_peak.append(float(anti[pk]))

        # Lead a siguiente inyección
        future = [t for t in injected_times if t > pk]
        lead = int(future[0] - pk) if future else -1
        leads.append(lead)

    mean_at_win = float(np.mean(peak_window_means)) if peak_window_means else np.nan
    mean_pre = float(np.mean(pre_100_means)) if pre_100_means else np.nan
    mean_at = float(np.mean(anti_at_peak)) if anti_at_peak else np.nan

    # Baseline: todos los tiempos fuera de las ventanas ±50 de picos
    is_near = np.zeros(len(anti), dtype=bool)
    for pk in peak_times:
        lo = max(0, pk - 50)
        hi = min(T, pk + 50)
        is_near[lo:hi] = True
    baseline_vals = anti[~is_near]
    mean_baseline = float(np.nanmean(baseline_vals)) if len(baseline_vals) > 0 else global_mean

    diff = mean_at_win - mean_baseline
    if diff > 0.0005:
        direction = "SUBE cerca de picos"
    elif diff < -0.0005:
        direction = "BAJA cerca de picos"
    else:
        direction = "sin cambio apreciable"

    # Correlación con lead (solo picos con lead válido)
    valid_idx = [i for i, l in enumerate(leads) if l >= 0]
    corr, corr_p = np.nan, np.nan
    if len(valid_idx) >= 3:
        a_vals = np.asarray([anti_at_peak[i] for i in valid_idx])
        l_vals = np.asarray([leads[i] for i in valid_idx])
        corr, corr_p = stats.spearmanr(a_vals, l_vals)

    # Distribución de control: medias de ventanas de 101 pasos en posiciones aleatorias
    rng = np.random.default_rng(42)
    n_ctrl = max(300, n_peaks * 3)
    control_means = []
    for _ in range(n_ctrl):
        c = rng.integers(120, T - 120)
        lo = max(0, c - 50)
        hi = min(T, c + 50)
        control_means.append(float(np.nanmean(anti[lo:hi])))

    # Mann-Whitney entre las medias de ventana de picos vs control
    try:
        _, mw_p = stats.mannwhitneyu(peak_window_means, control_means, alternative="two-sided")
    except Exception:
        mw_p = np.nan

    return {
        "n_peaks": n_peaks,
        "mean_anti_global": round(global_mean, 5),
        "mean_anti_baseline": round(mean_baseline, 5),
        "mean_anti_at_peaks_pm50": round(mean_at_win, 5),
        "mean_anti_pre100": round(mean_pre, 5),
        "delta_at_vs_baseline": round(diff, 5),
        "direction": direction,
        "n_valid_leads": len(valid_idx),
        "corr_anti_lead_spearman": None if np.isnan(corr) else round(float(corr), 5),
        "corr_p": None if np.isnan(corr_p) else round(float(corr_p), 5),
        "mw_p_peakwin_vs_control": None if np.isnan(mw_p) else round(float(mw_p), 5),
        # datos para figuras y export
        "peak_window_means": peak_window_means,
        "control_window_means": control_means[:len(peak_window_means) * 2],
        "anti_series": anti,
        "peak_times": peak_times,
        "leads": leads,
        "anti_at_peak": anti_at_peak,
        "injected_times": injected_times,
    }


# =============================================================================
# FIGURAS
# =============================================================================

def plot_timeline(anti, peak_times, injected_times, title, outpath, inj_label="Inyección"):
    fig, ax = plt.subplots(figsize=(13, 4.8))
    t = np.arange(len(anti))
    ax.plot(t, anti, lw=0.95, color="#1f77b4", alpha=0.9, label="Antisincronización (std τ_s)")

    if peak_times:
        pts = np.asarray(peak_times)
        ax.scatter(pts, anti[pts], marker="D", s=38, c="#d62728", zorder=6,
                   alpha=0.85, edgecolors="white", linewidths=0.4, label="Picos estructurales (D)")

    for t0 in injected_times:
        ax.axvline(t0, color="green", ls="--", lw=1.6, alpha=0.75)

    ax.set_xlabel("Paso de tiempo (k)")
    ax.set_ylabel("Antisincronización (std(τ_s entre componentes))")
    ax.set_title(title, fontsize=12)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.95)
    plt.tight_layout()
    plt.savefig(outpath, bbox_inches="tight")
    plt.close()
    print(f"  [FIG] {os.path.basename(outpath)}")


def plot_box_and_violin(res, title, outpath):
    """Box + strip de medias de ventana en picos vs controles aleatorios."""
    peak_m = res["peak_window_means"]
    ctrl_m = res["control_window_means"]
    df = pd.DataFrame({
        "media_antisinc": peak_m + ctrl_m,
        "grupo": (["Cerca de picos (±50)"] * len(peak_m)) +
                 (["Control (ventanas aleatorias)"] * len(ctrl_m))
    })

    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    sns.boxplot(data=df, x="grupo", y="media_antisinc", ax=ax, hue="grupo",
                palette={"Cerca de picos (±50)": "#d62728", "Control (ventanas aleatorias)": "#2ca02c"},
                width=0.55, legend=False)
    sns.stripplot(data=df, x="grupo", y="media_antisinc", ax=ax,
                  color="black", alpha=0.25, size=2.5, jitter=0.25)

    ax.set_ylabel("Media de antisincronización en ventana de 101 pasos")
    ax.set_xlabel("")
    ax.set_title(title, fontsize=11)
    plt.xticks(rotation=8)
    plt.tight_layout()
    plt.savefig(outpath, bbox_inches="tight")
    plt.close()
    print(f"  [FIG] {os.path.basename(outpath)}")


def plot_lead_vs_anti(res, title, outpath):
    """Scatter lead vs antisincronización en el pico (solo leads válidos)."""
    leads = np.asarray(res["leads"])
    antis = np.asarray(res["anti_at_peak"])
    mask = leads >= 0
    if mask.sum() < 3:
        print(f"  [FIG skip] {os.path.basename(outpath)} (pocos leads válidos)")
        return

    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    ax.scatter(antis[mask], leads[mask], c="#1f77b4", s=48, alpha=0.75,
               edgecolors="white", linewidths=0.4, zorder=5)

    # línea de tendencia
    try:
        from scipy.stats import linregress
        lr = linregress(antis[mask], leads[mask])
        xs = np.linspace(antis[mask].min(), antis[mask].max(), 60)
        ax.plot(xs, lr.intercept + lr.slope * xs, "r--", lw=1.8, alpha=0.75,
                label=f"tendencia (r={lr.rvalue:.2f})")
        ax.legend(fontsize=8)
    except Exception:
        pass

    ax.set_xlabel("Antisincronización en el pico (std τ_s)")
    ax.set_ylabel("Adelanto a siguiente inyección (pasos)")
    ax.set_title(title, fontsize=11)
    plt.tight_layout()
    plt.savefig(outpath, bbox_inches="tight")
    plt.close()
    print(f"  [FIG] {os.path.basename(outpath)}")


def plot_comparative_bars(results, outpath):
    """Barras comparativas baseline vs picos para los dos sistemas."""
    systems = ["Logistic r=3.8\n(121 picos)", "Lorenz\n(123 picos)"]
    base = [results["logistic"]["mean_anti_baseline"], results["lorenz"]["mean_anti_baseline"]]
    peak = [results["logistic"]["mean_anti_at_peaks_pm50"], results["lorenz"]["mean_anti_at_peaks_pm50"]]

    x = np.arange(len(systems))
    w = 0.36

    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    b1 = ax.bar(x - w/2, base, w, label="Baseline (resto de la serie)", color="#2ca02c", alpha=0.85)
    b2 = ax.bar(x + w/2, peak, w, label="Cerca de picos estructurales (±50)", color="#d62728", alpha=0.85)

    ax.set_ylabel("Media de antisincronización (std τ_s)")
    ax.set_title("Antisincronización cerca de picos hiperestructurales vs baseline\nComparación entre sistemas sintéticos")
    ax.set_xticks(x)
    ax.set_xticklabels(systems, fontsize=9)
    ax.legend(loc="upper right")

    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.0008, f"{h:.4f}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    # anotar deltas
    for i, (bb, pp) in enumerate(zip(base, peak)):
        d = pp - bb
        ax.text(i, max(bb, pp) + 0.004, f"Δ={d:+.4f}", ha="center", fontsize=8, color="#333")

    plt.tight_layout()
    plt.savefig(outpath, bbox_inches="tight")
    plt.close()
    print(f"  [FIG] {os.path.basename(outpath)}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 88)
    print("ANÁLISIS DE ANTISINCRONIZACIÓN (proxy: std de τ_s entre componentes)")
    print("Mapa logístico acoplado r=3.8  |  Atractor de Lorenz (inyecciones de rho)")
    print("Usa exactamente los parámetros y pipeline que produjeron 121 y 123 picos estructurales.")
    print("=" * 88)

    results = {}

    for sys_name, gen in [("logistic", LOGISTIC), ("lorenz", LORENZ)]:
        print(f"\n>>> Sistema: {sys_name.upper()}")
        print("-" * 60)

        # 1. Generar datos (limpios, baseline)
        if sys_name == "logistic":
            X, inj_times = generate_coupled_logistic(
                n_comp=gen["n_components"], T=gen["T"], r=gen["r"],
                coupling=gen["coupling"], seed=gen["seed"], injections=gen["injections"]
            )
        else:
            X, inj_times = generate_lorenz(
                T=gen["T"], dt=gen["dt"], sigma=gen["sigma"], rho=gen["rho"],
                beta=gen["beta"], seed=gen["seed"], injections=gen["injections"]
            )

        regions = [X[:, [i]] for i in range(gen["n_components"])]
        print(f"  Datos: shape={X.shape}, inyecciones en t={inj_times}")

        # 2. RECD completo → τ_s
        metrics = compute_all_metrics(regions)
        tau_s = metrics["tau_s"]
        anti = compute_antisync_series(tau_s)
        print(f"  τ_s calculada: shape={tau_s.shape}, antisincronización global media = {np.mean(anti):.5f}")

        # 3. RQA + detección de picos estructurales (require_rqa=True)
        n_reg = tau_s.shape[0]
        lam_s = np.zeros_like(tau_s)
        tt_s = np.zeros_like(tau_s)
        lam_a = np.zeros_like(tau_s)
        tt_a = np.zeros_like(tau_s)
        for i in range(n_reg):
            l, t, la, ta = compute_rolling_rqa(tau_s[i])
            lam_s[i], tt_s[i], lam_a[i], tt_a[i] = l, t, la, ta
        rqa_measures = (lam_s, tt_s, lam_a, tt_a)

        struct_peaks = detect_strong_peaks_refined_rqa(metrics, rqa_measures, require_rqa=True)
        peak_ks = get_structural_peak_times(struct_peaks)
        print(f"  Picos estructurales detectados: {len(struct_peaks)} (k únicos: {len(set(peak_ks))})")

        # 4. Análisis de antisincronización
        res = analyze_antisynchronization(anti, peak_ks, inj_times, gen["T"], sys_name)
        results[sys_name] = res

        # Guardar serie completa de antisincronización
        ser_df = pd.DataFrame({
            "k": np.arange(len(anti)),
            "antisincronizacion_std_tau_s": anti
        })
        ser_df.to_csv(os.path.join(OUTPUT_DIR, f"antisinc_series_{sys_name}.csv"), index=False)

        # Resumen rápido por sistema
        print(f"  Antisinc. baseline: {res['mean_anti_baseline']:.5f} | "
              f"en ±50 de picos: {res['mean_anti_at_peaks_pm50']:.5f} | "
              f"delta={res['delta_at_vs_baseline']:+.5f} ({res['direction']})")

    # =============================================================================
    # TABLA COMPARATIVA
    # =============================================================================
    print("\n" + "=" * 95)
    print("TABLA COMPARATIVA - ANTISINCRONIZACIÓN Y PICOS HIPERESTRUCTURALES")
    print("=" * 95)

    table_rows = []
    for name in ["logistic", "lorenz"]:
        r = results[name]
        table_rows.append({
            "sistema": name,
            "n_picos_estructurales": r["n_peaks"],
            "anti_global": r["mean_anti_global"],
            "anti_baseline": r["mean_anti_baseline"],
            "anti_picos_pm50": r["mean_anti_at_peaks_pm50"],
            "anti_pre100": r["mean_anti_pre100"],
            "delta_pico_vs_baseline": r["delta_at_vs_baseline"],
            "tendencia": r["direction"],
            "n_leads_validos": r["n_valid_leads"],
            "corr_spearman_anti_lead": r["corr_anti_lead_spearman"],
            "p_corr": r["corr_p"],
            "mw_p_picos_vs_ctrl": r["mw_p_peakwin_vs_control"],
        })

    df = pd.DataFrame(table_rows)
    print(df.to_string(index=False))
    csv_path = os.path.join(OUTPUT_DIR, "resumen_antisincronizacion.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nCSV resumen guardado: {csv_path}")

    # =============================================================================
    # FIGURAS
    # =============================================================================
    print("\n[Generando figuras...]")
    out = OUTPUT_DIR

    # Logistic
    plot_timeline(
        results["logistic"]["anti_series"],
        results["logistic"]["peak_times"],
        results["logistic"]["injected_times"],
        "Antisincronización (std τ_s) — Mapa Logístico acoplado r=3.8\nD = picos estructurales (refinado + RQA Config B)  |  líneas verdes = inyecciones de acoplamiento",
        os.path.join(out, "fig1_antisinc_logistic_timeline.png")
    )
    plot_box_and_violin(
        results["logistic"],
        "Antisincronización en ventanas alrededor de picos estructurales vs control\nMapa Logístico r=3.8 (121 picos)",
        os.path.join(out, "fig2_antisinc_logistic_box.png")
    )
    plot_lead_vs_anti(
        results["logistic"],
        "Nivel de antisincronización vs adelanto a inyecciones (picos estructurales)\nLogístico r=3.8",
        os.path.join(out, "fig3_antisinc_logistic_lead_vs_anti.png")
    )

    # Lorenz
    plot_timeline(
        results["lorenz"]["anti_series"],
        results["lorenz"]["peak_times"],
        results["lorenz"]["injected_times"],
        "Antisincronización (std τ_s) — Atractor de Lorenz (x,y,z)\nD = picos estructurales (refinado + RQA Config B)  |  líneas verdes = inyecciones de ρ",
        os.path.join(out, "fig4_antisinc_lorenz_timeline.png")
    )
    plot_box_and_violin(
        results["lorenz"],
        "Antisincronización en ventanas alrededor de picos estructurales vs control\nAtractor de Lorenz (123 picos)",
        os.path.join(out, "fig5_antisinc_lorenz_box.png")
    )
    plot_lead_vs_anti(
        results["lorenz"],
        "Nivel de antisincronización vs adelanto a inyecciones (picos estructurales)\nLorenz",
        os.path.join(out, "fig6_antisinc_lorenz_lead_vs_anti.png")
    )

    # Comparativa combinada
    plot_comparative_bars(results, os.path.join(out, "fig7_antisinc_comparacion_bars.png"))

    # =============================================================================
    # INTERPRETACIÓN FINAL
    # =============================================================================
    print("\n" + "=" * 95)
    print("INTERPRETACIÓN — ¿EXISTE RELACIÓN ENTRE ANTISINCRONIZACIÓN Y PICOS HIPERESTRUCTURALES?")
    print("=" * 95)

    for name in ["logistic", "lorenz"]:
        r = results[name]
        print(f"\n{name.upper()} (r=3.8 / Lorenz):")
        print(f"  • {r['n_peaks']} picos estructurales analizados.")
        print(f"  • Antisincronización media global: {r['mean_anti_global']}")
        print(f"  • Media en baseline (tiempos no cercanos a picos): {r['mean_anti_baseline']}")
        print(f"  • Media en ventanas ±50 alrededor de picos: {r['mean_anti_at_peaks_pm50']}  "
              f"(Δ = {r['delta_at_vs_baseline']:+.5f})")
        print(f"  • Tendencia: {r['direction']}")
        print(f"  • Media en los 100 pasos previos a cada pico: {r['mean_anti_pre100']}")
        if r["corr_anti_lead_spearman"] is not None:
            print(f"  • Correlación (Spearman) antisincronización-en-pico vs adelanto: "
                  f"ρ = {r['corr_anti_lead_spearman']} (p={r['corr_p']})")
        if r["mw_p_peakwin_vs_control"] is not None:
            sig = "SIGNIFICATIVA (p<0.05)" if r["mw_p_peakwin_vs_control"] < 0.05 else "no significativa"
            print(f"  • Test Mann-Whitney (medias de ventana picos vs controles aleatorios): "
                  f"p = {r['mw_p_peakwin_vs_control']} → {sig}")

    print("""
CONCLUSIÓN GENERAL:

El proxy de antisincronización (desviación estándar de τ_s entre los componentes en cada instante)
mide el grado de DIVERSIDAD / DESACOPLAMIENTO de las escalas de persistencia local entre las
"regiones" o variables del sistema.

- Si la antisincronización SUBE significativamente cerca de los picos hiperestructurales (detectados
  con I + hiper-persistencia > 1.0 + RQA Config B), indica que estos picos tienden a ocurrir en
  momentos de mayor DIVERSIDAD entre componentes. Esto puede reflejar una "tensión" o reorganización
  interna que precede o acompaña a la transición de régimen inyectada (cambio de acoplamiento o de ρ).

- Si BAJA (el sistema se vuelve más sincrónico globalmente), los picos estructurales coincidirían
  con estados de mayor coherencia colectiva.

- La comparación "pre-100" ayuda a distinguir si la antisincronización es un PRECURSOR (sube antes)
  o un fenómeno CONCOMITANTE / posterior.

- La correlación con el lead (adelanto) revela si niveles más altos de antisincronización en el
  momento del pico se asocian con mejor capacidad de anticipación a las transiciones conocidas.

DIFERENCIAS ENTRE SISTEMAS:
  El mapa logístico acoplado (sistema discreto con acoplamiento explícito controlado) y el atractor
  de Lorenz (flujo continuo 3D con cambios de parámetro ρ) pueden exhibir patrones distintos de
  (anti)sincronización porque su topología de acoplamiento y la naturaleza de las transiciones
  inyectadas son fundamentalmente diferentes. El análisis cuantitativo anterior permite compararlos
  directamente bajo el mismo marco RECD + RQA.

Archivos guardados en: {0}
""".format(os.path.abspath(OUTPUT_DIR)))

    print("✅ Análisis de antisincronización completado.")
    print(f"   Resultados en: {os.path.abspath(OUTPUT_DIR)}/")


if __name__ == "__main__":
    main()
