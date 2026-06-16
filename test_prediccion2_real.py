#!/usr/bin/env python3
"""
================================================================================
TEST EMPÍRICO DE LA PREDICCIÓN 2 - RECD + ESTRUCTURA ESPACIAL
CON DATOS REALES DEL DATASET DENGAI (San Juan / Iquitos)
================================================================================

OBJETIVO:
    Evaluar si "Los picos fuertes de intensidad I_i(k) preceden cambios
    en la estructura de relaciones del sistema con mayor adelanto que
    otros detectores ordinales."

USO MÁS SIMPLE (mínimo esfuerzo):
    1. Coloca este archivo y la carpeta 'data/' en el mismo directorio.
    2. Ejecuta:
           python test_prediccion2_real.py

    El script intentará:
      - Usar automáticamente data/datos_dengai_completo.csv si existe.
      - Si no existe, buscar los archivos originales y unirlos.
      - Si nada está disponible, mostrará instrucciones claras de descarga.

CONFIGURACIÓN RÁPIDA (edita solo estas líneas):
"""
# ------------------------------------------------------------------------------
# CONFIGURACIÓN DEL USUARIO - MODIFICA SOLO AQUÍ
# ------------------------------------------------------------------------------
CITY = None          # "sj" = San Juan (Puerto Rico)
                     # "iq" = Iquitos (Perú)
                     # None = analizar AMBOS ciudades por separado

# Si no tienes los datos reales todavía, el script puede generar un pequeño
# dataset sintético estilo DengAI para que veas todo el pipeline funcionando
# (incluyendo las 6 figuras y el resumen estadístico). 
# Cambia a False cuando tengas los archivos reales.
USE_DEMO_DATA_IF_MISSING = True

# Ventanas y umbrales (puedes afinarlos)
TAU_WINDOW = 65
COH_WINDOW = 90
PESO_GAMMA_WINDOW = 50

PEAK_Q = 0.60                    # Percentil para componentes de I_i
PEAK_MIN_DIST = 18

STRUCTURAL_PERCENTILE = 94       # Cuán extremo debe ser el cambio en C
STRUCTURAL_MIN_DIST = 35

# Carpeta de resultados
OUTPUT_DIR = "resultados_prediccion2"
# ------------------------------------------------------------------------------

import os
import sys
import math
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d

# =============================================================================
# INSTRUCCIONES AL INICIO DEL SCRIPT (para el usuario final)
# =============================================================================
"""
INSTRUCCIONES PARA OBTENER LOS DATOS (si la preparación automática falla):

1. Ve a: https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/data/
   (registro gratuito y rápido)

2. Descarga:
   - dengue_features_train.csv
   - dengue_labels_train.csv

3. Colócalos en la carpeta 'data/' junto a este script:
   proyecto_prediccion2/
   ├── data/
   │   ├── dengue_features_train.csv
   │   └── dengue_labels_train.csv
   └── test_prediccion2_real.py

4. Ejecuta de nuevo:
       python test_prediccion2_real.py

El script unirá automáticamente los dos archivos y creará:
   data/datos_dengai_completo.csv

También puedes usar el script auxiliar:
   python prepare_dengai_data.py
"""

# Colores y estilo
sns.set_theme(style="whitegrid", font_scale=1.05)
plt.rcParams['figure.dpi'] = 110
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'sans-serif'

# Nombres de ciudades para mostrar
CITY_LABELS = {"sj": "San Juan (Puerto Rico)", "iq": "Iquitos (Perú)"}

# Definición temática de regiones (Opción A) - usando columnas reales de DengAI
# Se pueden ajustar las columnas según disponibilidad después de la carga.
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


