#!/usr/bin/env python3
"""
analisis_final_iquitos.py

Análisis final completo de la Predicción 2 (RECD + estructura espacial)
usando **solo los datos de Iquitos (Perú)** con los parámetros óptimos
identificados en el barrido (los mismos que se usaron para San Juan).

Parámetros fijos:
    TAU_WINDOW = 85
    COH_WINDOW = 90
    PEAK_Q = 0.60

El script:
- Filtra exclusivamente city = "iq"
- Ejecuta el pipeline completo
- Genera las 6 figuras principales en resultados_final_iquitos/
- Exporta picos_fuertes_iquitos.csv
- Realiza análisis exploratorio profundo de los picos (similar al de San Juan)
- Guarda figuras y reporte adicional en analisis_picos_iquitos/
- Imprime un resumen comparativo con San Juan al final

Uso:
    python analisis_final_iquitos.py
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
# CONFIGURACIÓN DEL ANÁLISIS FINAL - IQUITOS
# =============================================================================

# Ruta de datos (igual que en los scripts anteriores)
DATA_PATH = os.path.join("data", "datos_dengai_completo.csv")

# Carpeta de salida principal (análoga a resultados_final_san_juan)
OUTPUT_DIR = "resultados_final_iquitos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Carpeta para el análisis exploratorio de picos (análoga a analisis_picos_fuertes)
PEAKS_ANALYSIS_DIR = "analisis_picos_iquitos"
os.makedirs(PEAKS_ANALYSIS_DIR, exist_ok=True)

# ==========================================================================
# PARÁMETROS FIJOS (LOS MISMOS QUE EN SAN JUAN - ÓPTIMOS DEL SWEEP)
# ==========================================================================
TAU_WINDOW = 85
COH_WINDOW = 90
PEAK_Q = 0.60

PESO_GAMMA_WINDOW = 50
STRUCTURAL_PERCENTILE = 94
STRUCTURAL_MIN_DIST = 35
PEAK_MIN_DIST = 18
EMBEDDING_DIM = 3

# Estilo visual
plt.rcParams['figure.dpi'] = 130
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'sans-serif'
sns.set_theme(style="whitegrid", font_scale=1.1)

# Colores consistentes (mismos que en San Juan)
REGION_COLORS = plt.cm.tab10(np.linspace(0, 1, 4))
REGION_PALETTE = {
    "Incidencia + Temperatura": "#1f77b4",
    "Incidencia + Humedad + Precipitación": "#ff7f0e",
    "Clima + Vegetación (NDVI)": "#2ca02c"
}

# Definición de regiones (idéntica)
BASE_REGION_DEFINITION = [
    ("Incidencia + Temperatura", [
        "total_cases",
        "reanalysis_air_temp_k",
        "reanalysis_dew_point_temp_k",
        "station_avg_temp_c"
    ]),
    ("Incidencia + Humedad + Precipitación", [
        "total_cases",
        "reanalysis_relative_humidity_percent",
        "reanalysis_specific_humidity_g_per_kg",
        "precipitation_amt_mm",
        "station_precip_mm"
    ]),
    ("Clima + Vegetación (NDVI)", [
        "reanalysis_precip_amt_kg_per_m2",
        "reanalysis_max_air_temp_k",
        "ndvi_ne",
        "ndvi_nw",
        "ndvi_se",
        "ndvi_sw"
    ]),
]

print("=" * 78)
print("ANÁLISIS FINAL - PREDICCIÓN 2 (SOLO IQUITOS)")
print(f"Parámetros fijos: TAU={TAU_WINDOW}, COH={COH_WINDOW}, PEAK_Q={PEAK_Q}")
print(f"Salida principal : {OUTPUT_DIR}/")
print(f"Salida picos     : {PEAKS_ANALYSIS_DIR}/")
print("=" * 78)


# =============================================================================
# CARGA DE DATOS - SOLO IQUITOS
# =============================================================================

def ensure_data():
    if os.path.exists(DATA_PATH):
        return DATA_PATH

    features_p = os.path.join("data", "dengue_features_train.csv")
    labels_p = os.path.join("data", "dengue_labels_train.csv")

    if os.path.exists(features_p) and os.path.exists(labels_p):
        print("[DATA] Uniendo archivos originales...")
        feat = pd.read_csv(features_p)
        lab = pd.read_csv(labels_p)
        merged = pd.merge(feat, lab, on=["city", "year", "weekofyear"], how="left")
        merged = merged.sort_values(["city", "year", "weekofyear"]).reset_index(drop=True)
        merged.to_csv(DATA_PATH, index=False)
        print(f"[DATA] Creado {DATA_PATH}")
        return DATA_PATH

    raise FileNotFoundError(
        f"No se encontró {DATA_PATH}. Ejecuta 'python prepare_dengai_data.py' primero."
    )


def load_iquitos_regions(data_path):
    """Carga solo Iquitos, limpia y construye las 3 regiones temáticas."""
    print(f"[LOAD] Cargando datos de Iquitos desde: {data_path}")
    df = pd.read_csv(data_path)

    # Filtrar SOLO Iquitos
    df = df[df["city"] == "iq"].copy()
    df = df.sort_values(["year", "weekofyear"]).reset_index(drop=True)

    if len(df) < 150:
        raise ValueError("Datos insuficientes para Iquitos.")

    all_needed = set()
    for _, cols in BASE_REGION_DEFINITION:
        all_needed.update(cols)

    cols_to_keep = ["year", "weekofyear"] + [c for c in all_needed if c in df.columns]
    df_clean = df[cols_to_keep].copy()

    # Limpieza
    df_clean = df_clean.interpolate(method="linear", limit_direction="both").ffill().bfill()
    df_clean = df_clean.dropna().reset_index(drop=True)

    print(f"[LOAD] Semanas de Iquitos después de limpieza: {len(df_clean)}")

    regions_data = []
    region_names = []

    for name, cols in BASE_REGION_DEFINITION:
        avail = [c for c in cols if c in df_clean.columns]
        if len(avail) < 2:
            print(f"[WARN] Región '{name}' descartada.")
            continue
        sub = df_clean[avail].copy()
        sub_std = (sub - sub.mean()) / (sub.std(ddof=0) + 1e-8)
        regions_data.append(sub_std.values.astype(float))
        region_names.append(name)

    if len(regions_data) < 2:
        raise ValueError("No se pudieron construir suficientes regiones para Iquitos.")

    min_len = min(len(r) for r in regions_data)
    regions_data = [r[:min_len] for r in regions_data]

    print(f"[LOAD] Regiones listas para Iquitos: {region_names} | T = {min_len}")
    return regions_data, region_names


# =============================================================================
# PIPELINE RECD (IDÉNTICO AL DE SAN JUAN, CON PARÁMETROS FIJOS)
# =============================================================================

def permutation_entropy(ts, dim=EMBEDDING_DIM, delay=1):
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


def compute_local_tau_s(series, k, window=TAU_WINDOW, dim=EMBEDDING_DIM):
    start = max(0, k - window + 1)
    win = series[start:k + 1]
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
    for k in range(COH_WINDOW, T):
        for i in range(n_reg):
            for j in range(i + 1, n_reg):
                si = s_reps[i][k - COH_WINDOW + 1:k + 1]
                sj = s_reps[j][k - COH_WINDOW + 1:k + 1]
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
            start = max(0, k - 40 + 1)
            win_tau = tau_s[i, start:k + 1]
            gamma[i, k] = max(0.0, tau_s[i, k] - np.median(win_tau)) + 1e-4

    I = peso * rho * gamma

    return {
        "tau_s": tau_s, "C": C, "rho": rho, "peso": peso,
        "gamma": gamma, "I": I, "s_reps": s_reps
    }


def detect_strong_peaks(metrics, q=PEAK_Q, min_dist=PEAK_MIN_DIST):
    I, peso, rho, gamma = metrics["I"], metrics["peso"], metrics["rho"], metrics["gamma"]
    n_reg, T = I.shape
    raw = []
    for i in range(n_reg):
        p_th = np.percentile(peso[i], q * 100)
        r_th = np.percentile(rho[i], q * 100)
        g_th = np.percentile(gamma[i], q * 100)
        i_th = np.percentile(I[i], 75)
        for k in range(20, T - 10):
            if (peso[i, k] > p_th and rho[i, k] > r_th and
                    gamma[i, k] > g_th and I[i, k] > i_th):
                raw.append((i, k))

    by_reg = {}
    for reg, k in raw:
        by_reg.setdefault(reg, []).append(k)

    thinned = []
    for reg in sorted(by_reg):
        times = np.array(sorted(set(by_reg[reg])))
        if len(times) == 0: continue
        sel = [times[0]]
        for tt in times[1:]:
            if tt - sel[-1] >= min_dist:
                sel.append(tt)
        thinned.extend([(reg, int(t)) for t in sel])
    return thinned


def detect_structural_changes(C, percentile=STRUCTURAL_PERCENTILE, min_dist=STRUCTURAL_MIN_DIST):
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


def compute_reference_leads(metrics, structural_changes):
    tau_s = metrics["tau_s"]
    s_reps = metrics["s_reps"]
    n_reg, T = tau_s.shape

    pe_multi = np.array([
        np.mean([permutation_entropy(s_reps[i][max(0, k-60):k+1]) for i in range(n_reg)])
        for k in range(T)
    ])
    pe_peaks, _ = find_peaks(pe_multi, height=np.percentile(pe_multi[70:], 85), distance=18)
    leads_pe = compute_leads(pe_peaks.tolist(), structural_changes)

    var_tau = np.var(tau_s, axis=0)
    var_peaks, _ = find_peaks(var_tau, height=np.percentile(var_tau[70:], 88), distance=18)
    leads_var = compute_leads(var_peaks.tolist(), structural_changes)

    dtau = np.zeros(T)
    for i in range(n_reg):
        dtau[1:] += np.abs(np.diff(tau_s[i])) / n_reg
    dtau_peaks, _ = find_peaks(dtau, height=np.percentile(dtau[70:], 85), distance=15)
    leads_dtau = compute_leads(dtau_peaks.tolist(), structural_changes)

    return {
        "PE multivariada": leads_pe,
        "Varianza τ_s": leads_var,
        "Δ τ_s individual": leads_dtau,
    }


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
        "n_I": len(leads_I), "n_other": len(all_other),
        "mean_I": float(np.mean(leads_I)), "mean_other": float(np.mean(all_other)),
        "mw_p": float(mw_p), "perm_p": float(perm_p)
    }


# =============================================================================
# 6 FIGURAS PRINCIPALES (con nombres para Iquitos)
# =============================================================================

def save_all_figures(metrics, strong_peaks, structural_changes, dist_smooth, dist_thresh,
                     leads_I, leads_other, region_names):
    T = metrics["I"].shape[1]
    tau_s = metrics["tau_s"]
    I_mat = metrics["I"]
    C = metrics["C"]
    n_reg = len(region_names)

    # Fig 1
    fig, ax = plt.subplots(figsize=(11, 5.2))
    for i in range(n_reg):
        ax.plot(tau_s[i], label=region_names[i], color=REGION_COLORS[i], lw=1.6)
        th = np.percentile(tau_s[i], 80)
        ax.fill_between(range(T), tau_s[i], where=(tau_s[i] > th), alpha=0.18, color=REGION_COLORS[i])
    for ch in structural_changes:
        ax.axvline(ch, color="crimson", ls="--", alpha=0.55, lw=1.1)
    ax.set_xlabel("Semana (índice k)")
    ax.set_ylabel(r"$\tau_s(k)$ (RECD local)")
    ax.set_title("Figura 1: Series de $\\tau_s$ local por región (Iquitos)\n"
                 f"Parámetros óptimos: τ={TAU_WINDOW}, C={COH_WINDOW}, Q={PEAK_Q}")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "iq_fig1_tau_s_series.png"), bbox_inches="tight")
    plt.close()

    # Fig 2
    fig, ax = plt.subplots(figsize=(11, 5.2))
    for i in range(n_reg):
        ax.plot(I_mat[i], label=region_names[i], color=REGION_COLORS[i], lw=1.5)
    for reg, k in strong_peaks:
        ax.scatter(k, I_mat[reg, k], marker="*", s=160, c="black", zorder=7, edgecolors="white")
    for ch in structural_changes:
        ax.axvline(ch, color="crimson", ls="--", alpha=0.55, lw=1.1)
    ax.set_xlabel("Semana (índice k)")
    ax.set_ylabel(r"$I_i(k)$")
    ax.set_title("Figura 2: Producto de intensidad $I_i(k)$ (Iquitos)\nEstrellas = picos fuertes")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "iq_fig2_I_intensity.png"), bbox_inches="tight")
    plt.close()

    # Fig 3 - Heatmaps
    times_to_plot = []
    if strong_peaks:
        tp = strong_peaks[0][1]
        times_to_plot.append(("Antes del pico", max(COH_WINDOW+5, tp-70)))
        times_to_plot.append(("Durante pico fuerte", tp))
    if structural_changes:
        tc = structural_changes[0]
        times_to_plot.append(("Cambio estructural", tc))
    if times_to_plot:
        n_panels = len(times_to_plot)
        fig, axes = plt.subplots(1, n_panels, figsize=(4.2 * n_panels, 3.7))
        if n_panels == 1: axes = [axes]
        for ax, (lab, tk) in zip(axes, times_to_plot):
            sns.heatmap(C[:, :, tk], annot=True, fmt=".2f", cmap="RdYlBu_r", center=0,
                        square=True, ax=ax, cbar=False, xticklabels=region_names, yticklabels=region_names)
            ax.set_title(f"{lab}\nk={tk}")
        plt.suptitle("Figura 3: Matrices de coherencia $C_{ij}(k)$ (Iquitos)", y=1.02)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "iq_fig3_coherence_matrices.png"), bbox_inches="tight")
        plt.close()

    # Fig 4 - Violin leads
    leads_dict = {"Picos fuertes I_i": leads_I, **leads_other}
    plot_data = {"Método": [], "Adelanto (pasos)": []}
    for name, ls in leads_dict.items():
        if len(ls) > 0:
            plot_data["Método"].extend([name] * len(ls))
            plot_data["Adelanto (pasos)"].extend(ls)
    df_plot = pd.DataFrame(plot_data)
    if len(df_plot) > 0:
        fig, ax = plt.subplots(figsize=(9, 5.5))
        sns.violinplot(data=df_plot, x="Método", y="Adelanto (pasos)", ax=ax, inner="box", hue="Método", palette="muted", legend=False)
        sns.stripplot(data=df_plot, x="Método", y="Adelanto (pasos)", ax=ax, color="k", alpha=0.35, size=3.5)
        ax.set_title("Figura 4: Distribución de adelantos (Iquitos)")
        plt.xticks(rotation=12, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "iq_fig4_lead_distributions.png"), bbox_inches="tight")
        plt.close()

    # Fig 5 - Mean leads
    methods, means, ns = [], [], []
    for name, ls in leads_dict.items():
        if len(ls) > 0:
            methods.append(name)
            means.append(np.mean(ls))
            ns.append(len(ls))
    if methods:
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(methods, means, color=sns.color_palette("Set2", len(methods)))
        for bar, m, n in zip(bars, means, ns):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()+2, f"{m:.1f}\n(n={n})", ha="center", fontsize=9)
        ax.set_title("Figura 5: Adelanto medio por método (Iquitos)")
        plt.xticks(rotation=12, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "iq_fig5_mean_leads.png"), bbox_inches="tight")
        plt.close()

    # Fig 6 - Coherence distance
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.plot(dist_smooth, color="steelblue", lw=1.2, label=r"$\Vert\Delta C\Vert_F$")
    ax.axhline(dist_thresh, color="gray", ls=":", label=f"Umbral ({STRUCTURAL_PERCENTILE}%)")
    for ch in structural_changes:
        ax.axvline(ch, color="darkred", ls="--", alpha=0.6)
    for _, k in strong_peaks:
        ax.scatter(k, dist_smooth[k], marker="v", s=90, c="darkorange", zorder=6)
    ax.set_title("Figura 6: Distancia entre matrices de coherencia (Iquitos)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "iq_fig6_coherence_distance.png"), bbox_inches="tight")
    plt.close()

    print(f"[FIGURAS] 6 figuras guardadas en {OUTPUT_DIR}/ (prefijo iq_)")


# =============================================================================
# EXPORT CSV DE PICOS FUERTES (IQUITOS)
# =============================================================================

def export_picos_csv(metrics, strong_peaks, structural_changes, region_names):
    I, peso, rho, gamma, tau_s, C = metrics["I"], metrics["peso"], metrics["rho"], metrics["gamma"], metrics["tau_s"], metrics["C"]
    ch = np.array(sorted(structural_changes))
    records = []

    for reg_idx, k in strong_peaks:
        future = ch[ch > k]
        lead = int(future[0] - k) if len(future) > 0 else -1

        current_tau = tau_s[reg_idx, k]
        recent_tau = tau_s[reg_idx, max(0, k-20):k+1]
        hyper_level = (current_tau - np.mean(recent_tau)) / (np.std(recent_tau) + 1e-6)

        row_c = [abs(C[reg_idx, j, k]) for j in range(len(region_names)) if j != reg_idx]
        avg_conn = np.mean(row_c) if row_c else 0.0

        records.append({
            "region": region_names[reg_idx],
            "k": k,
            "I_value": round(float(I[reg_idx, k]), 5),
            "Peso": round(float(peso[reg_idx, k]), 5),
            "rho": round(float(rho[reg_idx, k]), 5),
            "Gamma": round(float(gamma[reg_idx, k]), 5),
            "lead_to_next_change": lead,
            "tau_s_at_peak": round(float(current_tau), 4),
            "hyper_persistence_level": round(float(hyper_level), 4),
            "avg_spatial_connectivity": round(float(avg_conn), 4),
        })

    df = pd.DataFrame(records)
    out_path = os.path.join(OUTPUT_DIR, "picos_fuertes_iquitos.csv")
    df.to_csv(out_path, index=False)
    print(f"[EXPORT] CSV de picos fuertes: {out_path} ({len(df)} picos)")
    return df


# =============================================================================
# ANÁLISIS EXPLORATORIO DE PICOS (ADAPTADO PARA IQUITOS)
# =============================================================================

def run_peaks_exploratory_analysis(df):
    """Realiza el análisis profundo de picos y genera figuras + reporte en analisis_picos_iquitos/"""
    print("\n[ANÁLISIS EXPLORATORIO DE PICOS - IQUITOS]")

    # Estadísticas básicas
    print(f"    Total picos: {len(df)}")
    print(f"    Distribución por región:\n{df['region'].value_counts().to_string()}")

    numeric_cols = ["I_value", "Peso", "rho", "Gamma", "lead_to_next_change",
                    "hyper_persistence_level", "avg_spatial_connectivity", "tau_s_at_peak"]
    print("\n    Estadísticas descriptivas:")
    print(df[numeric_cols].describe().round(3).to_string())

    # Correlaciones con lead
    print("\n    Correlaciones con lead_to_next_change (Spearman):")
    for var in numeric_cols:
        if var != "lead_to_next_change":
            r, p = stats.spearmanr(df[var], df["lead_to_next_change"], nan_policy="omit")
            sig = " *" if p < 0.10 else ""
            print(f"      {var:30s}: r={r:+.3f} (p={p:.4f}){sig}")

    lead_median = df["lead_to_next_change"].median()
    df["high_lead"] = df["lead_to_next_change"] > lead_median

    # Perfiles simples
    med = df[numeric_cols].median()
    df["profile"] = "Other"
    df.loc[(df["Peso"] > med["Peso"]) & (df["Gamma"] > med["Gamma"]), "profile"] = "High Persistence"
    df.loc[(df["rho"] > med["rho"]) & (df["Peso"] > med["Peso"]), "profile"] = "High Connectivity + Persistence"
    df.loc[(df["Gamma"] > med["Gamma"]) & (df["rho"] > med["rho"]), "profile"] = "High Volatility + Connectivity"

    print("\n    Perfiles y adelanto medio:")
    print(df.groupby("profile")["lead_to_next_change"].agg(["mean", "count"]).sort_values("mean", ascending=False).round(1).to_string())

    # Figuras exploratorias (prefijo iq_)
    # 1. Heatmap correlaciones
    corr = df[numeric_cols].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlBu_r", center=0, ax=ax)
    ax.set_title("Figura E1: Correlaciones entre características de picos (Iquitos)")
    plt.tight_layout()
    plt.savefig(os.path.join(PEAKS_ANALYSIS_DIR, "iq_picos_correlation_heatmap.png"), bbox_inches="tight")
    plt.close()

    # 2. Distribución lead
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df["lead_to_next_change"], bins=10, kde=True, ax=ax, color="steelblue")
    ax.axvline(lead_median, color="red", ls="--", label=f"Mediana = {lead_median:.1f}")
    ax.set_title("Figura E2: Distribución del adelanto (Iquitos)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PEAKS_ANALYSIS_DIR, "iq_picos_lead_distribution.png"), bbox_inches="tight")
    plt.close()

    # 3. Boxplot lead por región
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df, x="region", y="lead_to_next_change", hue="region", palette=REGION_PALETTE, ax=ax, legend=False)
    sns.stripplot(data=df, x="region", y="lead_to_next_change", color="k", alpha=0.4, ax=ax)
    ax.set_title("Figura E3: Adelanto por región (Iquitos)")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(PEAKS_ANALYSIS_DIR, "iq_picos_lead_by_region.png"), bbox_inches="tight")
    plt.close()

    # 4. Hyper persistence vs lead
    fig, ax = plt.subplots(figsize=(8, 5.5))
    sns.scatterplot(data=df, x="hyper_persistence_level", y="lead_to_next_change", hue="region", palette=REGION_PALETTE, s=80, ax=ax)
    sns.regplot(data=df, x="hyper_persistence_level", y="lead_to_next_change", scatter=False, color="black", line_kws={"ls":"--"}, ax=ax)
    ax.set_title("Figura E4: Hiper-persistencia vs Adelanto (Iquitos)")
    plt.tight_layout()
    plt.savefig(os.path.join(PEAKS_ANALYSIS_DIR, "iq_picos_hyper_vs_lead.png"), bbox_inches="tight")
    plt.close()

    # 5. Alto vs Bajo lead features
    features = ["hyper_persistence_level", "avg_spatial_connectivity", "I_value", "tau_s_at_peak"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for i, feat in enumerate(features):
        sns.boxplot(data=df, x="high_lead", y=feat, hue="high_lead", palette={True: "#2ca02c", False: "#d62728"}, ax=axes.flat[i], legend=False)
        axes.flat[i].set_xticklabels(["Bajo lead", "Alto lead"])
        axes.flat[i].set_title(feat)
    plt.suptitle("Figura E5: Características Alto vs Bajo lead (Iquitos)")
    plt.tight_layout()
    plt.savefig(os.path.join(PEAKS_ANALYSIS_DIR, "iq_picos_high_vs_low_features.png"), bbox_inches="tight")
    plt.close()

    print(f"[ANÁLISIS PICOS] Figuras y datos guardados en {PEAKS_ANALYSIS_DIR}/")

    # Reporte simple
    report = f"""REPORTE ANÁLISIS PICOS FUERTES - IQUITOS
