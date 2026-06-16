#!/usr/bin/env python3
"""
analisis_refinado_rqa_lorenz_sin_inyecciones.py

Versión del pipeline REFINADO + RQA aplicado al **atractor de Lorenz**
**sin inyecciones de régimen**.

Usa las tres variables (x, y, z) como las tres "componentes/regiones".

Objetivo:
- Correr el sistema con rho=28.0 constante durante toda la trayectoria.
- Aplicar exactamente los mismos parámetros RECD y RQA Config B.
- Comparar el comportamiento de detección de picos (base y estructurales)
  con el caso que sí tenía inyecciones de rho.

Configuración idéntica al run con inyecciones excepto:
- "injections": []
- Salida en: resultados_sintetico_lorenz_sin_inyecciones/

El generador usa integración directa (sin piecewise) con rho fijo.
Todo el resto del pipeline (métricas, detección refinada + RQA, figuras, CSV)
es idéntico.
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
from scipy.integrate import odeint

# =============================================================================
# CONFIGURACIÓN - LORENZ SIN INYECCIONES
# =============================================================================
CONFIG = {
    # Sistema
    "system": "lorenz",
    "n_components": 3,              # x, y, z
    "T": 5000,
    "dt": 0.02,
    
    # Parámetros clásicos del atractor de Lorenz (sin cambios)
    "sigma": 10.0,
    "rho": 28.0,
    "beta": 8.0 / 3.0,
    
    # Sin inyecciones de régimen (rho constante durante todo el run)
    "injections": [],
    
    "seed": 42,
    
    # === PARÁMETROS RECD (exactamente los mismos) ===
    "TAU_WINDOW": 85,
    "COH_WINDOW": 90,
    "PEAK_Q": 0.60,
    "PESO_GAMMA_WINDOW": 50,
    "STRUCTURAL_PERCENTILE": 94,
    "STRUCTURAL_MIN_DIST": 35,
    "PEAK_MIN_DIST": 18,
    "EMBEDDING_DIM": 3,
    
    # Refinamiento hiper-persistencia
    "HYPER_PERSISTENCE_THRESHOLD": 1.0,
    "HYPER_RECENT_WINDOW": 20,
    
    # === RQA CONFIG B (Equilibrio) ===
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

OUTPUT_DIR = "resultados_sintetico_lorenz_sin_inyecciones"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 82)
print("ANÁLISIS REFINADO + RQA - ATRACTOR DE LORENZ (SIN INYECCIONES DE RÉGIMEN)")
print(f"Parámetros: sigma={CONFIG['sigma']}, rho={CONFIG['rho']}, beta={CONFIG['beta']:.4f}")
print(f"n_components={CONFIG['n_components']} (x,y,z) | T={CONFIG['T']} | dt={CONFIG['dt']}")
print(f"Inyecciones de rho: {CONFIG['injections']}  (rho constante durante todo el experimento)")
print(f"RQA Config B: LAM>={CONFIG['LAM_THRESHOLD']}, TT>={CONFIG['TT_THRESHOLD']}")
print("=" * 82)


# =============================================================================
# GENERADOR DE LORENZ (SIN INYECCIONES - RHO CONSTANTE)
# =============================================================================

def lorenz_deriv(state, t, sigma, rho, beta):
    """Ecuaciones del atractor de Lorenz."""
    x, y, z = state
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return [dx, dy, dz]


def generate_lorenz(T=None, dt=None, sigma=None, rho=None, beta=None, 
                    seed=None, injections=None):
    """
    Genera la trayectoria del atractor de Lorenz (x, y, z) con rho constante.
    
    Cuando injections=[] (o None), realiza integración directa sin cambios
    piecewise de parámetros.
    
    Devuelve:
        X: array (T, 3) con columnas [x, y, z]
        change_times: [] (sin inyecciones)
    """
    if T is None: T = CONFIG["T"]
    if dt is None: dt = CONFIG["dt"]
    if sigma is None: sigma = CONFIG["sigma"]
    if rho is None: rho = CONFIG["rho"]
    if beta is None: beta = CONFIG["beta"]
    
    if seed is not None:
        np.random.seed(seed)
    
    t = np.arange(0, T * dt, dt)
    
    # Condición inicial típica
    state0 = [1.0, 1.0, 1.0]
    
    # Sin inyecciones: integración directa con rho fijo (constante = 28.0)
    if not injections:
        print("  [SIN INYECCIONES] Integrando Lorenz con rho constante = 28.0 durante todo el run")
        X = odeint(lorenz_deriv, state0, t, args=(sigma, rho, beta))
        change_times = []
    else:
        # (Este branch no se usa en esta versión, pero se mantiene por compatibilidad)
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
            print(f"  [INYECCIÓN] t={inj_idx} (índice): rho cambiado a {new_rho}")
        
        t_piece = t[t >= current_t]
        if len(t_piece) > 1:
            sol = odeint(lorenz_deriv, current_state, t_piece, 
                         args=(sigma, current_rho, beta))
            pieces.append(sol)
        
        X = np.vstack(pieces)[:T]
    
    # Asegurar que X tenga exactamente T filas
    if len(X) > T:
        X = X[:T]
    elif len(X) < T:
        pad = np.tile(X[-1:], (T - len(X), 1))
        X = np.vstack([X, pad])
    
    print(f"  Trayectoria Lorenz generada: shape={X.shape} (rho constante)")
    return X, change_times


# =============================================================================
# FUNCIONES DEL PIPELINE (REUTILIZADAS - IDÉNTICAS)
# =============================================================================

def permutation_entropy(ts, dim=CONFIG["EMBEDDING_DIM"], delay=1):
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


def compute_local_tau_s(series, k, window=CONFIG["TAU_WINDOW"], dim=CONFIG["EMBEDDING_DIM"]):
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
# RQA (Config B) - IDÉNTICO
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


def compute_rqa_lam_tt(series_segment, eps=None, eps_percentile=CONFIG["RQA_EPS_PERCENTILE"], min_length=CONFIG["RQA_MIN_LINE_LENGTH"]):
    s = np.asarray(series_segment, dtype=float).ravel()
    n = len(s)
    if n < min_length + 1:
        return 0.0, 0.0, eps or 0.0
    
    dist = np.abs(s[:, None] - s[None, :])
    if eps is None:
        iu = np.triu_indices(n, k=1)
        eps = np.percentile(dist[iu], eps_percentile) if len(iu[0]) > 0 else np.std(s) * 0.5 or 0.1
    
    R = (dist <= eps).astype(int)
    v_lengths = _vertical_line_lengths(R, min_length)
    
    if not v_lengths:
        return 0.0, 0.0, eps
    
    n_v = sum(v_lengths)
    total_rp = max(np.sum(R) - n, 1)
    lam = n_v / total_rp
    tt = float(np.mean(v_lengths))
    return lam, tt, eps


def compute_rolling_rqa(tau_series, window=CONFIG["RQA_WINDOW"], eps_percentile=CONFIG["RQA_EPS_PERCENTILE"], min_length=CONFIG["RQA_MIN_LINE_LENGTH"]):
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
                recent_tau = tau_s[i, start : k + 1]
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


def detect_structural_changes(C, percentile=CONFIG["STRUCTURAL_PERCENTILE"], min_dist=CONFIG["STRUCTURAL_MIN_DIST"]):
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
    return {"n_I": len(leads_I), "n_other": len(all_other),
            "mean_I": float(np.mean(leads_I)),
            "mean_other": float(np.mean(all_other)),
            "mw_p": float(mw_p), "perm_p": float(perm_p)}


# =============================================================================
# EXPORT Y FIGURAS (ADAPTADAS SOLO PARA AUSENCIA DE INYECCIONES)
# =============================================================================

def export_enriched_csv(metrics, structural_peaks, structural_changes, rqa_measures, injected_times, output_dir):
    """Export idéntico; cuando no hay inyecciones, lead_to_next_injected_change será -1 para todos."""
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
        lead_detected = int(future[0] - k) if len(future) > 0 else -1
        
        inj_future = [inj for inj in injected_times if inj > k]
        lead_inj = int(inj_future[0] - k) if inj_future else -1
        
        current_tau = tau_s[reg_idx, k]
        recent = tau_s[reg_idx, max(0, k - CONFIG["HYPER_RECENT_WINDOW"]):k+1]
        hyper_level = (current_tau - np.mean(recent)) / (np.std(recent) + 1e-6)
        
        row_c = [abs(C[reg_idx, j, k]) for j in range(3) if j != reg_idx]
        avg_conn = np.mean(row_c) if row_c else 0.0
        
        lam_val = lam_s[reg_idx, k] if not np.isnan(lam_s[reg_idx, k]) else 0.0
        tt_val = tt_s[reg_idx, k] if not np.isnan(tt_s[reg_idx, k]) else 0.0
        lam_acc = lam_acc_s[reg_idx, k] if not np.isnan(lam_acc_s[reg_idx, k]) else 0.0
        tt_acc = tt_acc_s[reg_idx, k] if not np.isnan(tt_acc_s[reg_idx, k]) else 0.0
        
        score = (CONFIG["RQA_SCORE_LAM_W"] * min(1.0, lam_val / 0.8) +
                 CONFIG["RQA_SCORE_TT_W"] * min(1.0, tt_val / 4.0) +
                 CONFIG["RQA_SCORE_ACCEL_W"] * (max(0, lam_acc)/0.1 + max(0, tt_acc)/0.5)*0.5 )
        score = float(np.clip(score, 0., 1.))
        
        records.append({
            "region": reg_idx,
            "k": k,
            "I_value": round(float(I[reg_idx, k]), 5),
            "Peso": round(float(peso[reg_idx, k]), 5),
            "rho": round(float(rho[reg_idx, k]), 5),
            "Gamma": round(float(gamma[reg_idx, k]), 5),
            "lead_to_next_detected_change": lead_detected,
            "lead_to_next_injected_change": lead_inj,
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
    out_path = os.path.join(output_dir, "picos_fuertes_refinados_rqa_lorenz_sin_inyecciones.csv")
    df.to_csv(out_path, index=False)
    print(f"[EXPORT] CSV: {out_path} ({len(df)} picos)")
    return df


def save_figures(metrics, base_peaks, structural_peaks, struct_changes, dist_smooth, dist_thresh,
                 leads_struct, injected_times, lam_series, tt_series, output_dir):
    """Figuras con la misma lógica, pero sin líneas de inyección cuando no existen."""
    T = metrics["I"].shape[1]
    tau_s = metrics["tau_s"]
    I_mat = metrics["I"]
    n_reg = 3
    prefix = "lorenz_sin_inj_"
    has_inj = len(injected_times) > 0
    
    # Fig 1: tau_s (sin referencias a inyecciones)
    fig, ax = plt.subplots(figsize=(11, 5))
    labels = ["x", "y", "z"]
    for i in range(n_reg):
        ax.plot(tau_s[i], label=labels[i], lw=1.2)
    if has_inj:
        for t in injected_times:
            ax.axvline(t, color="green", ls="--", alpha=0.8, label="Cambio de rho (inyectado)" if t == injected_times[0] else "")
    ax.set_title("Figura 1: τ_s(k) - Atractor de Lorenz\n(rho = 28.0 constante durante todo el run - sin inyecciones)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{prefix}fig1_tau_s.png"), bbox_inches="tight")
    plt.close()
    print(f"  [FIG] {prefix}fig1_tau_s.png")
    
    # Fig 2: I con marcadores diferenciados (sin vlines de inyecciones)
    fig, ax = plt.subplots(figsize=(11, 5))
    for i in range(n_reg):
        ax.plot(I_mat[i], label=labels[i], lw=1.2, alpha=0.8)
    
    for reg, k in base_peaks:
        if (reg, k) not in structural_peaks:
            ax.scatter(k, I_mat[reg, k], marker="o", s=50, c="gray", zorder=6, alpha=0.6)
    
    for reg, k in structural_peaks:
        ax.scatter(k, I_mat[reg, k], marker="D", s=110, c="#d62728", zorder=8, edgecolors="white", lw=0.6)
    
    if has_inj:
        for t in injected_times:
            ax.axvline(t, color="green", ls="--", alpha=0.8)
    
    title2 = "Figura 2: I_i(k) Lorenz (refinado + RQA)\n○ base | ◆ estructural (RQA)"
    if has_inj:
        title2 += " | verde = inyecciones de rho"
    else:
        title2 += " | (sin inyecciones de rho - régimen constante)"
    ax.set_title(title2)
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{prefix}fig2_I_intensity_rqa.png"), bbox_inches="tight")
    plt.close()
    print(f"  [FIG] {prefix}fig2_I_intensity_rqa.png")
    
    # Fig extra RQA
    fig, axes = plt.subplots(3, 1, figsize=(11, 7), sharex=True)
    for i in range(n_reg):
        axes[0].plot(tau_s[i], label=labels[i], lw=1.0)
    axes[0].set_ylabel("τ_s")
    axes[0].set_title("Evolución RQA sobre τ_s (Lorenz, sin inyecciones) - Config B")
    axes[0].legend(fontsize=8)
    
    for i in range(n_reg):
        axes[1].plot(lam_series[i], lw=1.0)
    axes[1].axhline(CONFIG["LAM_THRESHOLD"], color="red", ls="--", alpha=0.6)
    axes[1].set_ylabel("LAM")
    
    for i in range(n_reg):
        axes[2].plot(tt_series[i], lw=1.0)
    axes[2].axhline(CONFIG["TT_THRESHOLD"], color="red", ls="--", alpha=0.6)
    axes[2].set_ylabel("TT")
    axes[2].set_xlabel("Tiempo (pasos)")
    
    if has_inj:
        for t in injected_times:
            for a in axes:
                a.axvline(t, color="green", ls="--", alpha=0.5)
    for reg, k in structural_peaks:
        for a in axes[1:]:
            a.axvline(k, color="#d62728", alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{prefix}fig_extra_rqa.png"), bbox_inches="tight")
    plt.close()
    print(f"  [FIG] {prefix}fig_extra_rqa.png")


# =============================================================================
# MAIN
# =============================================================================

def main():
    # 1. Generar datos Lorenz (sin inyecciones)
    print("\n[1] Generando trayectoria del atractor de Lorenz (sin inyecciones, rho=28 constante)...")
    X, injected_times = generate_lorenz(
        T=CONFIG["T"],
        dt=CONFIG["dt"],
        sigma=CONFIG["sigma"],
        rho=CONFIG["rho"],
        beta=CONFIG["beta"],
        seed=CONFIG["seed"],
        injections=CONFIG["injections"]
    )
    
    # Tratar x, y, z como las 3 componentes
    regions_data = [X[:, [i]] for i in range(3)]
    
    # 2. Pipeline completo (idéntico)
    print("[2] Ejecutando pipeline RECD + RQA (Config B)...")
    metrics = compute_all_metrics(regions_data)
    tau_s = metrics["tau_s"]
    
    # RQA rodante
    lam_s = np.zeros_like(tau_s)
    tt_s = np.zeros_like(tau_s)
    lam_acc_s = np.zeros_like(tau_s)
    tt_acc_s = np.zeros_like(tau_s)
    
    for i in range(3):
        l, t, la, ta = compute_rolling_rqa(tau_s[i])
        lam_s[i] = l
        tt_s[i] = t
        lam_acc_s[i] = la
        tt_acc_s[i] = ta
    
    rqa_measures = (lam_s, tt_s, lam_acc_s, tt_acc_s)
    
    # Detecciones
    base_peaks = detect_strong_peaks_refined_rqa(metrics, rqa_measures, require_rqa=False)
    struct_peaks = detect_strong_peaks_refined_rqa(metrics, rqa_measures, require_rqa=True)
    
    struct_changes, dist_smooth, dist_thresh = detect_structural_changes(metrics["C"])
    
    # Leads
    struct_k = [k for _, k in struct_peaks]
    leads_to_detected = compute_leads(struct_k, struct_changes)
    leads_to_inj = compute_leads(struct_k, injected_times)  # Será [] porque no hay inyecciones
    
    # 3. Figuras y export
    print("[3] Generando figuras y CSV...")
    save_figures(metrics, base_peaks, struct_peaks, struct_changes,
                 dist_smooth, dist_thresh, leads_to_detected, injected_times,
                 lam_s, tt_s, OUTPUT_DIR)
    
    export_enriched_csv(metrics, struct_peaks, struct_changes, rqa_measures,
                        injected_times, OUTPUT_DIR)
    
    # 4. Resumen final (adaptado para sin inyecciones + comparación)
    print("\n" + "=" * 82)
    print("RESUMEN FINAL - ATRACTOR DE LORENZ (REFINADO + RQA Config B) - SIN INYECCIONES")
    print("=" * 82)
    print(f"Componentes (x,y,z): 3")
    print(f"Parámetro rho: {CONFIG['rho']} (constante durante todo el run T=5000)")
    print(f"Transiciones de régimen inyectadas (cambio de rho): {len(injected_times)}")
    print(f"  Tiempos: {injected_times}")
    print(f"Picos refinados base (sin RQA): {len(base_peaks)}")
    print(f"Picos estructurales (refinado + RQA): {len(struct_peaks)}")
    
    print(f"\nCambios estructurales detectados por norma de Frobenius sobre matrices C:")
    if struct_changes:
        print(f"  → Sí, {len(struct_changes)} cambios detectados")
        print(f"     Tiempos (índices k): {struct_changes[:10]}{'...' if len(struct_changes)>10 else ''}")
    else:
        print("  → No se detectaron cambios estructurales significativos por Frobenius en este run.")
    
    if leads_to_inj:
        print(f"\nAdelanto medio de picos estructurales a SIGUIENTE inyección de rho:")
        print(f"  → {np.mean(leads_to_inj):.2f} pasos (n={len(leads_to_inj)})")
    else:
        print("\nAdelanto a inyecciones de rho: N/A (no se inyectaron transiciones en este run)")
    
    if leads_to_detected:
        print(f"Adelanto medio a cambios estructurales detectados (Frobenius):")
        print(f"  → {np.mean(leads_to_detected):.2f} pasos (n={len(leads_to_detected)})")
    
    # Comparación explícita con el run anterior que SÍ tenía inyecciones
    print("\n" + "-" * 82)
    print("COMPARACIÓN CON RUN ANTERIOR (CON INYECCIONES DE RÉGIMEN)")
    print("-" * 82)
    print("Run anterior (con inyecciones rho 28→35 en t=1500 y 35→24 en t=3200):")
    print("  - 123 picos estructurales (refinado + RQA)")
    print("  - Adelanto medio a la siguiente inyección de rho: 720.70 pasos (n=57)")
    print()
    print(f"Run actual (sin inyecciones, rho=28.0 constante todo el tiempo):")
    print(f"  - {len(struct_peaks)} picos estructurales (refinado + RQA)")
    print(f"  - Picos base refinados: {len(base_peaks)}")
    n_frob = len(struct_changes)
    print(f"  - Cambios estructurales por Frobenius: {n_frob} {'(detectados)' if n_frob > 0 else '(ninguno)'}")
    print("  - Leads a 'inyecciones' : todos -1 (no existen)")
    print()
    print("Observación: En ausencia de inyecciones explícitas de rho, el sistema")
    print("permanece en el régimen caótico clásico del atractor de Lorenz. El número")
    print("de picos 'hiperestructurales' y la presencia/ausencia de cambios detectados")
    print("por Frobenius dan información sobre la estabilidad estructural intrínseca")
    print("del atractor sin perturbaciones externas de parámetros.")
    print("-" * 82)
    
    print(f"\nArchivos guardados en: {os.path.abspath(OUTPUT_DIR)}/")
    print("=" * 82)


if __name__ == "__main__":
    main()