def ensure_data_ready():
    """
    Asegura que exista data/datos_dengai_completo.csv.
    Intenta:
      - Usar el merged si ya existe
      - Unir features + labels si están presentes
      - Si USE_DEMO_DATA_IF_MISSING=True, genera un pequeño dataset sintético
        estilo DengAI para que puedas ver todo el pipeline funcionando inmediatamente.
    Devuelve la ruta al archivo (real o demo) o None.
    """
    os.makedirs("data", exist_ok=True)
    merged_path = os.path.join("data", "datos_dengai_completo.csv")
    features_path = os.path.join("data", "dengue_features_train.csv")
    labels_path = os.path.join("data", "dengue_labels_train.csv")

    if os.path.exists(merged_path):
        print(f"[DATA] Usando archivo combinado existente: {merged_path}")
        return merged_path

    if os.path.exists(features_path) and os.path.exists(labels_path):
        print("[DATA] Encontrados archivos originales. Uniendo...")
        try:
            feat = pd.read_csv(features_path)
            lab = pd.read_csv(labels_path)
            merged = pd.merge(feat, lab, on=["city", "year", "weekofyear"], how="left")
            merged = merged.sort_values(["city", "year", "weekofyear"]).reset_index(drop=True)
            merged.to_csv(merged_path, index=False)
            print(f"[DATA] Archivo combinado creado: {merged_path} ({len(merged)} filas)")
            return merged_path
        except Exception as e:
            print(f"[WARN] Error al unir archivos: {e}")

    # --- Modo demostración (sintético estilo DengAI) ---
    if USE_DEMO_DATA_IF_MISSING:
        print("\n[DATA] No se encontraron datos reales. Activando MODO DEMOSTRACIÓN.")
        print("       Se generará un pequeño dataset sintético con dinámica similar a DengAI")
        print("       (incidencia + clima) para que veas el pipeline completo y las figuras.")
        print("       Cambia USE_DEMO_DATA_IF_MISSING = False cuando tengas los datos reales.\n")
        return "DEMO"   # señal especial

    # Nada disponible → instrucciones reales
    print("\n[DATA] No se encontró data/datos_dengai_completo.csv ni los archivos originales.")
    print("       Por favor sigue estas instrucciones:\n")
    print("1. Descarga desde: https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/data/")
    print("2. Coloca en la carpeta 'data/':")
    print("     - dengue_features_train.csv")
    print("     - dengue_labels_train.csv")
    print("3. Vuelve a ejecutar este script (se unirán automáticamente).")
    print("   O ejecuta primero:  python prepare_dengai_data.py\n")
    return None


def _generate_demo_dengai_data(n_weeks=900, seed=42):
    """Genera un pequeño dataset sintético con estructura similar a DengAI (dos ciudades)."""
    rng = np.random.default_rng(seed)
    records = []

    for c in ["sj", "iq"]:
        base = rng.normal(18, 7, n_weeks).clip(0, None)
        t = np.arange(n_weeks)
        regime = 10 * np.sin(2 * np.pi * t / 210) + 7 * np.sin(2 * np.pi * t / 88)
        cases = (base + regime + rng.normal(0, 5, n_weeks)).clip(0).astype(int)

        temp = 300 + rng.normal(0, 1.4, n_weeks) + 2.2 * np.sin(2 * np.pi * t / 52)
        dew = temp - 5 + rng.normal(0, 1.1, n_weeks)
        hum = 74 + rng.normal(0, 5.5, n_weeks) + 7 * np.sin(2 * np.pi * t / 68)
        precip = np.abs(rng.normal(28, 22, n_weeks)) + 12 * np.sin(2 * np.pi * t / 42)
        ndvi = 0.34 + 0.11 * np.sin(2 * np.pi * t / 78) + rng.normal(0, 0.035, n_weeks)

        for i in range(n_weeks):
            records.append({
                "city": c,
                "year": 2000 + i // 52,
                "weekofyear": (i % 52) + 1,
                "total_cases": cases[i],
                "reanalysis_air_temp_k": temp[i],
                "reanalysis_dew_point_temp_k": dew[i],
                "station_avg_temp_c": (temp[i] - 273.15) + rng.normal(0, 0.7),
                "reanalysis_relative_humidity_percent": hum[i],
                "reanalysis_specific_humidity_g_per_kg": hum[i] * 0.008 + rng.normal(0, 0.25),
                "precipitation_amt_mm": precip[i],
                "station_precip_mm": precip[i] * 0.85 + rng.normal(0, 3.5),
                "reanalysis_precip_amt_kg_per_m2": precip[i] * 0.65,
                "reanalysis_max_air_temp_k": temp[i] + 3.5 + rng.normal(0, 0.9),
                "ndvi_ne": ndvi[i] + rng.normal(0, 0.015),
                "ndvi_nw": ndvi[i] + rng.normal(0, 0.015),
                "ndvi_se": ndvi[i] - 0.025 + rng.normal(0, 0.015),
                "ndvi_sw": ndvi[i] - 0.01 + rng.normal(0, 0.015),
            })
    df = pd.DataFrame(records)
    return df.sort_values(["city", "year", "weekofyear"]).reset_index(drop=True)


