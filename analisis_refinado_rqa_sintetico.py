#!/usr/bin/env python3
"""
analisis_refinado_rqa_sintetico.py

Versión del pipeline REFINADO + RQA adaptada para datos sintéticos controlados.

Permite generar sistemas dinámicos (principalmente mapa logístico acoplado)
con transiciones de régimen inyectadas conocidas, para validar si los picos
"hiperestructurales" (refinado + RQA) anticipan los cambios estructurales.

Uso:
    python analisis_refinado_rqa_sintetico.py

Salida:
    - Carpeta resultados_sintetico/
    - Figuras con prefijo sintetico_
    - CSV enriquecido con columnas RQA
    - Resumen en consola con leads a las transiciones inyectadas
"""

import os
import math
from collections import Counter
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d

# =============================================================================
# CONFIGURACIÓN FÁCIL (EDITAR AQUÍ)
# =============================================================================
CONFIG = {
    # Tipo de sistema sintético
    "system": "logistic_coupled",   # "logistic_coupled" (principal) o "lorenz"
    
    # Parámetros del generador
    "n_components": 4,              # Número de componentes / "regiones"
    "T": 1500,                      # Longitud de la serie
    "r": 3.8,                       # r más caótico para generar más variabilidad
    "coupling": 0.02,               # Acoplamiento base bajo
    
    # Inyecciones de transiciones conocidas (t, new_value, "coupling" o "r")
    "injections": [
        (380, 0.28, "coupling"),    # Aumento fuerte de acoplamiento (cambio estructural)
        (920, 0.015, "coupling"),   # Caída fuerte de acoplamiento
    ],
    
    # Semilla para reproducibilidad
    "seed": 42,
    
    # Parámetros RECD (igual que en el script real)
    "TAU_WINDOW": 85,
    "COH_WINDOW": 90,
    "PEAK_Q": 0.60,
    "PESO_GAMMA_WINDOW": 50,
    "STRUCTURAL_PERCENTILE": 94,
    "STRUCTURAL_MIN_DIST": 35,
    "PEAK_MIN_DIST": 18,
    "EMBEDDING_DIM": 3,
    
    # Refinamiento hiper-persistencia (base)
    "HYPER_PERSISTENCE_THRESHOLD": 1.0,
    "HYPER_RECENT_WINDOW": 20,
    
    # === CONFIG B (Equilibrio) para RQA ===
    "RQA_WINDOW": 25,
    "RQA_EPS_PERCENTILE": 10,
    "RQA_MIN_LINE_LENGTH": 2,
    "LAM_THRESHOLD": 0.80,
    "TT_THRESHOLD": 3.4,
    "LAM_ACCEL_THRESHOLD": 0.055,
    "TT_ACCEL_THRESHOLD": 0.38,
    
    # Pesos para el score estructural combinado
    "RQA_SCORE_LAM_W": 0.45,
    "RQA_SCORE_TT_W": 0.30,
    "RQA_SCORE_ACCEL_W": 0.25,
}

# Salida
OUTPUT_DIR = "resultados_sintetico"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 82)
print("ANÁLISIS REFINADO + RQA SOBRE DATOS SINTÉTICOS CONTROLADOS")
print(f"Sistema: {CONFIG['system']} | Componentes: {CONFIG['n_components']} | T={CONFIG['T']}")
print(f"RQA Config B: LAM>={CONFIG['LAM_THRESHOLD']}, TT>={CONFIG['TT_THRESHOLD']}")
print(f"Inyecciones de régimen: {len(CONFIG['injections'])} transiciones conocidas")
print("=" * 82)


# =============================================================================
# GENERADORES DE DATOS SINTÉTICOS
# =============================================================================

def generate_coupled_logistic(n_comp, T, r, coupling, seed=None, injections=None):
    """
    Genera series de un mapa logístico acoplado con acoplamiento variable.
    
    inyecciones: lista de tuplas (t, new_value, "coupling" o "r")
    Permite inyectar cambios de régimen en momentos conocidos (ground truth).
    """
    if seed is not None:
        np.random.seed(seed)
    
    X = np.zeros((T, n_comp))
    # Inicialización en régimen caótico típico
    X[0] = np.random.rand(n_comp) * 0.2 + 0.4
    
    current_c = coupling
    current_r = r
    change_times = []
    
    inj_dict = {}
    if injections:
        for t, val, typ in injections:
            inj_dict[t] = (val, typ)
    
    for t in range(T-1):
        if t in inj_dict:
            val, typ = inj_dict[t]
            if typ == "coupling":
                current_c = val
            elif typ == "r":
                current_r = val
            change_times.append(t)
            print(f"  [INYECCIÓN] t={t}: {typ} -> {val}")
        
        for i in range(n_comp):
            f_i = current_r * X[t, i] * (1 - X[t, i])
            
            f_coup = 0.0
            for j in range(n_comp):
                if j != i:
                    f_coup += current_r * X[t, j] * (1 - X[t, j])
            if n_comp > 1:
                f_coup /= (n_comp - 1)
            
            X[t+1, i] = (1 - current_c) * f_i + current_c * f_coup
    
    return X, change_times


