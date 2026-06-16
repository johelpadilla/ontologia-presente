#!/usr/bin/env python3
"""
sweep_prediccion2_san_juan.py

Barrido sistemático de hiperparámetros para el test empírico de la
Predicción 2 (RECD + estructura espacial) usando SOLO datos de San Juan.

Ejecución:
    python sweep_prediccion2_san_juan.py

El script:
- Carga (o prepara) data/datos_dengai_completo.csv
- Filtra exclusivamente la ciudad "sj"
- Ejecuta el pipeline completo de la Predicción 2 para cada combinación
  de la grilla de parámetros.
- Registra métricas clave y guarda resultados en resultados_sweep/
- Imprime un ranking de las mejores configuraciones al final.
"""

import os
import math
from collections import Counter
from itertools import product
from datetime import datetime

import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import find_peaks
from scipy.ndimage import uniform_filter1d

# =============================================================================
# CONFIGURACIÓN DEL EXPERIMENTO (EDITAR AQUÍ)
# =============================================================================

# Ruta al archivo de datos (se crea automáticamente si no existe)
DATA_PATH = os.path.join("data", "datos_dengai_completo.csv")

# Carpeta de salida
OUTPUT_DIR = "resultados_sweep"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Grilla de parámetros a barrer (todas las combinaciones cartesianas)
PARAM_GRID = {
    "TAU_WINDOW": [55, 65, 75, 85],
    "COH_WINDOW": [80, 90, 100],
    "PEAK_Q": [0.55, 0.60, 0.65, 0.70],
}

# Parámetros fijos (puedes moverlos a la grilla si quieres explorarlos)
FIXED_PARAMS = {
    "PESO_GAMMA_WINDOW": 50,
    "STRUCTURAL_PERCENTILE": 94,
    "STRUCTURAL_MIN_DIST": 35,
    "PEAK_MIN_DIST": 18,           # separación mínima entre picos fuertes
    "EMBEDDING_DIM": 3,            # para entropía de permutación
}

# Columnas usadas para definir las 3 regiones temáticas (San Juan)
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

# Semilla para reproducibilidad en tests de permutación
SEED = 42
np.random.seed(SEED)

print("=" * 75)
print("SWEEP PREDICCIÓN 2 - SOLO SAN JUAN (SJ)")
print(f"Grilla: {len(PARAM_GRID['TAU_WINDOW'])} × {len(PARAM_GRID['COH_WINDOW'])} × "
      f"{len(PARAM_GRID['PEAK_Q'])} = "
      f"{len(PARAM_GRID['TAU_WINDOW']) * len(PARAM_GRID['COH_WINDOW']) * len(PARAM_GRID['PEAK_Q'])} combinaciones")
print(f"Salida: {OUTPUT_DIR}/")
print("=" * 75)


# =============================================================================
# CARGA DE DATOS - EXCLUSIVAMENTE SAN JUAN
# =============================================================================

def ensure_data_file():
    """Asegura que exista el archivo merged. Si no, da instrucciones."""
    if os.path.exists(DATA_PATH):
        return DATA_PATH

    features_p = os.path.join("data", "dengue_features_train.csv")
    labels_p = os.path.join("data", "dengue_labels_train.csv")

    if os.path.exists(features_p) and os.path.exists(labels_p):
        print("[DATA] Archivos originales encontrados. Uniendo...")
        feat = pd.read_csv(features_p)
        lab = pd.read_csv(labels_p)
        merged = pd.merge(feat, lab, on=["city", "year", "weekofyear"], how="left")
        merged = merged.sort_values(["city", "year", "weekofyear"]).reset_index(drop=True)
        merged.to_csv(DATA_PATH, index=False)
        print(f"[DATA] Creado {DATA_PATH} con {len(merged)} filas")
        return DATA_PATH

    print(f"\n[ERROR] No se encontró {DATA_PATH} ni los archivos originales.")
    print("Ejecuta primero: python prepare_dengai_data.py")
    print("O descarga manualmente desde DrivenData y colócalos en data/.")
    raise FileNotFoundError("Datos de DengAI no disponibles.")