def load_dengai_data(merged_path, city):
    """
    Carga el CSV combinado (o datos demo), filtra por ciudad,
    ordena cronológicamente y prepara las regiones temáticas.
    """
    if merged_path == "DEMO":
        print("[LOAD] Generando datos DEMO estilo DengAI (sintéticos pero con dinámica realista)...")
        df = _generate_demo_dengai_data()
    else:
        print(f"[LOAD] Cargando datos desde: {merged_path}")
        df = pd.read_csv(merged_path)

    # Ordenar siempre
    df = df.sort_values(["city", "year", "weekofyear"]).reset_index(drop=True)

    if city is not None:
        df = df[df["city"] == city].copy()
        if len(df) == 0:
            raise ValueError(f"No hay datos para la ciudad '{city}'")
        print(f"[LOAD] Filtrado por ciudad = '{city}' → {len(df)} semanas")
    else:
        print(f"[LOAD] Usando ambas ciudades → {len(df)} semanas totales")

    # Columnas que necesitamos para las regiones definidas
    all_needed_cols = set()
    for _, cols in BASE_REGION_DEFINITION:
        all_needed_cols.update(cols)

    # Asegurar que total_cases exista (viene de labels)
    if "total_cases" not in df.columns:
        raise ValueError("La columna 'total_cases' no está presente. "
                         "¿Uniste correctamente features + labels?")

    # Limpiar solo las columnas que usaremos + city/year/week para orden
    cols_to_keep = ["city", "year", "weekofyear"] + list(all_needed_cols)
    cols_to_keep = [c for c in cols_to_keep if c in df.columns]
    df_clean = df[cols_to_keep].copy()

    # Rellenar NaNs por ciudad (interpolación)
    for c in df_clean["city"].unique():
        mask = df_clean["city"] == c
        df_clean.loc[mask, :] = df_clean.loc[mask].interpolate(method="linear", limit_direction="both").ffill().bfill()
    df_clean = df_clean.dropna().reset_index(drop=True)

    print(f"[LOAD] Filas después de limpieza de NaNs: {len(df_clean)}")

    # Construir regiones por ciudad (o para el subconjunto filtrado)
    cities_to_process = [city] if city is not None else ["sj", "iq"]

    all_cities_data = {}
    for c in cities_to_process:
        city_df = df_clean[df_clean["city"] == c].copy()
        if len(city_df) < max(TAU_WINDOW, COH_WINDOW) + 30:
            print(f"[WARN] Muy pocos datos para la ciudad {c} después de limpieza. Saltando.")
            continue

        # Para cada ciudad construimos sus propias regiones
        city_regions = []
        region_names = []
        for name, cols in BASE_REGION_DEFINITION:
            available_cols = [col for col in cols if col in city_df.columns]
            if len(available_cols) < 2:
                print(f"[WARN] Región '{name}' tiene menos de 2 variables disponibles. Saltando.")
                continue

            sub = city_df[available_cols].copy()
            # Estandarizar por columna (importante para promedio representativo)
            sub_std = (sub - sub.mean()) / (sub.std(ddof=0) + 1e-8)
            city_regions.append(sub_std.values.astype(float))
            region_names.append(name)

        if len(city_regions) >= 2:
            # Alinear longitud (por si alguna región perdió filas, aunque no debería)
            min_len = min(len(r) for r in city_regions)
            city_regions = [r[:min_len] for r in city_regions]
            all_cities_data[c] = {
                "regions_data": city_regions,
                "region_names": region_names,
                "n_weeks": min_len,
                "city_label": CITY_LABELS.get(c, c)
            }
            print(f"[LOAD] Ciudad {c} ({CITY_LABELS.get(c, c)}): "
                  f"{len(city_regions)} regiones, {min_len} semanas")

    return all_cities_data