def generate_lorenz(T=1500, dt=0.02, sigma=10.0, rho=28.0, beta=8/3, seed=None):
    """
    Generador opcional del atractor de Lorenz (3 componentes: x, y, z).
    Útil para probar en sistemas caóticos de dimensión superior.
    """
    if seed is not None:
        np.random.seed(seed)
    
    X = np.zeros((T, 3))
    X[0] = np.array([0.1, 0.0, 0.0]) + np.random.randn(3) * 0.01
    
    for t in range(T-1):
        x, y, z = X[t]
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        X[t+1] = X[t] + dt * np.array([dx, dy, dz])
    
    return X, []   # sin inyecciones por defecto (se pueden añadir manualmente)


def get_regions_data(system, config):
    """Genera los datos y los formatea como lista de 'regiones' para el pipeline."""
    if system == "logistic_coupled":
        X, inj_times = generate_coupled_logistic(
            n_comp=config["n_components"],
            T=config["T"],
            r=config["r"],
            coupling=config["coupling"],
            seed=config["seed"],
            injections=config["injections"]
        )
        regions_data = [X[:, i:i+1] for i in range(config["n_components"])]
        return regions_data, inj_times, X
    
    elif system == "lorenz":
        X, inj_times = generate_lorenz(T=config["T"], seed=config["seed"])
        regions_data = [X[:, i:i+1] for i in range(3)]
        return regions_data, inj_times, X
    
    else:
        raise ValueError(f"Sistema '{system}' no soportado.")


# =============================================================================
# FUNCIONES RECD (REUTILIZADAS DEL SCRIPT ANTERIOR)
# =============================================================================

def permutation_entropy(ts, dim=3, delay=1):
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


def compute_local_tau_s(series, k, window=None, dim=3):
    if window is None:
        window = CONFIG["TAU_WINDOW"]
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


def compute_all_metrics(regions_data, config):
    n_reg = len(regions_data)
    T = len(regions_data[0])
    
    s_reps = [compute_representative(rd) for rd in regions_data]
    
    tau_s = np.zeros((n_reg, T))
    for i in range(n_reg):
        for k in range(T):
            tau_s[i, k] = compute_local_tau_s(s_reps[i], k, window=config["TAU_WINDOW"], dim=config["EMBEDDING_DIM"])
    
    C = np.ones((n_reg, n_reg, T))
    for k in range(config["COH_WINDOW"], T):
        for i in range(n_reg):
            for j in range(i + 1, n_reg):
                si = s_reps[i][k - config["COH_WINDOW"] + 1 : k + 1]
                sj = s_reps[j][k - config["COH_WINDOW"] + 1 : k + 1]
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
            start = max(0, k - config["PESO_GAMMA_WINDOW"] + 1)
            win_tau = tau_s[i, start : k + 1]
            gamma[i, k] = max(0.0, tau_s[i, k] - np.median(win_tau)) + 1e-4
    
    I = peso * rho * gamma
    
    return {
        "tau_s": tau_s,
        "C": C,
        "rho": rho,
        "peso": peso,
        "gamma": gamma,
        "I": I,
        "s_reps": s_reps,
    }


# =============================================================================
# RQA RODANTE (Config B - REUTILIZADO)
# =============================================================================

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
        if len(iu[0]) > 0:
            eps = np.percentile(dist[iu], eps_percentile)
        else:
            eps = np.std(s) * 0.5 or 0.1
    
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


# =============================================================================
# DETECCIÓN REFINADA + RQA (LÓGICA IDÉNTICA)
# =============================================================================

