#!/usr/bin/env python3
"""
analisis_refinado_san_juan.py

Análisis REFINADO de la Predicción 2 (RECD + estructura espacial)
usando una definición más estricta de "pico fuerte" de I_i.

La refinación clave:
    Un pico fuerte ahora requiere:
    - Peso, rho y Gamma por encima del percentil PEAK_Q (0.60)
    - I por encima del percentil 75
    - **Y** hyper_persistence_level > 1.0
      (es decir, la región debe estar en un estado de persistencia
       significativamente superior a su media reciente en el momento del pico).

Esto implementa de forma explícita la idea de que los precursores
más potentes ocurren durante "hiper-persistencia" clara.

Script enfocado en San Juan por defecto.
Cambia CITY = "iq" (o ejecuta con ambas) para Iquitos.

Uso:
    python analisis_refinado_san_juan.py
    # Para Iquitos:
    # edita CITY = "iq" al inicio y vuelve a ejecutar

Parámetros fijos (idénticos a la versión original):
    TAU_WINDOW = 85
    COH_WINDOW = 90
    PEAK_Q = 0.60
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
# CONFIGURACIÓN DEL ANÁLISIS REFINADO
# =============================================================================

# Ciudad(es) a analizar. 
# "sj" = San Juan, "iq" = Iquitos
# Puedes poner ["sj", "iq"] para analizar ambas en una sola ejecución.
CITIES_TO_RUN = ["sj"]

# Ruta de datos (compartida)
DATA_PATH = os.path.join("data", "datos_dengai_completo.csv")

# ==========================================================================
# PARÁMETROS FIJOS (LOS MISMOS QUE EN LA VERSIÓN ORIGINAL ÓPTIMA)
# ==========================================================================
TAU_WINDOW = 85
COH_WINDOW = 90
PEAK_Q = 0.60

# Parámetros secundarios
PESO_GAMMA_WINDOW = 50
STRUCTURAL_PERCENTILE = 94
STRUCTURAL_MIN_DIST = 35
PEAK_MIN_DIST = 18
EMBEDDING_DIM = 3

# =============================================================================
# REFINAMIENTO DE LA DEFINICIÓN DE "PICO FUERTE"
# =============================================================================
# NUEVO: Umbral explícito de hiper-persistencia.
# El pico solo se considera fuerte si, además de los tres componentes altos,
# la tau_s local está > 1 desviación estándar por encima de su media reciente.
HYPER_PERSISTENCE_THRESHOLD = 1.0
HYPER_RECENT_WINDOW = 20          # Ventana para calcular la media reciente de tau_s

# Estilo visual (idéntico a scripts anteriores)
plt.rcParams['figure.dpi'] = 130
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'sans-serif'
sns.set_theme(style="whitegrid", font_scale=1.1)

# Colores consistentes
REGION_COLORS = plt.cm.tab10(np.linspace(0, 1, 4))

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

# Números de la versión ORIGINAL (sin la condición de hiper-persistencia)
# Tomados de las corridas anteriores con exactamente los mismos parámetros.
ORIGINAL_RESULTS = {
    "sj": {
        "n_peaks": 27,
        "n_with_lead": 23,
        "mean_lead": 90.57,
        "mw_p": 0.0995,
        "perm_p": 0.0930,
        "conclusion": "EVIDENCIA A FAVOR"
    },
    "iq": {
        "n_peaks": 17,
        "n_with_lead": 13,
        "mean_lead": 65.77,
        "mw_p": 0.0606,
        "perm_p": 0.0848,
        "conclusion": "TENDENCIA A FAVOR"
    }
}

print("=" * 82)
print("ANÁLISIS REFINADO - PREDICCIÓN 2 (RECD + ESTRUCTURA ESPACIAL)")
print("Definición de pico fuerte MEJORADA con condición explícita de hiper-persistencia")
print(f"Parámetros fijos: TAU={TAU_WINDOW}, COH={COH_WINDOW}, PEAK_Q={PEAK_Q}")
print(f"Umbral hiper-persistencia: hyper_persistence_level > {HYPER_PERSISTENCE_THRESHOLD}")
print(f"Ciudades a analizar: {CITIES_TO_RUN}")
print("=" * 82)


# =============================================================================
# CARGA DE DATOS (SOPORTA AMBAS CIUDADES)
# =============================================================================

def ensure_data():
    if os.path.exists(DATA_PATH):
        return DATA_PATH

    feat_p = os.path.join("data", "dengue_features_train.csv")
    lab_p = os.path.join("data", "dengue_labels_train.csv")
    if os.path.exists(feat_p) and os.path.exists(lab_p):
        print("[DATA] Uniendo archivos originales...")
        feat = pd.read_csv(feat_p)
        lab = pd.read_csv(lab_p)
        merged = pd.merge(feat, lab, on=["city", "year", "weekofyear"], how="left")
        merged = merged.sort_values(["city", "year", "weekofyear"]).reset_index(drop=True)
        merged.to_csv(DATA_PATH, index=False)
        return DATA_PATH

    raise FileNotFoundError(f"No se encontró {DATA_PATH}. Ejecuta prepare_dengai_data.py primero.")


def load_city_data(data_path, city_code):
    """Carga datos para la ciudad indicada ('sj' o 'iq') y construye las regiones."""
    city_name = "San Juan" if city_code == "sj" else "Iquitos"
    print(f"[LOAD] Cargando datos de {city_name} ({city_code}) desde: {data_path}")

    df = pd.read_csv(data_path)
    df = df[df["city"] == city_code].copy()
    df = df.sort_values(["year", "weekofyear"]).reset_index(drop=True)

    min_len_req = 200 if city_code == "sj" else 150
    if len(df) < min_len_req:
        raise ValueError(f"Datos insuficientes para {city_name}.")

    all_needed = set()
    for _, cols in BASE_REGION_DEFINITION:
        all_needed.update(cols)

    cols_to_keep = ["year", "weekofyear"] + [c for c in all_needed if c in df.columns]
    df_clean = df[cols_to_keep].copy()

    df_clean = df_clean.interpolate(method="linear", limit_direction="both").ffill().bfill()
    df_clean = df_clean.dropna().reset_index(drop=True)

    print(f"[LOAD] Semanas después de limpieza para {city_name}: {len(df_clean)}")

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
        raise ValueError(f"No se pudieron construir suficientes regiones para {city_name}.")

    min_len = min(len(r) for r in regions_data)
    regions_data = [r[:min_len] for r in regions_data]

    print(f"[LOAD] Regiones listas para {city_name}: {region_names} | T = {min_len}")
    return regions_data, region_names, city_name


# =============================================================================
# PIPELINE RECD (IDÉNTICO AL ORIGINAL)
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
    """tau_s local (RECD). Alta tau_s = alta persistencia."""
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
    """Calcula todas las métricas con los parámetros fijos."""
    n_reg = len(regions_data)
    T = len(regions_data[0])
    s_reps = [compute_representative(rd) for rd in regions_data]

    # tau_s
    tau_s = np.zeros((n_reg, T))
    for i in range(n_reg):
        for k in range(T):
            tau_s[i, k] = compute_local_tau_s(s_reps[i], k)

    # Coherencias
    C = np.ones((n_reg, n_reg, T))
    for k in range(COH_WINDOW, T):
        for i in range(n_reg):
            for j in range(i + 1, n_reg):
                si = s_reps[i][k - COH_WINDOW + 1 : k + 1]
                sj = s_reps[j][k - COH_WINDOW + 1 : k + 1]
                corr = np.corrcoef(si, sj)[0, 1]
                C[i, j, k] = C[j, i, k] = corr

    # rho
    rho = np.zeros((n_reg, T))
    for k in range(T):
        for i in range(n_reg):
            others = [abs(C[i, j, k]) for j in range(n_reg) if j != i]
            rho[i, k] = np.mean(others) if others else 0.0

    # Peso y Gamma
    peso = np.zeros((n_reg, T))
    gamma = np.zeros((n_reg, T))
    for i in range(n_reg):
        for k in range(T):
            peso[i, k] = tau_s[i, k]
            start = max(0, k - 40 + 1)
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
# DETECCIÓN REFINADA DE PICOS FUERTES (EL CAMBIO CLAVE)
# =============================================================================

def detect_strong_peaks_refined(metrics,
                                q=PEAK_Q,
                                min_dist=PEAK_MIN_DIST,
                                hyper_thresh=HYPER_PERSISTENCE_THRESHOLD,
                                hyper_window=HYPER_RECENT_WINDOW):
    """
    Detecta picos fuertes con la DEFINICIÓN REFINADA.

    Condiciones simultáneas requeridas:
        1. Peso_i(k)   > percentil(q) de la serie de Peso de la región
        2. rho_i(k)    > percentil(q) de la serie de rho
        3. Gamma_i(k)  > percentil(q) de la serie de Gamma
        4. I_i(k)      > percentil(75) de la serie de I (intensidad alta)
        5. hyper_persistence_level(k) > hyper_thresh   <--- NUEVA CONDICIÓN REFINADA

    hyper_persistence_level se calcula como:
        (tau_s_actual - media_tau_ventana_reciente) / std_tau_ventana_reciente

    Esto garantiza que el pico ocurra cuando la región está en un régimen
    de persistencia claramente superior a su comportamiento reciente.
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
            # Condiciones originales de componentes + intensidad
            if (peso[i, k] > p_th and
                rho[i, k] > r_th and
                gamma[i, k] > g_th and
                I[i, k] > i_th):

                # === CONDICIÓN REFINADA DE HIPER-PERSISTENCIA ===
                current_tau = tau_s[i, k]
                start = max(0, k - hyper_window)
                recent_tau = tau_s[i, start : k + 1]
                hyper_level = (current_tau - np.mean(recent_tau)) / (np.std(recent_tau) + 1e-6)

                if hyper_level > hyper_thresh:
                    raw.append((i, k))

    # Thinning (idéntico)
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

    print(f"[DETECT] Picos fuertes REFINADOS detectados: {len(thinned)} "
          f"(hyper_persistence_level > {hyper_thresh})")
    return thinned