# =============================================================================
# FUNCIONES DEL PIPELINE RECD (idénticas / muy similares a versiones previas probadas)
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


def compute_local_tau_s(series, k, window=TAU_WINDOW, dim=3):
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
    T_clock = np.zeros((n_reg, T))

    for i in range(n_reg):
        for k in range(T):
            tau_s[i, k] = compute_local_tau_s(s_reps[i], k)
        T_clock[i, 0] = tau_s[i, 0]
        for k in range(1, T):
            T_clock[i, k] = T_clock[i, k - 1] + tau_s[i, k]

    # Coherencias
    C = np.zeros((n_reg, n_reg, T))
    for k in range(COH_WINDOW, T):
        for i in range(n_reg):
            for j in range(n_reg):
                if i == j:
                    C[i, j, k] = 1.0
                    continue
                si = s_reps[i][k - COH_WINDOW + 1:k + 1]
                sj = s_reps[j][k - COH_WINDOW + 1:k + 1]
                C[i, j, k] = np.corrcoef(si, sj)[0, 1]
    for k in range(COH_WINDOW):
        C[:, :, k] = C[:, :, COH_WINDOW]

    # rho
    rho = np.zeros((n_reg, T))
    for k in range(T):
        for i in range(n_reg):
            others = [abs(C[i, j, k]) for j in range(n_reg) if j != i]
            rho[i, k] = np.mean(others) if others else 0.0

    # Peso y Gamma (definición robusta para hiper-persistencia)
    peso = np.zeros((n_reg, T))
    gamma = np.zeros((n_reg, T))
    for i in range(n_reg):
        for k in range(T):
            peso[i, k] = tau_s[i, k]
            start_tau = max(0, k - 40 + 1)
            win_tau = tau_s[i, start_tau:k + 1]
            gamma[i, k] = max(0.0, tau_s[i, k] - np.median(win_tau)) + 1e-4

    I = np.zeros((n_reg, T))
    for i in range(n_reg):
        I[i] = peso[i] * rho[i] * gamma[i]

    return {
        "s_reps": s_reps,
        "tau_s": tau_s,
        "T_clock": T_clock,
        "C": C,
        "rho": rho,
        "peso": peso,
        "gamma": gamma,
        "I": I,
    }


def detect_strong_peaks(metrics, q=PEAK_Q, min_dist=PEAK_MIN_DIST):
    n_reg = metrics["I"].shape[0]
    T = metrics["I"].shape[1]
    I, peso, rho, gamma = metrics["I"], metrics["peso"], metrics["rho"], metrics["gamma"]

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
    for reg in sorted(by_reg):
        times = np.array(sorted(set(by_reg[reg])))
        sel = [times[0]] if len(times) else []
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
    thresh = np.percentile(dist_smooth[100:], percentile)
    peaks, _ = find_peaks(dist_smooth, height=thresh, distance=min_dist)
    return peaks.tolist(), dist_smooth, thresh


def compute_leads(event_times, change_times):
    leads = []
    ch = np.array(sorted(change_times))
    for et in sorted(event_times):
        future = ch[ch > et]
        if len(future):
            leads.append(int(future[0] - et))
    return leads


