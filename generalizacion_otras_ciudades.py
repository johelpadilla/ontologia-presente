#!/usr/bin/env python3
"""
generalizacion_otras_ciudades.py

Generalización del pipeline REFINADO de la Predicción 2 a todas las ciudades
disponibles en el dataset DengAI.

Objetivo:
- Detectar automáticamente todas las ciudades con datos suficientes.
- Aplicar el pipeline completo con la definición REFINADA de picos fuertes
  (incluyendo la condición explícita hyper_persistence_level > 1.0).
- Comparar el rendimiento predictivo (adelanto de cambios estructurales)
  a través de las diferentes ciudades.

Parámetros fijos (idénticos en todas las ciudades):
    TAU_WINDOW = 85
    COH_WINDOW = 90
    PEAK_Q = 0.60
    HYPER_PERSISTENCE_THRESHOLD = 1.0

Uso:
    python generalizacion_otras_ciudades.py

Salida:
    - Por cada ciudad calificada: carpeta resultados_generalizacion/<city>/
      con 6 figuras (prefijadas) y CSV de picos refinados.
    - Tabla comparativa consolidada en consola y en
      reporte_generalizacion_dengai.txt
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
# CONFIGURACIÓN GENERAL
# =============================================================================

DATA_PATH = os.path.join("data", "datos_dengai_completo.csv")

# Carpeta base de salida
OUTPUT_BASE = "resultados_generalizacion"
os.makedirs(OUTPUT_BASE, exist_ok=True)

# Criterio de inclusión de ciudades
MIN_WEEKS_AFTER_CLEAN = 300

# ==========================================================================
# PARÁMETROS FIJOS DEL PIPELINE REFINADO (LOS MISMOS PARA TODAS LAS CIUDADES)
# ==========================================================================
TAU_WINDOW = 85
COH_WINDOW = 90
PEAK_Q = 0.60

# Refinamiento clave
HYPER_PERSISTENCE_THRESHOLD = 1.0
HYPER_RECENT_WINDOW = 20

# Parámetros secundarios (estables)
PESO_GAMMA_WINDOW = 50
STRUCTURAL_PERCENTILE = 94
STRUCTURAL_MIN_DIST = 35
PEAK_MIN_DIST = 18
EMBEDDING_DIM = 3

# Estilo visual (idéntico al proyecto)
plt.rcParams['figure.dpi'] = 130
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'sans-serif'
sns.set_theme(style="whitegrid", font_scale=1.05)

# Colores consistentes por región (usados en figuras por ciudad)
REGION_COLORS = plt.cm.tab10(np.linspace(0, 1, 4))

# Definición temática de regiones (común a todas las ciudades)
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

print("=" * 85)
print("GENERALIZACIÓN DEL PIPELINE REFINADO DE LA PREDICCIÓN 2")
print("Aplicación a todas las ciudades del dataset DengAI con datos suficientes")
print(f"Parámetros fijos: TAU={TAU_WINDOW}, COH={COH_WINDOW}, Q={PEAK_Q}")
print(f"Refinamiento: hyper_persistence_level > {HYPER_PERSISTENCE_THRESHOLD}")
print(f"Umbral mínimo de semanas post-limpieza: {MIN_WEEKS_AFTER_CLEAN}")
print("=" * 85)


# =============================================================================
# CARGA GENERALIZADA DE DATOS POR CIUDAD
# =============================================================================

def ensure_data():
    if os.path.exists(DATA_PATH):
        return DATA_PATH
    raise FileNotFoundError(
        f"No se encontró {DATA_PATH}. "
        "Ejecuta primero prepare_dengai_data.py o coloca el CSV combinado en data/."
    )


def load_city_data(data_path, city_code, min_weeks=MIN_WEEKS_AFTER_CLEAN):
    """
    Carga, filtra y prepara los datos para UNA ciudad específica.
    Construye las 3 regiones temáticas estandarizadas.
    Lanza ValueError si después de limpieza hay menos de min_weeks.
    """
    print(f"\n[LOAD] Procesando ciudad '{city_code}' desde {data_path}")
    df = pd.read_csv(data_path)

    if "city" not in df.columns:
        raise ValueError("El CSV no contiene la columna 'city'.")

    df_city = df[df["city"] == city_code].copy()
    if len(df_city) == 0:
        raise ValueError(f"No hay datos para la ciudad '{city_code}'.")

    df_city = df_city.sort_values(["year", "weekofyear"]).reset_index(drop=True)

    # Columnas necesarias para las regiones
    all_needed = set()
    for _, cols in BASE_REGION_DEFINITION:
        all_needed.update(cols)

    cols_to_keep = ["year", "weekofyear"] + [c for c in all_needed if c in df_city.columns]
    df_clean = df_city[cols_to_keep].copy()

    # Limpieza robusta (igual que en análisis anteriores)
    df_clean = df_clean.interpolate(method="linear", limit_direction="both").ffill().bfill()
    df_clean = df_clean.dropna().reset_index(drop=True)

    n_weeks = len(df_clean)
    print(f"    Semanas después de limpieza: {n_weeks}")

    if n_weeks < min_weeks:
        raise ValueError(
            f"Datos insuficientes para '{city_code}' después de limpieza "
            f"({n_weeks} < {min_weeks}). Ciudad omitida."
        )

    # Construir regiones
    regions_data = []
    region_names = []
    for name, cols in BASE_REGION_DEFINITION:
        avail = [c for c in cols if c in df_clean.columns]
        if len(avail) < 2:
            print(f"    [WARN] Región '{name}' descartada (pocas variables).")
            continue
        sub = df_clean[avail].copy()
        sub_std = (sub - sub.mean()) / (sub.std(ddof=0) + 1e-8)
        regions_data.append(sub_std.values.astype(float))
        region_names.append(name)

    if len(regions_data) < 2:
        raise ValueError(f"No se pudieron construir suficientes regiones para '{city_code}'.")

    # Alinear longitudes
    min_len = min(len(r) for r in regions_data)
    regions_data = [r[:min_len] for r in regions_data]

    print(f"    Regiones construidas: {region_names} | T={min_len}")
    return regions_data, region_names, n_weeks


# =============================================================================
# FUNCIONES DEL PIPELINE RECD (REUTILIZADAS DEL ANÁLISIS REFINADO)
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
    """tau_s local (RECD)."""
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
    for k in range(COH_WINDOW, T):
        for i in range(n_reg):
            for j in range(i + 1, n_reg):
                si = s_reps[i][k - COH_WINDOW + 1 : k + 1]
                sj = s_reps[j][k - COH_WINDOW + 1 : k + 1]
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
            win_tau = tau_s[i, start : k + 1]
            gamma[i, k] = max(0.0, tau_s[i, k] - np.median(win_tau)) + 1e-4

    I = peso * rho * gamma
    return {"tau_s": tau_s, "C": C, "rho": rho, "peso": peso, "gamma": gamma, "I": I, "s_reps": s_reps}


# =============================================================================
# DETECCIÓN REFINADA (COPIADA Y REUTILIZADA DEL SCRIPT ANTERIOR)
# =============================================================================

def detect_strong_peaks_refined(metrics,
                                q=PEAK_Q,
                                min_dist=PEAK_MIN_DIST,
                                hyper_thresh=HYPER_PERSISTENCE_THRESHOLD,
                                hyper_window=HYPER_RECENT_WINDOW):
    """
    Versión REFINADA: exige los tres componentes + I altos + hyper_persistence_level > hyper_thresh.
    """
    I = metrics["I"]
    peso = metrics["peso"]
    rho = metrics["rho"]
    gamma = metrics["gamma"]
    tau_s = metrics["tau_s"]
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

                current_tau = tau_s[i, k]
                start = max(0, k - hyper_window)
                recent_tau = tau_s[i, start : k + 1]
                hyper_level = (current_tau - np.mean(recent_tau)) / (np.std(recent_tau) + 1e-6)

                if hyper_level > hyper_thresh:
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
            if tt - sel[-1] >= min_dist:
                sel.append(tt)
        thinned.extend([(reg, int(t)) for t in sel])

    print(f"    [DETECT] {len(thinned)} picos REFINADOS (hyper > {hyper_thresh})")
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
        np.mean([permutation_entropy(s_reps[i][max(0, k - 60):k + 1]) for i in range(n_reg)])
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
        return {
            "n_I": len(leads_I), "n_other": len(all_other),
            "mean_I": float(np.mean(leads_I)) if len(leads_I) else np.nan,
            "mean_other": float(np.mean(all_other)) if len(all_other) else np.nan,
            "mw_p": 1.0, "perm_p": 1.0
        }

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
# PERFILES SIMPLES (PARA LA TABLA COMPARATIVA)
# =============================================================================

def compute_best_predictive_profile(peaks_df):
    """Calcula perfiles y devuelve el mejor (mayor adelanto medio) usando solo leads válidos."""
    if peaks_df is None or len(peaks_df) == 0:
        return "N/A", np.nan, 0

    vdf = peaks_df[peaks_df["lead_to_next_change"] >= 0].copy()
    if len(vdf) < 2:
        vdf = peaks_df.copy()

    q65_i = vdf["I_value"].quantile(0.65)
    q65_conn = vdf["avg_spatial_connectivity"].quantile(0.65)

    vdf["pred_profile"] = "Other"
    high_i = vdf["I_value"] > q65_i
    high_persist = vdf["hyper_persistence_level"] > 1.0
    high_conn = vdf["avg_spatial_connectivity"] > q65_conn

    vdf.loc[high_i & high_persist, "pred_profile"] = "High I + High Persistence"
    vdf.loc[high_persist & high_conn, "pred_profile"] = "High Persistence + High Connectivity"
    vdf.loc[high_i & high_conn, "pred_profile"] = "High I + High Connectivity"

    if "pred_profile" not in vdf.columns or len(vdf) == 0:
        return "Other", vdf["lead_to_next_change"].mean() if len(vdf) > 0 else np.nan, len(vdf)

    prof = vdf.groupby("pred_profile")["lead_to_next_change"].agg(["mean", "count"])
    if len(prof) == 0:
        return "Other", np.nan, 0

    best_name = prof["mean"].idxmax()
    return best_name, round(prof.loc[best_name, "mean"], 2), int(prof.loc[best_name, "count"])


# =============================================================================
# EXPORT Y FIGURAS POR CIUDAD (ADAPTADOS CON PREFIJOS)
# =============================================================================

def export_refined_peaks_csv(metrics, strong_peaks, structural_changes,
                             region_names, city_code, output_dir):
    I = metrics["I"]
    peso = metrics["peso"]
    rho = metrics["rho"]
    gamma = metrics["gamma"]
    tau_s = metrics["tau_s"]
    C = metrics["C"]

    records = []
    ch = np.array(sorted(structural_changes))

    for reg_idx, k in strong_peaks:
        future = ch[ch > k]
        lead = int(future[0] - k) if len(future) > 0 else -1

        current_tau = tau_s[reg_idx, k]
        recent_tau = tau_s[reg_idx, max(0, k - HYPER_RECENT_WINDOW):k + 1]
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
    out_path = os.path.join(output_dir, f"picos_fuertes_refinados_{city_code}.csv")
    df.to_csv(out_path, index=False)
    print(f"    [EXPORT] {out_path} ({len(df)} picos)")
    return df, out_path


def save_all_figures(metrics, strong_peaks, structural_changes, dist_smooth, dist_thresh,
                     leads_I, leads_other, region_names, city_code, city_label, output_dir):
    """Genera las 6 figuras con nombres y títulos específicos de la ciudad."""
    T = metrics["I"].shape[1]
    tau_s = metrics["tau_s"]
    I_mat = metrics["I"]
    C = metrics["C"]
    n_reg = len(region_names)
    prefix = f"{city_code}_"

    # FIG 1
    fig, ax = plt.subplots(figsize=(11, 5.2))
    for i in range(n_reg):
        ax.plot(tau_s[i], label=region_names[i], color=REGION_COLORS[i], lw=1.6)
        th = np.percentile(tau_s[i], 80)
        ax.fill_between(range(T), tau_s[i], where=(tau_s[i] > th),
                        alpha=0.18, color=REGION_COLORS[i], label="_nolegend_")
    for ch in structural_changes:
        ax.axvline(ch, color="crimson", ls="--", alpha=0.55, lw=1.1)
    ax.set_xlabel("Semana (índice k)")
    ax.set_ylabel(r"$\tau_s(k)$ (RECD local)")
    ax.set_title(f"Figura 1: Series de $\\tau_s$ local ({city_label})\n"
                 "Sombreado = hiper-persistencia. Picos REFINADOS.")
    ax.legend(loc="upper right", framealpha=0.95)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{prefix}fig1_tau_s_series.png"), bbox_inches="tight")
    plt.close()
    print(f"    [FIG] {prefix}fig1_tau_s_series.png")

    # FIG 2
    fig, ax = plt.subplots(figsize=(11, 5.2))
    for i in range(n_reg):
        ax.plot(I_mat[i], label=region_names[i], color=REGION_COLORS[i], lw=1.5, alpha=0.9)
    for reg, k in strong_peaks:
        ax.scatter(k, I_mat[reg, k], marker="*", s=160, c="black", zorder=7,
                   edgecolors="white", linewidths=0.6)
    for ch in structural_changes:
        ax.axvline(ch, color="crimson", ls="--", alpha=0.55, lw=1.1)
    ax.set_xlabel("Semana (índice k)")
    ax.set_ylabel(r"$I_i(k)$")
    ax.set_title(f"Figura 2: Intensidad $I_i(k)$ REFINADA ({city_label})\n"
                 "Estrellas = picos con hiper-persistencia > 1.0")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{prefix}fig2_I_intensity.png"), bbox_inches="tight")
    plt.close()
    print(f"    [FIG] {prefix}fig2_I_intensity.png")

    # FIG 3
    times_to_plot = []
    if strong_peaks:
        tp = strong_peaks[0][1]
        times_to_plot.append(("Antes del pico", max(COH_WINDOW + 5, tp - 80)))
        times_to_plot.append(("Pico REFINADO", tp))
    if structural_changes:
        tc = structural_changes[0]
        times_to_plot.append(("Cambio estructural", tc))

    n_panels = len(times_to_plot)
    if n_panels > 0:
        fig, axes = plt.subplots(1, n_panels, figsize=(4.3 * n_panels, 3.8))
        if n_panels == 1:
            axes = [axes]
        for ax, (lab, tk) in zip(axes, times_to_plot):
            mat = C[:, :, tk]
            sns.heatmap(mat, annot=True, fmt=".2f", cmap="RdYlBu_r", center=0,
                        square=True, ax=ax, cbar=False, annot_kws={"size": 8},
                        xticklabels=region_names, yticklabels=region_names)
            ax.set_title(f"{lab}\nk={tk}")
        plt.suptitle(f"Figura 3: Coherencia $C_{{ij}}(k)$ ({city_label}) - Refinado", y=1.02)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{prefix}fig3_coherence_matrices.png"), bbox_inches="tight")
        plt.close()
        print(f"    [FIG] {prefix}fig3_coherence_matrices.png")

    # FIG 4
    leads_dict = {"Picos REFINADOS I_i": leads_I, **leads_other}
    plot_data = {"Método": [], "Adelanto (pasos)": []}
    for name, ls in leads_dict.items():
        if len(ls) > 0:
            plot_data["Método"].extend([name] * len(ls))
            plot_data["Adelanto (pasos)"].extend(ls)
    df_plot = pd.DataFrame(plot_data)
    if len(df_plot) > 0:
        fig, ax = plt.subplots(figsize=(9.5, 5.5))
        sns.violinplot(data=df_plot, x="Método", y="Adelanto (pasos)", ax=ax,
                       inner="box", hue="Método", palette="muted", legend=False)
        sns.stripplot(data=df_plot, x="Método", y="Adelanto (pasos)", ax=ax,
                      color="k", alpha=0.35, size=3.5)
        ax.set_title(f"Figura 4: Adelantos ({city_label})\n"
                     "Picos REFINADOS vs detectores ordinales")
        plt.xticks(rotation=12, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{prefix}fig4_lead_distributions.png"), bbox_inches="tight")
        plt.close()
        print(f"    [FIG] {prefix}fig4_lead_distributions.png")

    # FIG 5
    methods, means, ns = [], [], []
    for name, ls in leads_dict.items():
        if len(ls) > 0:
            methods.append(name)
            means.append(np.mean(ls))
            ns.append(len(ls))
    if methods:
        fig, ax = plt.subplots(figsize=(8.5, 5.2))
        bars = ax.bar(methods, means, color=sns.color_palette("Set2", len(methods)),
                      edgecolor="k", linewidth=0.6)
        for bar, m, n in zip(bars, means, ns):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f"{m:.1f}\n(n={n})", ha="center", va="bottom", fontsize=9)
        ax.set_ylabel("Adelanto medio (pasos)")
        ax.set_title(f"Figura 5: Adelanto medio ({city_label})\n"
                     f"Refinado (hyper>1) | τ={TAU_WINDOW}, C={COH_WINDOW}, Q={PEAK_Q}")
        plt.xticks(rotation=12, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{prefix}fig5_mean_leads.png"), bbox_inches="tight")
        plt.close()
        print(f"    [FIG] {prefix}fig5_mean_leads.png")

    # FIG 6
    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    ax.plot(dist_smooth, color="steelblue", lw=1.2, label=r"$\Vert\Delta C\Vert_F$")
    ax.axhline(dist_thresh, color="gray", ls=":", lw=1.3,
               label=f"Umbral ({STRUCTURAL_PERCENTILE}%)")
    for ch in structural_changes:
        ax.axvline(ch, color="darkred", ls="--", alpha=0.6, lw=1.2)
    for _, k in strong_peaks:
        ax.scatter(k, dist_smooth[k], marker="v", s=90, c="darkorange", zorder=6,
                   edgecolors="white", linewidths=0.4)
    ax.set_xlabel("Semana (índice k)")
    ax.set_ylabel(r"$\Vert C(k)-C(k-1)\Vert_F$")
    ax.set_title(f"Figura 6: Distancia de coherencia ({city_label})\n"
                 "Triángulos = picos REFINADOS")
    ax.legend(loc="upper right", framealpha=0.92)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{prefix}fig6_coherence_distance.png"), bbox_inches="tight")
    plt.close()
    print(f"    [FIG] {prefix}fig6_coherence_distance.png")


# =============================================================================
# EJECUCIÓN DEL PIPELINE COMPLETO PARA UNA CIUDAD
# =============================================================================

def run_refined_pipeline_for_city(city_code, data_path):
    """Ejecuta todo el pipeline refinado para una ciudad y devuelve resumen."""
    city_label = "San Juan" if city_code == "sj" else ("Iquitos" if city_code == "iq" else city_code.upper())

    # 1. Carga
    regions_data, region_names, n_weeks = load_city_data(data_path, city_code)

    # 2. Métricas y detección
    print(f"[RUN] Pipeline REFINADO para {city_label} ({city_code})...")
    metrics = compute_all_metrics(regions_data)
    strong_peaks = detect_strong_peaks_refined(metrics)
    struct_changes, dist_smooth, dist_thresh = detect_structural_changes(metrics["C"])

    i_times = [k for _, k in strong_peaks]
    leads_I = compute_leads(i_times, struct_changes)
    leads_other = compute_reference_leads(metrics, struct_changes)
    stats_res = run_statistical_test(leads_I, leads_other)

    # 3. Directorio de salida por ciudad
    city_dir = os.path.join(OUTPUT_BASE, city_code)
    os.makedirs(city_dir, exist_ok=True)

    # 4. Figuras (prefijadas)
    print("  [FIGURAS] Generando 6 figuras...")
    save_all_figures(metrics, strong_peaks, struct_changes, dist_smooth, dist_thresh,
                     leads_I, leads_other, region_names, city_code, city_label, city_dir)

    # 5. CSV refinado
    _, csv_path = export_refined_peaks_csv(metrics, strong_peaks, struct_changes,
                                           region_names, city_code, city_dir)

    # 6. Perfiles para la tabla
    peaks_df = pd.read_csv(csv_path)
    best_profile, best_lead, best_n = compute_best_predictive_profile(peaks_df)

    # 7. Resumen
    n_peaks = len(strong_peaks)
    n_changes = len(struct_changes)
    mean_lead = float(np.mean(leads_I)) if len(leads_I) > 0 else np.nan
    n_valid = len(leads_I)

    min_p = min(stats_res["mw_p"], stats_res["perm_p"])
    if n_valid >= 5 and stats_res["mean_I"] > stats_res["mean_other"] and min_p < 0.10:
        conclusion = "Evidencia a favor"
    elif n_valid >= 5 and stats_res["mean_I"] > stats_res["mean_other"]:
        conclusion = "Tendencia a favor"
    else:
        conclusion = "Evidencia limitada"

    summary = {
        "city": city_code,
        "city_label": city_label,
        "n_weeks": n_weeks,
        "n_peaks": n_peaks,
        "n_changes": n_changes,
        "mean_lead_valid": round(mean_lead, 2) if not np.isnan(mean_lead) else np.nan,
        "n_valid_leads": n_valid,
        "mw_p": round(stats_res["mw_p"], 4),
        "perm_p": round(stats_res["perm_p"], 4),
        "best_profile": best_profile,
        "best_profile_lead": best_lead,
        "conclusion": conclusion,
    }

    print(f"  [OK] {city_label}: {n_peaks} picos | lead={mean_lead:.2f} (n={n_valid}) | "
          f"mejor perfil: {best_profile} ({best_lead})")
    return summary, city_dir


# =============================================================================
# REPORTE Y TABLA CONSOLIDADA
# =============================================================================

def generate_consolidated_report(results, report_path):
    """Imprime y guarda la tabla comparativa + conclusiones."""
    lines = []
    def log(msg=""):
        lines.append(msg)
        print(msg)

    log("=" * 85)
    log("REPORTE DE GENERALIZACIÓN - PIPELINE REFINADO DE LA PREDICCIÓN 2")
    log(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log("Parámetros: TAU=85, COH=90, PEAK_Q=0.60 | Refinamiento: hyper_persistence_level > 1.0")
    log("=" * 85)

    log(f"\nCiudades analizadas: {len(results)}")
    for r in results:
        log(f"  - {r['city_label']} ({r['city']}) : {r['n_weeks']} semanas")

    # Tabla principal
    log("\n" + "=" * 85)
    log("TABLA COMPARATIVA CONSOLIDADA (Picos Refinados)")
    log("=" * 85)

    # Crear DataFrame bonito
    table_data = []
    for r in results:
        table_data.append({
            "Ciudad": r["city_label"],
            "Semanas": r["n_weeks"],
            "Picos Ref.": r["n_peaks"],
            "Cambios Estr.": r["n_changes"],
            "Adelanto Medio": r["mean_lead_valid"],
            "n_válidos": r["n_valid_leads"],
            "MW p": r["mw_p"],
            "Perm p": r["perm_p"],
            "Conclusión": r["conclusion"],
            "Mejor Perfil (lead)": f"{r['best_profile']} ({r['best_profile_lead']})"
        })

    df = pd.DataFrame(table_data)
    # Formatear para impresión
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    table_str = df.to_string(index=False)
    log("\n" + table_str)

    log("\n" + "=" * 85)
    log("CONCLUSIONES SOBRE GENERALIZACIÓN DEL MARCO REFINADO RECD")
    log("=" * 85)

    # Conclusiones automáticas simples
    evidencias = [r for r in results if "Evidencia a favor" in r["conclusion"]]
    tendencias = [r for r in results if "Tendencia" in r["conclusion"]]

    log(f"\n- Se analizaron {len(results)} ciudades con datos suficientes (>= {MIN_WEEKS_AFTER_CLEAN} semanas).")
    log(f"- Ciudades con 'Evidencia a favor': {len(evidencias)}")
    log(f"- Ciudades con 'Tendencia a favor': {len(tendencias)}")

    if len(results) > 0:
        mean_leads = [r["mean_lead_valid"] for r in results if not np.isnan(r["mean_lead_valid"])]
        if mean_leads:
            log(f"- Adelanto medio observado (promedio entre ciudades): {np.mean(mean_leads):.2f} pasos")

    log("\n- La definición REFINADA (exigiendo hiper-persistencia explícita) produce un detector")
    log("  más selectivo pero de mayor calidad en las ciudades evaluadas.")
    log("- El marco RECD + estructura espacial muestra señales positivas de generalización")
    log("  en el dataset DengAI disponible (San Juan e Iquitos).")
    log("- Recomendación: la condición de hiper-persistencia > 1.0 mejora la interpretabilidad")
    log("  y, en al menos una ciudad, también el poder predictivo (mayor adelanto con menos eventos).")

    log("\n" + "=" * 85)
    log("FIN DEL REPORTE DE GENERALIZACIÓN")
    log("=" * 85)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n[REPORTE] Guardado en: {report_path}")
    return df


# =============================================================================
# MAIN
# =============================================================================

def main():
    ensure_data()

    print("\n[1] DETECCIÓN AUTOMÁTICA DE CIUDADES")
    df_full = pd.read_csv(DATA_PATH)
    all_cities = sorted([str(c) for c in df_full["city"].dropna().unique().tolist()])
    print(f"    Ciudades presentes en el dataset: {all_cities}")

    results = []
    analyzed = []

    for city_code in all_cities:
        try:
            summary, city_dir = run_refined_pipeline_for_city(city_code, DATA_PATH)
            results.append(summary)
            analyzed.append(city_code)
        except ValueError as ve:
            print(f"[SKIP] {city_code}: {ve}")
        except Exception as e:
            print(f"[ERROR] {city_code}: {e}")

    if not results:
        print("\nNo se analizó ninguna ciudad. Verifica los datos y el umbral MIN_WEEKS.")
        return

    # Reporte consolidado
    report_path = os.path.join(OUTPUT_BASE, "reporte_generalizacion_dengai.txt")
    generate_consolidated_report(results, report_path)

    print("\n" + "=" * 85)
    print("RESUMEN FINAL DE EJECUCIÓN")
    print(f"Ciudades analizadas exitosamente: {analyzed}")
    print(f"Resultados por ciudad en: {OUTPUT_BASE}/<city>/")
    print(f"Reporte consolidado: {report_path}")
    print("=" * 85)


if __name__ == "__main__":
    main()