def detect_structural_changes(C, percentile=STRUCTURAL_PERCENTILE, min_dist=STRUCTURAL_MIN_DIST):
    """Cambios estructurales mediante distancia de Frobenius (sin cambios)."""
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
    """Detectores de referencia ordinal (sin cambios)."""
    tau_s = metrics["tau_s"]
    s_reps = metrics["s_reps"]
    n_reg, T = tau_s.shape

    # PE multivariada
    pe_multi = np.array([
        np.mean([permutation_entropy(s_reps[i][max(0, k - 60):k + 1]) for i in range(n_reg)])
        for k in range(T)
    ])
    pe_peaks, _ = find_peaks(pe_multi, height=np.percentile(pe_multi[70:], 85), distance=18)
    leads_pe = compute_leads(pe_peaks.tolist(), structural_changes)

    # Varianza de tau_s
    var_tau = np.var(tau_s, axis=0)
    var_peaks, _ = find_peaks(var_tau, height=np.percentile(var_tau[70:], 88), distance=18)
    leads_var = compute_leads(var_peaks.tolist(), structural_changes)

    # Δ tau_s
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
    """Mann-Whitney + permutation test (I_i > otros, una cola)."""
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
# FIGURAS (ACTUALIZADAS CON MENCIÓN A LA DEFINICIÓN REFINADA)
# =============================================================================