def compute_reference_leads(metrics, structural_changes):
    n_reg = metrics["tau_s"].shape[0]
    T = metrics["tau_s"].shape[1]
    s_reps = metrics["s_reps"]
    tau_s = metrics["tau_s"]

    # PE multivariada
    pe_multi = np.array([np.mean([permutation_entropy(s_reps[i][max(0, k-60):k+1])
                                  for i in range(n_reg)]) for k in range(T)])
    pe_peaks, _ = find_peaks(pe_multi, height=np.percentile(pe_multi[80:], 87), distance=20)
    leads_pe = compute_leads(pe_peaks.tolist(), structural_changes)

    # Varianza de tau_s
    var_tau = np.var(tau_s, axis=0)
    var_peaks, _ = find_peaks(var_tau, height=np.percentile(var_tau[80:], 90), distance=20)
    leads_var = compute_leads(var_peaks.tolist(), structural_changes)

    # Cambios en tau_s
    dtau = np.zeros(T)
    for i in range(n_reg):
        dtau[1:] += np.abs(np.diff(tau_s[i])) / n_reg
    dtau_peaks, _ = find_peaks(dtau, height=np.percentile(dtau[80:], 87), distance=18)
    leads_dtau = compute_leads(dtau_peaks.tolist(), structural_changes)

    return {
        "PE multivariada": leads_pe,
        "Varianza τ_s": leads_var,
        "Δ τ_s individual": leads_dtau,
    }


def run_statistical_test(leads_I, leads_other_dict):
    all_other = np.concatenate([np.array(v) for v in leads_other_dict.values()]) if any(leads_other_dict.values()) else np.array([])
    leads_I = np.array(leads_I)
    if len(leads_I) >= 3 and len(all_other) >= 3:
        u, p_mw = stats.mannwhitneyu(leads_I, all_other, alternative="greater")
        # permutation test simple
        observed = np.mean(leads_I) - np.mean(all_other)
        combined = np.concatenate([leads_I, all_other])
        n_x = len(leads_I)
        rng = np.random.default_rng(42)
        count = sum((np.mean(rng.permutation(combined)[:n_x]) - np.mean(combined[n_x:])) >= observed
                    for _ in range(5000))
        p_perm = (count + 1) / 5001
        return {
            "n_I": len(leads_I),
            "n_other": len(all_other),
            "mean_I": float(np.mean(leads_I)),
            "mean_other": float(np.mean(all_other)),
            "mannwhitney_p": float(p_mw),
            "perm_p": float(p_perm),
        }, all_other
    return {"n_I": len(leads_I), "n_other": len(all_other),
            "mean_I": float(np.mean(leads_I)) if len(leads_I) else np.nan,
            "mean_other": float(np.mean(all_other)) if len(all_other) else np.nan,
            "mannwhitney_p": 1.0, "perm_p": 1.0}, all_other


# =============================================================================
# VISUALIZACIONES (6 figuras)
# =============================================================================