def load_san_juan_regions(data_path):
    """
    Carga el CSV, filtra SOLO San Juan ("sj"), limpia NaNs,
    define las 3 regiones temáticas y devuelve las matrices estandarizadas.
    """
    print(f"[LOAD] Cargando datos de San Juan desde: {data_path}")
    df = pd.read_csv(data_path)

    # Filtrar ciudad y ordenar cronológicamente
    df = df[df["city"] == "sj"].copy()
    df = df.sort_values(["year", "weekofyear"]).reset_index(drop=True)

    if len(df) < 100:
        raise ValueError("Muy pocos datos para San Juan después del filtro.")

    # Columnas necesarias
    all_needed = set()
    for _, cols in BASE_REGION_DEFINITION:
        all_needed.update(cols)

    if "total_cases" not in df.columns:
        raise ValueError("Falta la columna 'total_cases'. ¿Se unieron features + labels?")

    cols_to_keep = [c for c in (["year", "weekofyear"] + list(all_needed)) if c in df.columns]
    df_clean = df[cols_to_keep].copy()

    # Limpieza de NaNs (interpolación)
    df_clean = df_clean.interpolate(method="linear", limit_direction="both").ffill().bfill()
    df_clean = df_clean.dropna().reset_index(drop=True)

    print(f"[LOAD] San Juan después de limpieza: {len(df_clean)} semanas")

    # Construir regiones (estandarizadas)
    regions_data = []
    region_names = []

    for name, cols in BASE_REGION_DEFINITION:
        avail = [c for c in cols if c in df_clean.columns]
        if len(avail) < 2:
            print(f"[WARN] Región '{name}' tiene <2 variables. Se omite.")
            continue
        sub = df_clean[avail].copy()
        sub_std = (sub - sub.mean()) / (sub.std(ddof=0) + 1e-8)
        regions_data.append(sub_std.values.astype(float))
        region_names.append(name)

    if len(regions_data) < 2:
        raise ValueError("No se pudieron construir al menos 2 regiones para San Juan.")

    # Alinear longitudes
    min_len = min(len(r) for r in regions_data)
    regions_data = [r[:min_len] for r in regions_data]

    print(f"[LOAD] Regiones construidas para San Juan: {region_names} (T={min_len})")
    return regions_data, region_names


# =============================================================================
# FUNCIONES DEL PIPELINE RECD (PARAMETRIZADAS)
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


def compute_local_tau_s(series, k, window, dim=3):
    """tau_s local con ventana configurable."""
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


def compute_all_metrics(regions_data, tau_window, coh_window):
    """Calcula todas las métricas RECD con ventanas configurables."""
    n_reg = len(regions_data)
    T = len(regions_data[0])
    s_reps = [compute_representative(rd) for rd in regions_data]

    # tau_s y reloj local
    tau_s = np.zeros((n_reg, T))
    for i in range(n_reg):
        for k in range(T):
            tau_s[i, k] = compute_local_tau_s(s_reps[i], k, tau_window)

    # Coherencias C_ij(k)
    C = np.ones((n_reg, n_reg, T))
    for k in range(coh_window, T):
        for i in range(n_reg):
            for j in range(i + 1, n_reg):
                si = s_reps[i][k - coh_window + 1 : k + 1]
                sj = s_reps[j][k - coh_window + 1 : k + 1]
                corr = np.corrcoef(si, sj)[0, 1]
                C[i, j, k] = C[j, i, k] = corr

    # rho_i (densidad espacial)
    rho = np.zeros((n_reg, T))
    for k in range(T):
        for i in range(n_reg):
            others = [abs(C[i, j, k]) for j in range(n_reg) if j != i]
            rho[i, k] = np.mean(others) if others else 0.0

    # Peso y Gamma (hiper-persistencia)
    peso = np.zeros((n_reg, T))
    gamma = np.zeros((n_reg, T))
    pg_win = FIXED_PARAMS["PESO_GAMMA_WINDOW"]
    for i in range(n_reg):
        for k in range(T):
            peso[i, k] = tau_s[i, k]
            start = max(0, k - 40 + 1)
            win_tau = tau_s[i, start : k + 1]
            gamma[i, k] = max(0.0, tau_s[i, k] - np.median(win_tau)) + 1e-4

    I = peso * rho * gamma
    return {"tau_s": tau_s, "C": C, "rho": rho, "peso": peso, "gamma": gamma, "I": I, "s_reps": s_reps}


def detect_strong_peaks(metrics, peak_q, min_dist):
    """Picos fuertes donde los 3 componentes + I están altos."""
    I, peso, rho, gamma = metrics["I"], metrics["peso"], metrics["rho"], metrics["gamma"]
    n_reg, T = I.shape
    raw_peaks = []

    for i in range(n_reg):
        p_th = np.percentile(peso[i], peak_q * 100)
        r_th = np.percentile(rho[i], peak_q * 100)
        g_th = np.percentile(gamma[i], peak_q * 100)
        i_th = np.percentile(I[i], 75)
        for k in range(20, T - 10):
            if (peso[i, k] > p_th and rho[i, k] > r_th and
                    gamma[i, k] > g_th and I[i, k] > i_th):
                raw_peaks.append((i, k))

    # Thinning por región
    by_reg = {}
    for reg, k in raw_peaks:
        by_reg.setdefault(reg, []).append(k)

    thinned = []
    for reg in sorted(by_reg):
        times = np.array(sorted(set(by_reg[reg])))
        if len(times) == 0:
            continue
        sel = [times[0]]
        for tt in times[1:]:
            if tt - sel[-1] >= min_dist:
                sel.append(tt)
        thinned.extend([(reg, int(t)) for t in sel])
    return thinned