def save_all_figures(metrics, strong_peaks, structural_changes, dist_smooth, dist_thresh,
                     leads_I, leads_other, region_names, city_label, output_dir):
    """Genera las 6 figuras con títulos que reflejan la definición refinada."""
    T = metrics["I"].shape[1]
    tau_s = metrics["tau_s"]
    I_mat = metrics["I"]
    C = metrics["C"]
    n_reg = len(region_names)

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
    ax.set_title(f"Figura 1: Series de $\\tau_s$ local por región ({city_label})\n"
                 "Sombreado = hiper-persistencia. Definición REFINADA de picos fuertes.")
    ax.legend(loc="upper right", framealpha=0.95)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig1_tau_s_series.png"), bbox_inches="tight")
    plt.close()
    print("  [FIG] fig1_tau_s_series.png")

    # FIG 2 - clave: mencionar la condición refinada
    fig, ax = plt.subplots(figsize=(11, 5.2))
    for i in range(n_reg):
        ax.plot(I_mat[i], label=region_names[i], color=REGION_COLORS[i], lw=1.5, alpha=0.9)
    for reg, k in strong_peaks:
        ax.scatter(k, I_mat[reg, k], marker="*", s=160, c="black", zorder=7,
                   edgecolors="white", linewidths=0.6)
    for ch in structural_changes:
        ax.axvline(ch, color="crimson", ls="--", alpha=0.55, lw=1.1)
    ax.set_xlabel("Semana (índice k)")
    ax.set_ylabel(r"$I_i(k) = \mathrm{Peso}_i \cdot \rho_i \cdot \Gamma_i$")
    ax.set_title(f"Figura 2: $I_i(k)$ con picos fuertes REFINADOS ({city_label})\n"
                 "Estrellas = picos que cumplen Peso+ρ+Γ altos + hyper_persistence_level > 1.0")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig2_I_intensity.png"), bbox_inches="tight")
    plt.close()
    print("  [FIG] fig2_I_intensity.png")

    # FIG 3
    times_to_plot = []
    if strong_peaks:
        tp = strong_peaks[0][1]
        times_to_plot.append(("Antes del pico refinado", max(COH_WINDOW + 5, tp - 80)))
        times_to_plot.append(("Durante pico fuerte REFINADO", tp))
    if structural_changes:
        tc = structural_changes[0]
        times_to_plot.append(("En cambio estructural", tc))

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
            ax.set_title(f"{lab}\nk = {tk}")
        plt.suptitle(f"Figura 3: Matrices de coherencia $C_{{ij}}(k)$ ({city_label}) - Definición Refinada", y=1.02)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "fig3_coherence_matrices.png"), bbox_inches="tight")
        plt.close()
        print("  [FIG] fig3_coherence_matrices.png")

    # FIG 4
    leads_dict = {"Picos fuertes I_i (refinado)": leads_I, **leads_other}
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
        ax.set_title(f"Figura 4: Distribución de adelantos ({city_label})\n"
                     "Picos fuertes REFINADOS (con hiper-persistencia) vs detectores ordinales")
        plt.xticks(rotation=12, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "fig4_lead_distributions.png"), bbox_inches="tight")
        plt.close()
        print("  [FIG] fig4_lead_distributions.png")

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
        ax.set_title(f"Figura 5: Adelanto medio por método ({city_label})\n"
                     f"Definición REFINADA (hyper > {HYPER_PERSISTENCE_THRESHOLD}) | τ={TAU_WINDOW}, C={COH_WINDOW}, Q={PEAK_Q}")
        plt.xticks(rotation=12, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "fig5_mean_leads.png"), bbox_inches="tight")
        plt.close()
        print("  [FIG] fig5_mean_leads.png")

    # FIG 6
    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    ax.plot(dist_smooth, color="steelblue", lw=1.2, label=r"$\Vert\Delta C\Vert_F$ (suavizada)")
    ax.axhline(dist_thresh, color="gray", ls=":", lw=1.3,
               label=f"Umbral estructural ({STRUCTURAL_PERCENTILE}%)")
    for ch in structural_changes:
        ax.axvline(ch, color="darkred", ls="--", alpha=0.6, lw=1.2)
    for _, k in strong_peaks:
        ax.scatter(k, dist_smooth[k], marker="v", s=90, c="darkorange", zorder=6,
                   edgecolors="white", linewidths=0.4)
    ax.set_xlabel("Semana (índice k)")
    ax.set_ylabel(r"Distancia Frobenius $\Vert C(k) - C(k-1) \Vert_F$")
    ax.set_title(f"Figura 6: Distancia entre matrices de coherencia ({city_label})\n"
                 "Triángulos = picos fuertes REFINADOS (incluye hiper-persistencia)")
    ax.legend(loc="upper right", framealpha=0.92)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig6_coherence_distance.png"), bbox_inches="tight")
    plt.close()
    print("  [FIG] fig6_coherence_distance.png")