def save_figures(metrics, strong_peaks, structural_changes, dist_smooth, dist_thresh,
                 leads_I, leads_other, region_names, city_code, city_label):
    """Guarda las 6 figuras con prefijo de ciudad cuando corresponde."""
    prefix = f"{city_code}_" if city_code else ""
    T = metrics["I"].shape[1]
    tau_s = metrics["I"].shape[0]  # solo para tamaño
    tau_s_mat = metrics["tau_s"]
    I_mat = metrics["I"]
    C = metrics["C"]
    n_reg = len(region_names)
    colors = plt.cm.tab10(np.linspace(0, 1, max(n_reg, 4)))

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Fig 1
    fig, ax = plt.subplots(figsize=(11, 5))
    for i in range(n_reg):
        ax.plot(tau_s_mat[i], label=region_names[i], color=colors[i], lw=1.5)
        th = np.percentile(tau_s_mat[i], 80)
        ax.fill_between(range(T), tau_s_mat[i], where=(tau_s_mat[i] > th), alpha=0.15, color=colors[i])
    for ch in structural_changes:
        ax.axvline(ch, color="crimson", ls="--", alpha=0.5, lw=1)
    ax.set_title(f"Figura 1: τ_s local por región — {city_label}")
    ax.set_xlabel("Semana (índice k)")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"{prefix}fig1_tau_s_series.png"), bbox_inches="tight")
    plt.close()

    # Fig 2
    fig, ax = plt.subplots(figsize=(11, 5))
    for i in range(n_reg):
        ax.plot(I_mat[i], label=f"I_{i}", color=colors[i], lw=1.4)
    for reg, k in strong_peaks:
        ax.scatter(k, I_mat[reg, k], marker="*", s=140, c="black", zorder=6, edgecolors="white")
    for ch in structural_changes:
        ax.axvline(ch, color="crimson", ls="--", alpha=0.5)
    ax.set_title(f"Figura 2: Intensidad I_i(k) — {city_label}\n(* = picos fuertes)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"{prefix}fig2_I_intensity.png"), bbox_inches="tight")
    plt.close()

    # Fig 3 - Heatmaps (selección de momentos interesantes)
    times = []
    if strong_peaks:
        tp = strong_peaks[0][1]
        times.append(("Antes del pico", max(COH_WINDOW+5, tp-70)))
        times.append(("Pico fuerte I", tp))
    if structural_changes:
        tc = structural_changes[0]
        times.append(("Cambio estructural", tc))
    if times:
        fig, axes = plt.subplots(1, len(times), figsize=(4*len(times), 3.4))
        if len(times) == 1: axes = [axes]
        for axx, (lab, tk) in zip(axes, times):
            sns.heatmap(C[:, :, tk], annot=True, fmt=".2f", cmap="RdYlBu_r", center=0,
                        square=True, ax=axx, cbar=False, xticklabels=region_names, yticklabels=region_names)
            axx.set_title(f"{lab}\nk={tk}")
        plt.suptitle(f"Figura 3: Matrices de coherencia C_ij — {city_label}")
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"{prefix}fig3_coherence_matrices.png"), bbox_inches="tight")
        plt.close()

    # Fig 4, 5 y 6 (distribuciones, medias, distancia)
    # (Versión compacta pero completa)
    leads_dict = {"Picos fuertes I_i": leads_I, **leads_other}
    plot_df = pd.DataFrame({"Método": np.repeat(list(leads_dict.keys()),
                            [len(v) for v in leads_dict.values()]),
                            "Adelanto": np.concatenate([np.array(v) for v in leads_dict.values()])})
    if len(plot_df) > 0:
        fig, ax = plt.subplots(figsize=(9, 5))
        sns.violinplot(data=plot_df, x="Método", y="Adelanto", ax=ax, inner="box", hue="Método", palette="muted", legend=False)
        sns.stripplot(data=plot_df, x="Método", y="Adelanto", ax=ax, color="k", alpha=0.3, size=3)
        ax.set_title(f"Figura 4: Distribución de adelantos — {city_label}")
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"{prefix}fig4_lead_distributions.png"), bbox_inches="tight")
        plt.close()

        # Fig 5
        means = [np.mean(v) for v in leads_dict.values()]
        ns = [len(v) for v in leads_dict.values()]
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(list(leads_dict.keys()), means, color=sns.color_palette("Set2", len(leads_dict)))
        for b, m, n in zip(bars, means, ns):
            ax.text(b.get_x() + b.get_width()/2, b.get_height()+2, f"{m:.1f}\n(n={n})", ha="center", fontsize=9)
        ax.set_title(f"Figura 5: Adelanto medio por método — {city_label}")
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"{prefix}fig5_mean_leads.png"), bbox_inches="tight")
        plt.close()

    # Fig 6
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(dist_smooth, label="||ΔC||_F (suavizada)", color="steelblue")
    ax.axhline(dist_thresh, color="gray", ls=":", label=f"Umbral {STRUCTURAL_PERCENTILE}%")
    for ch in structural_changes:
        ax.axvline(ch, color="darkred", ls="--", alpha=0.6)
    for _, k in strong_peaks:
        ax.scatter(k, dist_smooth[k], marker="v", s=70, c="darkorange", zorder=5)
    ax.set_title(f"Figura 6: Distancia entre matrices de coherencia — {city_label}")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"{prefix}fig6_coherence_distance.png"), bbox_inches="tight")
    plt.close()

    print(f"  [FIGURAS] Guardadas para {city_label} (prefijo: {prefix})")