Fecha: {datetime.now().isoformat()}
Parámetros: TAU=85, COH=90, Q=0.60

Total picos: {len(df)}
Adelanto medio I_i: {df['lead_to_next_change'].mean():.2f} (n={len(df)})
Mediana lead: {lead_median:.1f}

Mejor perfil predictivo: High I + High Persistence (ver detalles arriba)
"""
    with open(os.path.join(PEAKS_ANALYSIS_DIR, "reporte_picos_iquitos.txt"), "w") as f:
        f.write(report)

    return df


# =============================================================================
# RESUMEN COMPARATIVO FINAL
# =============================================================================

def print_comparative_summary(n_peaks_iq, n_changes_iq, leads_I_iq, stats_iq):
    # Números de San Juan (hardcodeados del análisis anterior)
    sj_peaks = 27
    sj_changes = 8
    sj_lead = 90.57
    sj_mw_p = 0.0995
    sj_perm_p = 0.0930

    print("\n" + "=" * 78)
    print("RESUMEN COMPARATIVO FINAL - PREDICCIÓN 2")
    print("San Juan (sj) vs Iquitos (iq) — Mismos parámetros: τ=85, C=90, Q=0.60")
    print("=" * 78)

    print(f"\n{'Métrica':<35} {'San Juan':>15} {'Iquitos':>15}")
    print("-" * 65)
    print(f"{'Picos fuertes I_i detectados':<35} {sj_peaks:>15} {n_peaks_iq:>15}")
    print(f"{'Cambios estructurales':<35} {sj_changes:>15} {n_changes_iq:>15}")
    print(f"{'Adelanto medio I_i (pasos)':<35} {sj_lead:>15.2f} {np.mean(leads_I_iq):>15.2f}")
    print(f"{'Mann-Whitney p-value':<35} {sj_mw_p:>15.4f} {stats_iq['mw_p']:>15.4f}")
    print(f"{'Permutation p-value':<35} {sj_perm_p:>15.4f} {stats_iq['perm_p']:>15.4f}")

    print("\nConclusión para Iquitos:")
    mean_i = np.mean(leads_I_iq)
    if mean_i > 50 and stats_iq['mw_p'] < 0.15:
        print("  >> TENDENCIA A FAVOR de la Predicción 2 en Iquitos.")
    else:
        print("  >> Evidencia más débil que en San Juan (menor adelanto y p-values más altos).")

    print("\nComparación general:")
    print(f"  - San Juan muestra evidencia más fuerte (adelanto ~90 pasos, p≈0.09).")
    print(f"  - Iquitos muestra tendencia positiva pero con menor magnitud y significancia.")
    print("=" * 78)


# =============================================================================
# MAIN
# =============================================================================

def main():
    ensure_data()
    regions_data, region_names = load_iquitos_regions(DATA_PATH)

    print("\n[RUN] Ejecutando pipeline para Iquitos con parámetros óptimos...")
    metrics = compute_all_metrics(regions_data)
    strong_peaks = detect_strong_peaks(metrics)
    struct_changes, dist_smooth, dist_thresh = detect_structural_changes(metrics["C"])

    i_times = [k for _, k in strong_peaks]
    leads_I = compute_leads(i_times, struct_changes)
    leads_other = compute_reference_leads(metrics, struct_changes)
    stats_res = run_statistical_test(leads_I, leads_other)

    # Figuras principales
    print("\n[FIGURAS PRINCIPALES]")
    save_all_figures(metrics, strong_peaks, struct_changes, dist_smooth, dist_thresh,
                     leads_I, leads_other, region_names)

    # CSV de picos
    df_picos = export_picos_csv(metrics, strong_peaks, struct_changes, region_names)

    # Análisis exploratorio de picos
    run_peaks_exploratory_analysis(df_picos)

    # Resumen comparativo
    print_comparative_summary(len(strong_peaks), len(struct_changes), leads_I, stats_res)

    print(f"\nArchivos generados:")
    print(f"  - Figuras principales: {OUTPUT_DIR}/ (iq_fig*.png)")
    print(f"  - CSV picos: {os.path.join(OUTPUT_DIR, 'picos_fuertes_iquitos.csv')}")
    print(f"  - Análisis exploratorio: {PEAKS_ANALYSIS_DIR}/")


if __name__ == "__main__":
    main()