# =============================================================================
# EXPORT CSV REFINADO
# =============================================================================

def export_refined_peaks_csv(metrics, strong_peaks, structural_changes, region_names, city_code, output_dir):
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
            "refined_hyper_threshold": HYPER_PERSISTENCE_THRESHOLD,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        })

    df = pd.DataFrame(records)
    suffix = "san_juan" if city_code == "sj" else "iquitos"
    out_path = os.path.join(output_dir, f"picos_fuertes_refinados_{suffix}.csv")
    df.to_csv(out_path, index=False)
    print(f"[EXPORT] CSV refinado guardado: {out_path} ({len(df)} picos)")
    return df


# =============================================================================
# RESÚMENES Y COMPARACIÓN
# =============================================================================

def print_city_summary(city_label, n_peaks, n_changes, leads_I, leads_other, stats_res, output_dir):
    print("\n" + "=" * 82)
    print(f"RESUMEN REFINADO - PREDICCIÓN 2 ({city_label})")
    print(f"Parámetros: TAU={TAU_WINDOW}, COH={COH_WINDOW}, PEAK_Q={PEAK_Q}")
    print(f"Definición de pico: Peso+ρ+Γ > q{PEAK_Q} + I>75 + hyper_persistence_level > {HYPER_PERSISTENCE_THRESHOLD}")
    print("=" * 82)

    print(f"\nPicos fuertes REFINADOS detectados : {n_peaks}")
    print(f"Cambios estructurales detectados   : {n_changes}")

    print("\nAdelantos (solo picos con cambio posterior observado):")
    n_leads = len(leads_I)
    mean_lead = np.mean(leads_I) if n_leads > 0 else np.nan
    print(f"  Picos fuertes I_i (refinado) : {mean_lead:.2f} pasos  (n={n_leads})")

    for name, ls in leads_other.items():
        if len(ls) > 0:
            print(f"  {name:28s}: {np.mean(ls):.2f}  (n={len(ls)})")

    print("\nTest estadístico (I_i refinado vs otros métodos combinados):")
    print(f"  Mann-Whitney (una cola)    : p = {stats_res['mw_p']:.4f}")
    print(f"  Permutation test           : p = {stats_res['perm_p']:.4f}")
    print(f"  Diferencia de medias       : {stats_res['mean_I'] - stats_res['mean_other']:.2f}")

    min_p = min(stats_res['mw_p'], stats_res['perm_p'])
    if n_leads >= 5 and stats_res['mean_I'] > stats_res['mean_other'] and min_p < 0.10:
        conc = "EVIDENCIA A FAVOR (refinado)"
    elif n_leads >= 5 and stats_res['mean_I'] > stats_res['mean_other']:
        conc = "TENDENCIA A FAVOR (refinado)"
    else:
        conc = "Evidencia más débil con la definición refinada"
    print(f"\nConclusión (refinada): {conc}")

    print(f"\nArchivos guardados en: {os.path.abspath(output_dir)}")
    print("=" * 82 + "\n")