def detect_strong_peaks_refined_rqa(metrics, rqa_measures, require_rqa=True):
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
                recent_tau = tau_s[i, start:k+1]
                hyper_level = (current_tau - np.mean(recent_tau)) / (np.std(recent_tau) + 1e-6)
                
                if hyper_level <= CONFIG["HYPER_PERSISTENCE_THRESHOLD"]:
                    continue
                
                if require_rqa:
                    lam_val = lam_series[i, k] if not np.isnan(lam_series[i, k]) else 0.0
                    tt_val = tt_series[i, k] if not np.isnan(tt_series[i, k]) else 0.0
                    lam_acc_val = lam_acc_series[i, k] if not np.isnan(lam_acc_series[i, k]) else 0.0
                    tt_acc_val = tt_acc_series[i, k] if not np.isnan(tt_acc_series[i, k]) else 0.0
                    
                    rqa_ok = (
                        (lam_val >= CONFIG["LAM_THRESHOLD"]) or
                        (tt_val >= CONFIG["TT_THRESHOLD"]) or
                        (lam_acc_val >= CONFIG["LAM_ACCEL_THRESHOLD"]) or
                        (tt_acc_val >= CONFIG["TT_ACCEL_THRESHOLD"])
                    )
                    if not rqa_ok:
                        continue
                
                raw.append((i, k))
    
    # Thinning
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


def run_statistical_test(leads_I, leads_other):
    leads_I = np.asarray(leads_I)
    all_other = np.concatenate([np.asarray(v) for v in leads_other.values()]) \
        if any(len(v) > 0 for v in leads_other.values()) else np.array([])
    
    if len(leads_I) < 3 or len(all_other) < 3:
        return {"n_I": len(leads_I), "n_other": len(all_other),
                "mean_I": float(np.mean(leads_I)) if len(leads_I) else np.nan,
                "mean_other": float(np.mean(all_other)) if len(all_other) else np.nan,
                "mw_p": 1.0, "perm_p": 1.0}
    
    _, mw_p = stats.mannwhitneyu(leads_I, all_other, alternative="greater")
    
    observed = np.mean(leads_I) - np.mean(all_other)
    combined = np.concatenate([leads_I, all_other])
    n_x = len(leads_I)
    rng = np.random.default_rng(42)
    count = sum((np.mean(rng.permutation(combined)[:n_x]) - np.mean(combined[n_x:])) >= observed
                for _ in range(5000))
    perm_p = (count + 1) / 5001
    
    return {
        "n_I": len(leads_I),
        "n_other": len(all_other),
        "mean_I": float(np.mean(leads_I)),
        "mean_other": float(np.mean(all_other)),
        "mw_p": float(mw_p),
        "perm_p": float(perm_p),
    }


# =============================================================================
# EXPORT Y FIGURAS (ADAPTADAS A SINTÉTICO)
# =============================================================================

def export_enriched_csv(metrics, structural_peaks, structural_changes,
                        rqa_measures, injected_times, output_dir):
    I = metrics["I"]
    peso = metrics["peso"]
    rho = metrics["rho"]
    gamma = metrics["gamma"]
    tau_s = metrics["tau_s"]
    C = metrics["C"]
    lam_s, tt_s, lam_acc_s, tt_acc_s = rqa_measures
    
    records = []
    ch = np.array(sorted(structural_changes))
    
    for reg_idx, k in structural_peaks:
        future = ch[ch > k]
        lead_to_detected = int(future[0] - k) if len(future) > 0 else -1
        
        # Lead a la siguiente inyección conocida
        inj_future = [inj for inj in injected_times if inj > k]
        lead_to_injection = int(inj_future[0] - k) if inj_future else -1
        
        current_tau = tau_s[reg_idx, k]
        recent = tau_s[reg_idx, max(0, k - CONFIG["HYPER_RECENT_WINDOW"]):k+1]
        hyper_level = (current_tau - np.mean(recent)) / (np.std(recent) + 1e-6)
        
        row_c = [abs(C[reg_idx, j, k]) for j in range(len(rqa_measures[0])) if j != reg_idx]
        avg_conn = np.mean(row_c) if row_c else 0.0
        
        lam_val = lam_s[reg_idx, k] if not np.isnan(lam_s[reg_idx, k]) else 0.0
        tt_val = tt_s[reg_idx, k] if not np.isnan(tt_s[reg_idx, k]) else 0.0
        lam_acc = lam_acc_s[reg_idx, k] if not np.isnan(lam_acc_s[reg_idx, k]) else 0.0
        tt_acc = tt_acc_s[reg_idx, k] if not np.isnan(tt_acc_s[reg_idx, k]) else 0.0
        
        score = (CONFIG["RQA_SCORE_LAM_W"] * min(1.0, lam_val / 0.8) +
                 CONFIG["RQA_SCORE_TT_W"] * min(1.0, tt_val / 4.0) +
                 CONFIG["RQA_SCORE_ACCEL_W"] * (max(0, lam_acc) / 0.1 + max(0, tt_acc) / 0.5) * 0.5)
        score = float(np.clip(score, 0.0, 1.0))
        
        records.append({
            "region": reg_idx,
            "k": k,
            "I_value": round(float(I[reg_idx, k]), 5),
            "Peso": round(float(peso[reg_idx, k]), 5),
            "rho": round(float(rho[reg_idx, k]), 5),
            "Gamma": round(float(gamma[reg_idx, k]), 5),
            "lead_to_next_detected_change": lead_to_detected,
            "lead_to_next_injected_change": lead_to_injection,
            "tau_s_at_peak": round(float(current_tau), 4),
            "hyper_persistence_level": round(float(hyper_level), 4),
            "avg_spatial_connectivity": round(float(avg_conn), 4),
            "laminarity_at_peak": round(lam_val, 4),
            "trapping_time_at_peak": round(tt_val, 4),
            "lam_acceleration": round(lam_acc, 4),
            "trap_acceleration": round(tt_acc, 4),
            "rqa_structural_score": round(score, 4),
            "is_structural_peak": True,
        })
    
    df = pd.DataFrame(records)
    out_path = os.path.join(output_dir, "picos_fuertes_refinados_rqa_sintetico.csv")
    df.to_csv(out_path, index=False)
    print(f"[EXPORT] CSV enriquecido: {out_path} ({len(df)} picos)")
    return df