def detect_structural_changes(C, percentile, min_dist):
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
    """Detectores de referencia (PE, var tau, delta tau)."""
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

    # Cambios en tau_s
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


def run_statistical_test(leads_I, leads_other_dict):
    leads_I = np.asarray(leads_I)
    all_other = np.concatenate([np.asarray(v) for v in leads_other_dict.values()]) \
        if any(len(v) > 0 for v in leads_other_dict.values()) else np.array([])

    if len(leads_I) < 3 or len(all_other) < 3:
        return {
            "n_I": len(leads_I),
            "n_other": len(all_other),
            "mean_I": float(np.mean(leads_I)) if len(leads_I) else np.nan,
            "mean_other": float(np.mean(all_other)) if len(all_other) else np.nan,
            "mw_p": 1.0,
            "perm_p": 1.0,
        }

    u_stat, mw_p = stats.mannwhitneyu(leads_I, all_other, alternative="greater")

    # Permutation test (simple)
    observed = np.mean(leads_I) - np.mean(all_other)
    combined = np.concatenate([leads_I, all_other])
    n_x = len(leads_I)
    rng = np.random.default_rng(SEED)
    count = 0
    for _ in range(3000):  # 3000 permutaciones para velocidad
        perm = rng.permutation(combined)
        mx = np.mean(perm[:n_x])
        my = np.mean(perm[n_x:])
        if (mx - my) >= observed:
            count += 1
    perm_p = (count + 1) / 3001

    return {
        "n_I": len(leads_I),
        "n_other": len(all_other),
        "mean_I": float(np.mean(leads_I)),
        "mean_other": float(np.mean(all_other)),
        "mw_p": float(mw_p),
        "perm_p": float(perm_p),
    }


def get_conclusion(mean_I, mean_other, mw_p, perm_p, n_I):
    min_p = min(mw_p, perm_p)
    if n_I >= 5 and mean_I > mean_other and min_p < 0.10:
        return "Evidencia a favor (p<0.10)"
    elif n_I >= 5 and mean_I > mean_other:
        return "Tendencia a favor"
    else:
        return "Sin evidencia clara"


# =============================================================================
# FUNCIÓN PRINCIPAL DEL EXPERIMENTO
# =============================================================================