def print_comparison_with_original(city_code, city_label, refined_n_peaks, refined_n_leads, refined_mean, refined_mw, refined_perm):
    """Compara los resultados refinados con los de la versión original (hardcodeados)."""
    orig = ORIGINAL_RESULTS[city_code]

    print("\n" + "=" * 82)
    print(f"COMPARACIÓN: DEFINICIÓN ORIGINAL vs REFINADA ({city_label})")
    print("=" * 82)

    print(f"\n{'Métrica':<45} {'Original':>15} {'Refinada':>15} {'Δ / Nota'}")
    print("-" * 80)

    delta_n = refined_n_peaks - orig["n_peaks"]
    print(f"{'Picos fuertes detectados':<45} {orig['n_peaks']:>15} {refined_n_peaks:>15} {delta_n:+d}")

    delta_lead = refined_mean - orig["mean_lead"]
    print(f"{'Adelanto medio (pasos, solo con lead)':<45} {orig['mean_lead']:>15.2f} {refined_mean:>15.2f} {delta_lead:+.2f}")

    print(f"{'p-value Mann-Whitney':<45} {orig['mw_p']:>15.4f} {refined_mw:>15.4f} {'mejor' if refined_mw < orig['mw_p'] else 'peor'}")
    print(f"{'p-value Permutation':<45} {orig['perm_p']:>15.4f} {refined_perm:>15.4f} {'mejor' if refined_perm < orig['perm_p'] else 'peor'}")

    print("\nInterpretación de la refinación (hyper_persistence_level > 1.0):")
    if refined_n_peaks < orig["n_peaks"]:
        print("  - La condición de hiper-persistencia es más selectiva (menos picos).")
    if refined_mean > orig["mean_lead"] + 5:
        print("  - El adelanto medio MEJORÓ notablemente con la condición de hiper-persistencia.")
    elif refined_mean > orig["mean_lead"]:
        print("  - El adelanto medio mejoró ligeramente.")
    else:
        print("  - El adelanto medio no mejoró (o empeoró levemente).")

    if refined_mw < orig["mw_p"] or refined_perm < orig["perm_p"]:
        print("  - Los p-values mejoraron (evidencia estadística más fuerte).")
    else:
        print("  - Los p-values no mejoraron respecto a la definición original.")

    # Conclusión final sobre si la condición ayuda
    print("\nCONCLUSIÓN SOBRE LA REFINACIÓN:")
    if refined_mean > orig["mean_lead"] and (refined_mw < 0.10 or refined_perm < 0.10):
        print("  >> La adición explícita de la condición de hiper-persistencia MEJORA")
        print("     el detector: mayor adelanto y/o mejor significación estadística")
        print("     con un número más reducido pero de mayor calidad de picos.")
    elif refined_mean > orig["mean_lead"]:
        print("  >> La condición de hiper-persistencia produce picos con MAYOR adelanto medio,")
        print("     aunque la significación estadística puede verse afectada por menor n.")
    else:
        print("  >> La condición de hiper-persistencia es más estricta pero en este caso")
        print("     no produjo una mejora clara en adelanto o significación.")
    print("=" * 82 + "\n")


