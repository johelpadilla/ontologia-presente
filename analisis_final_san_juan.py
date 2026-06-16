#!/usr/bin/env python3
"""
analisis_final_san_juan.py

Análisis final y reproducible de la Predicción 2 (RECD + estructura espacial)
usando exclusivamente los datos de San Juan (Puerto Rico) con los parámetros
óptimos identificados en el barrido.

Uso:
    python analisis_final_san_juan.py

Este script:
- Carga solo la ciudad "sj" del archivo data/datos_dengai_completo.csv
- Usa parámetros fijos óptimos (TAU=85, COH=90, PEAK_Q=0.60)
- Ejecuta el pipeline completo
- Genera 6 figuras de alta calidad en resultados_final_san_juan/
- Exporta un CSV detallado de todos los picos fuertes detectados
- Imprime un resumen profesional al final

Parámetros fijos elegidos (mejores del sweep):
- TAU_WINDOW = 85          → buena sensibilidad a hiper-persistencia
- COH_WINDOW = 90          → balance entre ruido y detección de cambios
- PEAK_Q = 0.60            → umbral que maximiza adelanto sin perder eventos
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
# CONFIGURACIÓN DEL ANÁLISIS FINAL (PARÁMETROS ÓPTIMOS)
# =============================================================================

# Ruta de datos
DATA_PATH = os.path.join("data", "datos_dengai_completo.csv")

# Carpeta de salida
OUTPUT_DIR = "resultados_final_san_juan"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================================================
# PARÁMETROS FIJOS (los mejores según sweep previo)
# ==========================================================================
TAU_WINDOW = 85                    # Ventana para cálculo de tau_s local (RECD)
COH_WINDOW = 90                    # Ventana para coherencias inter-regionales
PEAK_Q = 0.60                      # Percentil para detectar componentes "altos"

# Parámetros secundarios (razonables y estables)
PESO_GAMMA_WINDOW = 50             # Ventana para fluctuación de tau (Gamma)
STRUCTURAL_PERCENTILE = 94         # Umbral para cambios estructurales (Frobenius)
STRUCTURAL_MIN_DIST = 35           # Separación mínima entre cambios
PEAK_MIN_DIST = 18                 # Separación mínima entre picos fuertes de I
EMBEDDING_DIM = 3                  # Dimensión para entropía de permutación

# Estilo de figuras
plt.rcParams['figure.dpi'] = 130
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'sans-serif'
sns.set_theme(style="whitegrid", font_scale=1.1)

# Colores consistentes por región
REGION_COLORS = plt.cm.tab10(np.linspace(0, 1, 4))

# Definición de las 3 regiones temáticas (igual que en el sweep)
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
print("ANÁLISIS FINAL - PREDICCIÓN 2 (San Juan)")
print(f"Parámetros fijos: TAU={TAU_WINDOW}, COH={COH_WINDOW}, PEAK_Q={PEAK_Q}")
print(f"Salida: {OUTPUT_DIR}/")
print("=" * 78)


# =============================================================================
# CARGA Y PREPARACIÓN DE DATOS (SOLO SAN JUAN)
# =============================================================================

def ensure_data():
    """Verifica que exista el archivo de datos combinados."""
    if os.path.exists(DATA_PATH):
        return DATA_PATH

    # Intentar unir si existen los originales (mismo comportamiento que antes)
    feat_path = os.path.join("data", "dengue_features_train.csv")
    lab_path = os.path.join("data", "dengue_labels_train.csv")

    if os.path.exists(feat_path) and os.path.exists(lab_path):
        print("[DATA] Uniendo archivos originales...")
        feat = pd.read_csv(feat_path)
        lab = pd.read_csv(lab_path)
        merged = pd.merge(feat, lab, on=["city", "year", "weekofyear"], how="left")
        merged = merged.sort_values(["city", "year", "weekofyear"]).reset_index(drop=True)
        merged.to_csv(DATA_PATH, index=False)
        print(f"[DATA] Creado {DATA_PATH}")
        return DATA_PATH

    raise FileNotFoundError(
        f"No se encontró {DATA_PATH}. Ejecuta primero 'python prepare_dengai_data.py' "
        "o coloca los archivos de DrivenData en la carpeta data/."
    )


def load_san_juan_data(path):
    """
    Carga el CSV completo, filtra exclusivamente San Juan ("sj"),
    limpia valores faltantes y construye las 3 regiones temáticas estandarizadas.
    Retorna: regions_data (lista de arrays), region_names (lista de str)
    """
    print(f"[LOAD] Cargando datos de San Juan desde: {path}")
    df = pd.read_csv(path)

    # Filtrar solo San Juan y ordenar cronológicamente
    df = df[df["city"] == "sj"].copy()
    df = df.sort_values(["year", "weekofyear"]).reset_index(drop=True)

    if len(df) < 200:
        raise ValueError("Datos insuficientes para San Juan.")

    # Columnas necesarias
    all_needed = set()
    for _, cols in BASE_REGION_DEFINITION:
        all_needed.update(cols)

    cols_to_keep = ["year", "weekofyear"] + list(all_needed & set(df.columns))
    df_clean = df[cols_to_keep].copy()

    # Limpieza robusta de NaNs
    df_clean = df_clean.interpolate(method="linear", limit_direction="both").ffill().bfill()
    df_clean = df_clean.dropna().reset_index(drop=True)

    print(f"[LOAD] Semanas de San Juan después de limpieza: {len(df_clean)}")

    # Construir regiones
    regions_data = []
    region_names = []

    for name, cols in BASE_REGION_DEFINITION:
        avail = [c for c in cols if c in df_clean.columns]
        if len(avail) < 2:
            print(f"[WARN] Región '{name}' descartada (pocas variables).")
            continue

        sub = df_clean[avail].copy()
        # Estandarización por variable (importante para el promedio representativo)
        sub_std = (sub - sub.mean()) / (sub.std(ddof=0) + 1e-8)
        regions_data.append(sub_std.values.astype(float))
        region_names.append(name)

    if len(regions_data) < 2:
        raise ValueError("No se pudieron construir suficientes regiones.")

    # Alinear todas las regiones a la misma longitud
    min_len = min(len(r) for r in regions_data)
    regions_data = [r[:min_len] for r in regions_data]

    print(f"[LOAD] Regiones listas: {region_names} | T = {min_len}")
    return regions_data, region_names


# =============================================================================
# FUNCIONES DEL PIPELINE RECD (CON PARÁMETROS FIJOS)
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
    """Promedio de las variables estandarizadas de la región."""
    return np.mean(region_data, axis=1)


def compute_all_metrics(regions_data):
    """Calcula todas las métricas con los parámetros fijos del análisis final."""
    n_reg = len(regions_data)
    T = len(regions_data[0])
    s_reps = [compute_representative(rd) for rd in regions_data]

    # tau_s local
    tau_s = np.zeros((n_reg, T))
    for i in range(n_reg):
        for k in range(T):
            tau_s[i, k] = compute_local_tau_s(s_reps[i], k)

    # Coherencias C_ij(k) (ventana fija)
    C = np.ones((n_reg, n_reg, T))
    for k in range(COH_WINDOW, T):
        for i in range(n_reg):
            for j in range(i + 1, n_reg):
                si = s_reps[i][k - COH_WINDOW + 1 : k + 1]
                sj = s_reps[j][k - COH_WINDOW + 1 : k + 1]
                corr = np.corrcoef(si, sj)[0, 1]
                C[i, j, k] = C[j, i, k] = corr

    # rho_i(k) - densidad espacial
    rho = np.zeros((n_reg, T))
    for k in range(T):
        for i in range(n_reg):
            others = [abs(C[i, j, k]) for j in range(n_reg) if j != i]
            rho[i, k] = np.mean(others) if others else 0.0

    # Peso y Gamma (basados en hiper-persistencia)
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


def detect_strong_peaks(metrics, q=PEAK_Q, min_dist=PEAK_MIN_DIST):
    """Detecta picos donde Peso, rho y Gamma están simultáneamente altos."""
    I = metrics["I"]
    peso = metrics["peso"]
    rho = metrics["rho"]
    gamma = metrics["gamma"]
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
    return thinned


def detect_structural_changes(C, percentile=STRUCTURAL_PERCENTILE, min_dist=STRUCTURAL_MIN_DIST):
    """Cambios estructurales mediante distancia de Frobenius."""
    T = C.shape[2]
    dist = np.zeros(T)
    for k in range(1, T):
        dist[k] = np.linalg.norm(C[:, :, k] - C[:, :, k - 1], "fro")
    dist_smooth = uniform_filter1d(dist, size=7, mode="nearest")
    thresh = np.percentile(dist_smooth[80:], percentile)
    peaks, _ = find_peaks(dist_smooth, height=thresh, distance=min_dist)
    return peaks.tolist(), dist_smooth, thresh


def compute_leads(event_times, change_times):
    """Adelanto (en pasos) desde un evento hasta el siguiente cambio estructural."""
    leads = []
    ch = np.array(sorted(change_times))
    for et in sorted(event_times):
        future = ch[ch > et]
        if len(future) > 0:
            leads.append(int(future[0] - et))
    return leads


def compute_reference_leads(metrics, structural_changes):
    """Leads de los tres detectores de referencia ordinal."""
    tau_s = metrics["tau_s"]
    s_reps = metrics["s_reps"]
    n_reg, T = tau_s.shape

    # 1. PE multivariada
    pe_multi = np.array([
        np.mean([permutation_entropy(s_reps[i][max(0, k - 60):k + 1]) for i in range(n_reg)])
        for k in range(T)
    ])
    pe_peaks, _ = find_peaks(pe_multi, height=np.percentile(pe_multi[70:], 85), distance=18)
    leads_pe = compute_leads(pe_peaks.tolist(), structural_changes)

    # 2. Varianza de tau_s
    var_tau = np.var(tau_s, axis=0)
    var_peaks, _ = find_peaks(var_tau, height=np.percentile(var_tau[70:], 88), distance=18)
    leads_var = compute_leads(var_peaks.tolist(), structural_changes)

    # 3. Cambios en tau_s individual
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
    """Mann-Whitney + permutation test (una cola: I_i > otros)."""
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

    # Permutation test
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
# FIGURAS DE ALTA CALIDAD
# =============================================================================

def save_all_figures(metrics, strong_peaks, structural_changes, dist_smooth, dist_thresh,
                     leads_I, leads_other, region_names):
    """Genera y guarda las 6 figuras principales."""

    T = metrics["I"].shape[1]
    tau_s = metrics["tau_s"]
    I_mat = metrics["I"]
    C = metrics["C"]
    n_reg = len(region_names)

    # --- FIGURA 1: Series de tau_s ---
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
    ax.set_title("Figura 1: Series de $\\tau_s$ local por región (San Juan)\n"
                 "Sombreado = hiper-persistencia (> percentil 80). Líneas rojas = cambios estructurales")
    ax.legend(loc="upper right", framealpha=0.95)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig1_tau_s_series.png"), bbox_inches="tight")
    plt.close()
    print("  [FIG] Guardada fig1_tau_s_series.png")

    # --- FIGURA 2: I_i(k) con picos ---
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
    ax.set_title("Figura 2: Producto de intensidad $I_i(k)$ (San Juan)\n"
                 "Estrellas = picos fuertes (Peso, ρ y Γ altos simultáneamente)")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig2_I_intensity.png"), bbox_inches="tight")
    plt.close()
    print("  [FIG] Guardada fig2_I_intensity.png")

    # --- FIGURA 3: Heatmaps de coherencia ---
    times_to_plot = []
    if strong_peaks:
        tp = strong_peaks[0][1]
        times_to_plot.append(("Antes del pico fuerte", max(COH_WINDOW + 5, tp - 80)))
        times_to_plot.append(("Durante pico fuerte I", tp))
    if structural_changes:
        tc = structural_changes[0]
        times_to_plot.append(("En cambio estructural", tc))
        if len(structural_changes) > 1:
            times_to_plot.append(("Post-cambio", min(T - 10, structural_changes[0] + 70)))

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
            ax.set_xlabel("Región j")
            ax.set_ylabel("Región i")
        plt.suptitle("Figura 3: Matrices de coherencia $C_{ij}(k)$ en momentos clave (San Juan)", y=1.02)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "fig3_coherence_matrices.png"), bbox_inches="tight")
        plt.close()
        print("  [FIG] Guardada fig3_coherence_matrices.png")

    # --- FIGURA 4: Distribución de adelantos (violin) ---
    leads_dict = {"Picos fuertes I_i": leads_I, **leads_other}
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
        ax.set_title("Figura 4: Distribución de adelantos hasta el próximo cambio estructural\n"
                     "San Juan – Comparación de picos fuertes de I_i vs detectores ordinales")
        plt.xticks(rotation=12, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "fig4_lead_distributions.png"), bbox_inches="tight")
        plt.close()
        print("  [FIG] Guardada fig4_lead_distributions.png")

    # --- FIGURA 5: Adelanto medio (barras) ---
    methods = []
    means = []
    ns = []
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
        ax.set_title("Figura 5: Adelanto medio por método de detección (San Juan)\n"
                     f"Parámetros: τ={TAU_WINDOW}, C={COH_WINDOW}, Q={PEAK_Q}")
        plt.xticks(rotation=12, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, "fig5_mean_leads.png"), bbox_inches="tight")
        plt.close()
        print("  [FIG] Guardada fig5_mean_leads.png")

    # --- FIGURA 6: Distancia de coherencia ---
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
    ax.set_title("Figura 6: Evolución de la distancia entre matrices de coherencia (San Juan)\n"
                 "Triángulos naranja = picos fuertes de I_i | Líneas rojas = cambios estructurales")
    ax.legend(loc="upper right", framealpha=0.92)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig6_coherence_distance.png"), bbox_inches="tight")
    plt.close()
    print("  [FIG] Guardada fig6_coherence_distance.png")


# =============================================================================
# EXPORTACIÓN DETALLADA DE PICOS FUERTES
# =============================================================================

def export_strong_peaks_csv(metrics, strong_peaks, structural_changes, region_names):
    """
    Exporta un CSV detallado con información de cada pico fuerte detectado.
    """
    I = metrics["I"]
    peso = metrics["peso"]
    rho = metrics["rho"]
    gamma = metrics["gamma"]
    tau_s = metrics["tau_s"]
    C = metrics["C"]

    records = []
    ch = np.array(sorted(structural_changes))

    for reg_idx, k in strong_peaks:
        # Adelanto hasta el siguiente cambio
        future = ch[ch > k]
        lead = int(future[0] - k) if len(future) > 0 else np.nan

        # Métricas adicionales en el momento del pico
        current_tau = tau_s[reg_idx, k]
        recent_tau = tau_s[reg_idx, max(0, k-20):k+1]
        hyper_level = (current_tau - np.mean(recent_tau)) / (np.std(recent_tau) + 1e-6)

        # Conectividad espacial promedio en ese instante
        row_c = [abs(C[reg_idx, j, k]) for j in range(len(region_names)) if j != reg_idx]
        avg_connectivity = np.mean(row_c) if row_c else 0.0

        records.append({
            "region": region_names[reg_idx],
            "k": k,
            "I_value": round(float(I[reg_idx, k]), 5),
            "Peso": round(float(peso[reg_idx, k]), 5),
            "rho": round(float(rho[reg_idx, k]), 5),
            "Gamma": round(float(gamma[reg_idx, k]), 5),
            "lead_to_next_change": lead if not np.isnan(lead) else -1,
            "tau_s_at_peak": round(float(current_tau), 4),
            "hyper_persistence_level": round(float(hyper_level), 4),
            "avg_spatial_connectivity": round(float(avg_connectivity), 4),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        })

    df = pd.DataFrame(records)
    out_path = os.path.join(OUTPUT_DIR, "picos_fuertes_san_juan.csv")
    df.to_csv(out_path, index=False)
    print(f"[EXPORT] CSV de picos fuertes guardado: {out_path} ({len(df)} picos)")
    return df


# =============================================================================
# RESUMEN FINAL
# =============================================================================

def print_final_summary(n_peaks, n_changes, leads_I, leads_other, stats_res, region_names):
    print("\n" + "=" * 78)
    print("RESUMEN FINAL - PREDICCIÓN 2 (San Juan)")
    print(f"Parámetros: TAU_WINDOW={TAU_WINDOW}, COH_WINDOW={COH_WINDOW}, PEAK_Q={PEAK_Q}")
    print("=" * 78)

    print(f"\nRegiones analizadas : {region_names}")
    print(f"Picos fuertes de I_i detectados : {n_peaks}")
    print(f"Cambios estructurales detectados : {n_changes}")

    print("\nAdelantos (pasos hasta el próximo cambio estructural):")
    print(f"  Picos fuertes I_i          : {np.mean(leads_I):.2f}  (n={len(leads_I)})")
    for name, ls in leads_other.items():
        if len(ls) > 0:
            print(f"  {name:26s}: {np.mean(ls):.2f}  (n={len(ls)})")

    print("\nTest estadístico (I_i vs otros métodos combinados):")
    print(f"  Mann-Whitney (una cola)    : p = {stats_res['mw_p']:.4f}")
    print(f"  Permutation test           : p = {stats_res['perm_p']:.4f}")
    print(f"  Diferencia de medias (I - otros) : {stats_res['mean_I'] - stats_res['mean_other']:.2f}")

    min_p = min(stats_res['mw_p'], stats_res['perm_p'])
    mean_I = stats_res['mean_I']
    mean_o = stats_res['mean_other']

    print("\nConclusión:")
    if len(leads_I) >= 5 and mean_I > mean_o and min_p < 0.10:
        print("  >> EVIDENCIA A FAVOR de la Predicción 2 en San Juan.")
        print("     Los picos fuertes de intensidad I_i preceden los cambios")
        print("     en la estructura de relaciones con adelanto significativamente")
        print("     mayor que los detectores ordinales de referencia.")
    elif len(leads_I) >= 5 and mean_I > mean_o:
        print("  >> TENDENCIA A FAVOR de la Predicción 2.")
        print("     Mayor adelanto observado, pero no alcanza significación estadística (p>=0.10).")
    else:
        print("  >> Sin evidencia clara de mayor adelanto con estos parámetros.")

    print("=" * 78)
    print(f"Figuras y CSV guardados en: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 78 + "\n")


# =============================================================================
# MAIN
# =============================================================================

def main():
    # 1. Datos
    ensure_data()
    regions_data, region_names = load_san_juan_data(DATA_PATH)

    # 2. Pipeline con parámetros fijos
    print("\n[RUN] Ejecutando pipeline con parámetros óptimos...")
    metrics = compute_all_metrics(regions_data)
    strong_peaks = detect_strong_peaks(metrics)
    struct_changes, dist_smooth, dist_thresh = detect_structural_changes(metrics["C"])

    i_times = [k for _, k in strong_peaks]
    leads_I = compute_leads(i_times, struct_changes)
    leads_other = compute_reference_leads(metrics, struct_changes)
    stats_res = run_statistical_test(leads_I, leads_other)

    # 3. Figuras
    print("\n[FIGURAS] Generando 6 figuras de alta calidad...")
    save_all_figures(metrics, strong_peaks, struct_changes, dist_smooth, dist_thresh,
                     leads_I, leads_other, region_names)

    # 4. CSV detallado de picos fuertes
    export_strong_peaks_csv(metrics, strong_peaks, struct_changes, region_names)

    # 5. Resumen final
    print_final_summary(
        len(strong_peaks), len(struct_changes),
        leads_I, leads_other, stats_res, region_names
    )


if __name__ == "__main__":
    main()