def save_figures_synthetic(metrics, base_peaks, structural_peaks, structural_changes,
                           dist_smooth, dist_thresh, leads_struct, leads_other,
                           injected_times, lam_series, tt_series, output_dir):
    """Figuras adaptadas para datos sintéticos con marcas de inyecciones."""
    T = metrics["I"].shape[1]
    tau_s = metrics["tau_s"]
    I_mat = metrics["I"]
    n_reg = len(tau_s)
    prefix = "sintetico_"
    
    # Figura 1: τ_s + inyecciones
    fig, ax = plt.subplots(figsize=(11, 5))
    for i in range(n_reg):
        ax.plot(tau_s[i], label=f"Comp {i}", lw=1.3)
    for t in injected_times:
        ax.axvline(t, color="green", ls="--", alpha=0.7, label="Inyección de régimen" if t == injected_times[0] else "")
    ax.set_title("Figura 1: τ_s(k) - Mapa Logístico Acoplado Sintético\nLíneas verdes = cambios de régimen inyectados")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{prefix}fig1_tau_s.png"), bbox_inches="tight")
    plt.close()
    print(f"  [FIG] {prefix}fig1_tau_s.png")
    
    # Figura 2: I con picos diferenciados
    fig, ax = plt.subplots(figsize=(11, 5))
    for i in range(n_reg):
        ax.plot(I_mat[i], label=f"Comp {i}", lw=1.2, alpha=0.8)
    
    for reg, k in base_peaks:
        if (reg, k) not in structural_peaks:
            ax.scatter(k, I_mat[reg, k], marker="o", s=60, c="gray", zorder=6, alpha=0.6)
    
    for reg, k in structural_peaks:
        ax.scatter(k, I_mat[reg, k], marker="D", s=120, c="#d62728", zorder=8, edgecolors="white", lw=0.6)
    
    for t in injected_times:
        ax.axvline(t, color="green", ls="--", alpha=0.7)
    
    ax.set_title("Figura 2: I_i(k) Sintético\n○ = refinado base   ◆ = estructural (RQA)   |   Líneas verdes = inyecciones")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{prefix}fig2_I_intensity_rqa.png"), bbox_inches="tight")
    plt.close()
    print(f"  [FIG] {prefix}fig2_I_intensity_rqa.png")
    
    # Figura extra RQA
    fig, axes = plt.subplots(3, 1, figsize=(11, 7), sharex=True)
    for i in range(n_reg):
        axes[0].plot(tau_s[i], label=f"Comp {i}", lw=1.0)
    axes[0].set_ylabel("τ_s")
    axes[0].set_title("Evolución RQA sobre τ_s sintético (Config B)")
    
    for i in range(n_reg):
        axes[1].plot(lam_series[i], lw=1.0)
    axes[1].axhline(CONFIG["LAM_THRESHOLD"], color="red", ls="--", alpha=0.6)
    axes[1].set_ylabel("LAM")
    
    for i in range(n_reg):
        axes[2].plot(tt_series[i], lw=1.0)
    axes[2].axhline(CONFIG["TT_THRESHOLD"], color="red", ls="--", alpha=0.6)
    axes[2].set_ylabel("TT")
    axes[2].set_xlabel("Paso de tiempo")
    
    for t in injected_times:
        for axx in axes:
            axx.axvline(t, color="green", ls="--", alpha=0.5)
    
    for reg, k in structural_peaks:
        for axx in axes[1:]:
            axx.axvline(k, color="#d62728", alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{prefix}fig_extra_rqa.png"), bbox_inches="tight")
    plt.close()
    print(f"  [FIG] {prefix}fig_extra_rqa.png")


# =============================================================================
# MAIN
# =============================================================================

def main():
    # 1. Generar datos sintéticos
    print("\n[1] Generando datos sintéticos...")
    regions_data, injected_times, raw_X = get_regions_data(CONFIG["system"], CONFIG)
    
    # 2. Pipeline RECD + RQA (lógica idéntica)
    print("[2] Ejecutando pipeline RECD + RQA (Config B)...")
    metrics = compute_all_metrics(regions_data, CONFIG)
    tau_s = metrics["tau_s"]
    n_reg = tau_s.shape[0]
    
    # RQA rodante
    lam_s = np.zeros_like(tau_s)
    tt_s = np.zeros_like(tau_s)
    lam_acc_s = np.zeros_like(tau_s)
    tt_acc_s = np.zeros_like(tau_s)
    
    for i in range(n_reg):
        l, t, la, ta = compute_rolling_rqa(tau_s[i])
        lam_s[i] = l
        tt_s[i] = t
        lam_acc_s[i] = la
        tt_acc_s[i] = ta
    
    rqa_measures = (lam_s, tt_s, lam_acc_s, tt_acc_s)
    
    # Detección
    base_peaks = detect_strong_peaks_refined_rqa(metrics, rqa_measures, require_rqa=False)
    struct_peaks = detect_strong_peaks_refined_rqa(metrics, rqa_measures, require_rqa=True)
    
    struct_changes, dist_smooth, dist_thresh = detect_structural_changes(metrics["C"], 
                                                                         CONFIG["STRUCTURAL_PERCENTILE"],
                                                                         CONFIG["STRUCTURAL_MIN_DIST"])
    
    # Leads
    struct_times = [k for _, k in struct_peaks]
    leads_to_detected = compute_leads(struct_times, struct_changes)
    leads_to_injected = compute_leads(struct_times, injected_times)
    
    # 3. Figuras y export
    print("[3] Generando figuras y CSV...")
    save_figures_synthetic(metrics, base_peaks, struct_peaks, struct_changes,
                           dist_smooth, dist_thresh, leads_to_detected, {}, 
                           injected_times, lam_s, tt_s, OUTPUT_DIR)
    
    export_enriched_csv(metrics, struct_peaks, struct_changes, rqa_measures,
                        injected_times, OUTPUT_DIR)
    
    # 4. Resumen final
    print("\n" + "=" * 82)
    print("RESUMEN SINTÉTICO - DETECCIÓN DE PICOS HIPERESTRUCTURALES")
    print("=" * 82)
    print(f"Total componentes: {n_reg}")
    print(f"Transiciones de régimen inyectadas: {len(injected_times)} (t = {injected_times})")
    print(f"Picos refinados base (sin RQA): {len(base_peaks)}")
    print(f"Picos estructurales (refinado + RQA Config B): {len(struct_peaks)}")
    
    if leads_to_injected:
        mean_lead_inj = np.mean(leads_to_injected)
        print(f"\nAdelanto medio de picos estructurales a la SIGUIENTE transición inyectada:")
        print(f"  → {mean_lead_inj:.2f} pasos (n={len(leads_to_injected)})")
        if mean_lead_inj > 0:
            print("  ¡Los picos estructurales anticipan en promedio los cambios inyectados!")
    else:
        print("No se pudieron calcular leads a inyecciones (pocos eventos o sin solapamiento).")
    
    print(f"\nArchivos guardados en: {os.path.abspath(OUTPUT_DIR)}/")
    print("=" * 82)


if __name__ == "__main__":
    main()