# =============================================================================
# FUNCIÓN PRINCIPAL POR CIUDAD
# =============================================================================

def run_refined_for_city(city_code):
    """Ejecuta el pipeline completo con la definición REFINADA para una ciudad."""
    city_label = "San Juan" if city_code == "sj" else "Iquitos"
    output_dir = f"resultados_refinados_{'san_juan' if city_code == 'sj' else 'iquitos'}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'='*82}")
    print(f"INICIANDO ANÁLISIS REFINADO PARA: {city_label}")
    print(f"Salida: {output_dir}/")
    print(f"{'='*82}")

    # Cargar datos
    regions_data, region_names, _ = load_city_data(DATA_PATH, city_code)

    # Pipeline completo
    print("\n[RUN] Ejecutando pipeline con definición REFINADA de picos fuertes...")
    metrics = compute_all_metrics(regions_data)
    strong_peaks = detect_strong_peaks_refined(metrics)
    struct_changes, dist_smooth, dist_thresh = detect_structural_changes(metrics["C"])

    i_times = [k for _, k in strong_peaks]
    leads_I = compute_leads(i_times, struct_changes)
    leads_other = compute_reference_leads(metrics, struct_changes)
    stats_res = run_statistical_test(leads_I, leads_other)

    # Figuras actualizadas
    print("\n[FIGURAS] Generando 6 figuras (títulos actualizados con refinamiento)...")
    save_all_figures(metrics, strong_peaks, struct_changes, dist_smooth, dist_thresh,
                     leads_I, leads_other, region_names, city_label, output_dir)

    # CSV refinado
    export_refined_peaks_csv(metrics, strong_peaks, struct_changes, region_names, city_code, output_dir)

    # Resumen
    n_peaks = len(strong_peaks)
    n_changes = len(struct_changes)
    mean_lead = np.mean(leads_I) if len(leads_I) > 0 else np.nan

    print_city_summary(city_label, n_peaks, n_changes, leads_I, leads_other, stats_res, output_dir)

    # Comparación con versión original
    print_comparison_with_original(
        city_code, city_label,
        refined_n_peaks=n_peaks,
        refined_n_leads=len(leads_I),
        refined_mean=mean_lead,
        refined_mw=stats_res["mw_p"],
        refined_perm=stats_res["perm_p"]
    )

    return {
        "city": city_code,
        "n_peaks": n_peaks,
        "mean_lead": mean_lead,
        "mw_p": stats_res["mw_p"],
        "perm_p": stats_res["perm_p"]
    }


# =============================================================================
# MAIN
# =============================================================================

def main():
    ensure_data()

    all_results = []
    for city in CITIES_TO_RUN:
        res = run_refined_for_city(city)
        all_results.append(res)

    if len(CITIES_TO_RUN) > 1:
        print("\n" + "=" * 82)
        print("RESUMEN GLOBAL - AMBAS CIUDADES CON DEFINICIÓN REFINADA")
        print("=" * 82)
        for r in all_results:
            lab = "San Juan" if r["city"] == "sj" else "Iquitos"
            print(f"{lab:12s}: {r['n_peaks']:2d} picos | lead medio = {r['mean_lead']:.2f} | MW p={r['mw_p']:.4f}")
        print("=" * 82)

    print("\n✅ Script completado. Recuerda que la definición REFINADA es más estricta")
    print("   (exige hiper-persistencia clara) y por tanto selecciona picos de mayor calidad.")


if __name__ == "__main__":
    main()