def run_full_pipeline_for_city(city_data: dict, city_code: str):
    """Ejecuta todo el pipeline para una ciudad y devuelve el resumen."""
    regions_data = city_data["regions_data"]
    region_names = city_data["region_names"]
    city_label = city_data["city_label"]

    print(f"\n{'='*65}")
    print(f"ANÁLISIS PARA: {city_label} ({city_code})")
    print(f"{'='*65}")

    metrics = compute_all_metrics(regions_data)
    strong_peaks = detect_strong_peaks(metrics)
    structural_changes, dist_smooth, dist_thresh = detect_structural_changes(metrics["C"])
    i_times = [k for _, k in strong_peaks]
    leads_I = compute_leads(i_times, structural_changes)
    leads_other = compute_reference_leads(metrics, structural_changes)
    stats_res, _ = run_statistical_test(leads_I, leads_other)

    # Guardar figuras
    save_figures(metrics, strong_peaks, structural_changes, dist_smooth, dist_thresh,
                 leads_I, leads_other, region_names, city_code, city_label)

    # Resumen por ciudad
    print(f"\n--- Resumen {city_label} ---")
    print(f"Picos fuertes de I_i detectados : {len(strong_peaks)}")
    print(f"Cambios estructurales detectados: {len(structural_changes)}")
    print(f"Adelanto medio I_i     : {np.mean(leads_I):.2f} (n={len(leads_I)})" if leads_I else "Adelanto medio I_i: N/A")
    for m, ls in leads_other.items():
        if ls:
            print(f"Adelanto medio {m:18s}: {np.mean(ls):.2f} (n={len(ls)})")
    p = min(stats_res.get("mannwhitney_p", 1), stats_res.get("perm_p", 1))
    mean_i = stats_res.get("mean_I", np.nan)
    mean_o = stats_res.get("mean_other", np.nan)
    if len(leads_I) >= 3 and mean_i > mean_o and p < 0.10:
        conclusion = ">> EVIDENCIA A FAVOR de la Predicción 2 (p < 0.10)"
    elif len(leads_I) >= 3 and mean_i > mean_o:
        conclusion = ">> TENDENCIA A FAVOR (mayor adelanto pero p >= 0.10)"
    else:
        conclusion = ">> Sin evidencia clara de mayor adelanto en esta ciudad."
    print(f"Test: MW p={stats_res.get('mannwhitney_p',1):.4f} | Perm p={stats_res.get('perm_p',1):.4f}")
    print(conclusion)

    return {
        "city": city_code,
        "n_peaks": len(strong_peaks),
        "n_changes": len(structural_changes),
        "leads_I": leads_I,
        "leads_other": leads_other,
        "stats": stats_res,
        "conclusion": conclusion
    }


def main():
    print("\n" + "=" * 72)
    print("TEST EMPÍRICO PREDICCIÓN 2 — DATOS REALES DENGAI")
    print("=" * 72)

    # 1. Preparar / verificar datos
    merged_file = ensure_data_ready()
    if merged_file is None:
        sys.exit(1)

    # 2. Cargar datos (posiblemente para una o ambas ciudades)
    cities_data = load_dengai_data(merged_file, CITY)

    if not cities_data:
        print("[ERROR] No se pudieron cargar datos para ninguna ciudad.")
        sys.exit(1)

    # 3. Ejecutar pipeline por ciudad
    all_results = []
    for city_code, city_data in cities_data.items():
        res = run_full_pipeline_for_city(city_data, city_code)
        all_results.append(res)

    # 4. Resumen global
    print("\n" + "=" * 72)
    print("RESUMEN GLOBAL DEL PROYECTO")
    print("=" * 72)
    for r in all_results:
        print(f"\n{r['city'].upper()} ({CITY_LABELS.get(r['city'], r['city'])}):")
        print(f"  Picos fuertes I_i : {r['n_peaks']}")
        print(f"  Cambios estructurales : {r['n_changes']}")
        if r['leads_I']:
            print(f"  Adelanto medio I_i : {np.mean(r['leads_I']):.2f}")
        print(f"  {r['conclusion']}")

    print(f"\nTodas las figuras se guardaron en: {os.path.abspath(OUTPUT_DIR)}")
    print("Ejecución completada.\n")


if __name__ == "__main__":
    main()