def run_experiment(tau_window, coh_window, peak_q, regions_data, region_names):
    """
    Ejecuta el pipeline completo con una combinación específica de parámetros.
    Retorna un diccionario resumen + lista de leads individuales.
    """
    run_id = f"tau{tau_window}_coh{coh_window}_q{int(peak_q*100)}"

    # Métricas
    metrics = compute_all_metrics(regions_data, tau_window, coh_window)
    strong_peaks = detect_strong_peaks(
        metrics, peak_q, FIXED_PARAMS["PEAK_MIN_DIST"]
    )
    struct_changes, _, _ = detect_structural_changes(
        metrics["C"],
        FIXED_PARAMS["STRUCTURAL_PERCENTILE"],
        FIXED_PARAMS["STRUCTURAL_MIN_DIST"]
    )

    i_times = [k for _, k in strong_peaks]
    leads_I = compute_leads(i_times, struct_changes)
    leads_other = compute_reference_leads(metrics, struct_changes)
    stats_res = run_statistical_test(leads_I, leads_other)

    # Conclusión
    conclusion = get_conclusion(
        stats_res["mean_I"], stats_res["mean_other"],
        stats_res["mw_p"], stats_res["perm_p"], stats_res["n_I"]
    )

    # Resumen por combinación
    summary = {
        "run_id": run_id,
        "TAU_WINDOW": tau_window,
        "COH_WINDOW": coh_window,
        "PEAK_Q": peak_q,
        "n_picos_I": len(strong_peaks),
        "n_cambios_estructurales": len(struct_changes),
        "adelanto_I_mean": stats_res["mean_I"],
        "adelanto_I_n": stats_res["n_I"],
        "adelanto_PE_mean": float(np.mean(leads_other["PE multivariada"])) if leads_other["PE multivariada"] else np.nan,
        "adelanto_PE_n": len(leads_other["PE multivariada"]),
        "adelanto_var_tau_mean": float(np.mean(leads_other["Varianza τ_s"])) if leads_other["Varianza τ_s"] else np.nan,
        "adelanto_var_tau_n": len(leads_other["Varianza τ_s"]),
        "adelanto_dtau_mean": float(np.mean(leads_other["Δ τ_s individual"])) if leads_other["Δ τ_s individual"] else np.nan,
        "adelanto_dtau_n": len(leads_other["Δ τ_s individual"]),
        "mw_p": stats_res["mw_p"],
        "perm_p": stats_res["perm_p"],
        "min_p": min(stats_res["mw_p"], stats_res["perm_p"]),
        "conclusion": conclusion,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

    # Leads individuales (formato largo)
    lead_rows = []
    for lead in leads_I:
        lead_rows.append({
            "run_id": run_id, "TAU_WINDOW": tau_window, "COH_WINDOW": coh_window, "PEAK_Q": peak_q,
            "method": "I_i_strong", "lead": lead
        })
    for method, ls in leads_other.items():
        for lead in ls:
            lead_rows.append({
                "run_id": run_id, "TAU_WINDOW": tau_window, "COH_WINDOW": coh_window, "PEAK_Q": peak_q,
                "method": method, "lead": lead
            })

    return summary, lead_rows


# =============================================================================
# MAIN - BARRIDO Y EXPORTACIÓN
# =============================================================================

def main():
    # 1. Preparar datos
    ensure_data_file()
    regions_data, region_names = load_san_juan_regions(DATA_PATH)

    # 2. Preparar grilla
    param_names = list(PARAM_GRID.keys())
    param_values = list(PARAM_GRID.values())
    all_combos = list(product(*param_values))
    print(f"\n[SWEEP] Ejecutando {len(all_combos)} combinaciones...\n")

    summary_results = []
    all_leads = []

    for i, combo in enumerate(all_combos, 1):
        params = dict(zip(param_names, combo))
        tau = params["TAU_WINDOW"]
        coh = params["COH_WINDOW"]
        q = params["PEAK_Q"]

        print(f"[{i:3d}/{len(all_combos)}] tau={tau:3d}  coh={coh:3d}  q={q:.2f} ...", end=" ", flush=True)

        try:
            summary, lead_rows = run_experiment(tau, coh, q, regions_data, region_names)
            summary_results.append(summary)
            all_leads.extend(lead_rows)
            print(f"picos={summary['n_picos_I']:2d}  cambios={summary['n_cambios_estructurales']:2d}  "
                  f"adel_I={summary['adelanto_I_mean']:.1f}  min_p={summary['min_p']:.4f}")
        except Exception as e:
            print(f"ERROR: {e}")
            continue

    # 3. Guardar resultados
    print("\n[EXPORT] Guardando resultados...")

    df_summary = pd.DataFrame(summary_results)
    summary_path = os.path.join(OUTPUT_DIR, "resultados_sweep_san_juan.csv")
    df_summary.to_csv(summary_path, index=False)
    print(f"  - Resumen: {summary_path}")

    if all_leads:
        df_leads = pd.DataFrame(all_leads)
        leads_path = os.path.join(OUTPUT_DIR, "leads_individuales_san_juan.csv")
        df_leads.to_csv(leads_path, index=False)
        print(f"  - Leads individuales: {leads_path} ({len(df_leads)} filas)")

    # 4. Resumen final ordenado
    print("\n" + "=" * 75)
    print("RESUMEN FINAL - MEJORES CONFIGURACIONES (San Juan)")
    print("=" * 75)

    if len(df_summary) == 0:
        print("No se obtuvieron resultados válidos.")
        return

    # Ordenar por: mayor adelanto_I + menor min_p
    df_sorted = df_summary.sort_values(
        by=["adelanto_I_mean", "min_p", "n_picos_I"],
        ascending=[False, True, False]
    ).reset_index(drop=True)

    # Mostrar top 10
    cols_to_show = [
        "TAU_WINDOW", "COH_WINDOW", "PEAK_Q",
        "n_picos_I", "n_cambios_estructurales",
        "adelanto_I_mean", "adelanto_I_n",
        "mw_p", "perm_p", "min_p", "conclusion"
    ]
    print(df_sorted[cols_to_show].head(10).to_string(index=False))

    # Destacar las 3 mejores
    print("\n" + "-" * 75)
    print("TOP 3 MEJORES COMBINACIONES:")
    for rank, row in df_sorted.head(3).iterrows():
        print(f"\n{rank+1}. TAU={row['TAU_WINDOW']}  COH={row['COH_WINDOW']}  Q={row['PEAK_Q']:.2f}")
        print(f"   Adelanto I_i medio: {row['adelanto_I_mean']:.2f} (n={int(row['adelanto_I_n'])})")
        print(f"   p-values: MW={row['mw_p']:.4f} | Perm={row['perm_p']:.4f}")
        print(f"   {row['conclusion']}")

    print("\n" + "=" * 75)
    print(f"Archivos guardados en: {os.path.abspath(OUTPUT_DIR)}")
    print("Ejecución del sweep completada.")


if __name__ == "__main__":
    main()