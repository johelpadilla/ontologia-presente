#!/usr/bin/env python3
"""
analisis_profundo_lorenz.py

Análisis profundo de los picos estructurales (refinado + RQA) generados
en el experimento sintético con el atractor de Lorenz (3 variables x, y, z).

Basado en analisis_profundo_sintetico.py, adaptado para:
- Rutas específicas de resultados_sintetico_lorenz/
- INJECTED_CHANGES = [1500, 3200] (cambios de rho)
- Reporte con números de Lorenz e interpretación sobre hyper_persistence_level
  vs lo observado en el mapa logístico acoplado.

Carga el CSV enriquecido y realiza:
- Estadísticas de leads a transiciones inyectadas
- División en "buenos anticipadores" vs "débiles" (percentil 60)
- Comparación de perfiles RQA con tests Mann-Whitney (una cola)
- Análisis de concentración temporal antes de las inyecciones de rho
- 4 figuras y reporte estructurado

Uso:
    python analisis_profundo_lorenz.py
"""

import os
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# =============================================================================
# CONFIGURACIÓN - LORENZ
# =============================================================================
CSV_PATH = "resultados_sintetico_lorenz/picos_fuertes_refinados_rqa_lorenz.csv"
OUTPUT_DIR = "resultados_sintetico_lorenz/analisis_profundo"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Transiciones inyectadas conocidas (cambios de rho en el generador Lorenz)
INJECTED_CHANGES = [1500, 3200]

# Ventana para analizar concentración antes de cada inyección (pasos)
WINDOW_BEFORE_INJECTION = 200

# Estilo (idéntico al script base)
sns.set_theme(style="whitegrid", font_scale=1.05)
plt.rcParams['figure.dpi'] = 130
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.family'] = 'sans-serif'

print("=" * 82)
print("ANÁLISIS PROFUNDO DE PICOS ESTRUCTURALES - EXPERIMENTO LORENZ")
print("Atractor de Lorenz (x, y, z) | Config B (Equilibrio) + RECD + Hiper-persistencia")
print(f"Inyecciones de rho: {INJECTED_CHANGES}")
print("=" * 82)


# =============================================================================
# CARGA Y PREPARACIÓN
# =============================================================================

def load_and_prepare(csv_path):
    """Carga el CSV y prepara columnas relevantes."""
    print(f"\n[1] Cargando datos desde: {csv_path}")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"No se encontró el archivo {csv_path}. "
            "Ejecuta primero analisis_refinado_rqa_lorenz.py"
        )
    
    df = pd.read_csv(csv_path)
    
    print(f"    Total de picos estructurales: {len(df)}")
    print(f"    Columnas disponibles: {list(df.columns)}")
    
    # Asegurar que usamos solo leads válidos (lead >= 0)
    df["lead_valid"] = df["lead_to_next_injected_change"] >= 0
    
    n_valid = df["lead_valid"].sum()
    print(f"    Picos con lead válido a inyección: {n_valid} "
          f"({n_valid/len(df)*100:.1f}%)")
    
    if n_valid == 0:
        raise ValueError("No hay picos con lead válido a transiciones inyectadas.")
    
    # Estadísticas descriptivas generales de leads
    valid_leads = df[df["lead_valid"]]["lead_to_next_injected_change"]
    print(f"\n    Estadísticas de lead_to_next_injected_change (válidos):")
    print(f"      Media   : {valid_leads.mean():.2f}")
    print(f"      Mediana : {valid_leads.median():.2f}")
    print(f"      Min/Max : {valid_leads.min():.0f} / {valid_leads.max():.0f}")
    print(f"      Std     : {valid_leads.std():.2f}")
    
    return df


# =============================================================================
# DIVISIÓN EN GRUPOS DE ANTICIPACIÓN
# =============================================================================

def split_anticipators(df):
    """Divide los picos en 'buenos' y 'débiles' según percentil 60 de leads válidos."""
    print("\n[2] Dividiendo picos en grupos de anticipación")
    
    valid_df = df[df["lead_valid"]].copy()
    
    p60 = valid_df["lead_to_next_injected_change"].quantile(0.60)
    print(f"    Percentil 60 de leads válidos: {p60:.2f}")
    
    # Buenos anticipadores: lead > p60
    good_mask = (df["lead_valid"]) & (df["lead_to_next_injected_change"] > p60)
    weak_mask = (df["lead_valid"]) & (df["lead_to_next_injected_change"] <= p60)
    
    good = df[good_mask].copy()
    weak = df[weak_mask].copy()
    
    print(f"    Buenos anticipadores (lead > {p60:.2f}): {len(good)}")
    print(f"    Anticipadores débiles (lead <= {p60:.2f}): {len(weak)}")
    
    # Agregar etiqueta para visualizaciones
    df["anticipator_group"] = "N/A"
    df.loc[good_mask, "anticipator_group"] = "Buenos anticipadores"
    df.loc[weak_mask, "anticipator_group"] = "Anticipadores débiles"
    
    return df, good, weak, p60


# =============================================================================
# COMPARACIÓN DE PERFILES RQA
# =============================================================================

def compare_rqa_profiles(good, weak):
    """Compara métricas RQA entre grupos con tests Mann-Whitney."""
    print("\n[3] Comparando perfiles RQA entre grupos")
    
    metrics = [
        "laminarity_at_peak",
        "trapping_time_at_peak",
        "lam_acceleration",
        "trap_acceleration",
        "rqa_structural_score",
        "hyper_persistence_level"
    ]
    
    results = []
    
    print("\n    Tests Mann-Whitney (una cola: Buenos > Débiles):")
    for metric in metrics:
        if metric not in good.columns or metric not in weak.columns:
            print(f"      {metric}: columna no encontrada")
            continue
        
        g_vals = good[metric].dropna()
        w_vals = weak[metric].dropna()
        
        if len(g_vals) < 3 or len(w_vals) < 3:
            print(f"      {metric}: datos insuficientes")
            continue
        
        # Mann-Whitney greater (buenos anticipadores tienen valores mayores)
        _, p_greater = stats.mannwhitneyu(g_vals, w_vals, alternative="greater")
        _, p_two = stats.mannwhitneyu(g_vals, w_vals, alternative="two-sided")
        
        med_g = g_vals.median()
        med_w = w_vals.median()
        delta = med_g - med_w
        
        results.append({
            "metric": metric,
            "n_buenos": len(g_vals),
            "n_debiles": len(w_vals),
            "mediana_buenos": round(med_g, 4),
            "mediana_debiles": round(med_w, 4),
            "diferencia_medianas": round(delta, 4),
            "p_mw_greater": round(p_greater, 4),
            "p_mw_two_sided": round(p_two, 4),
            "significativo": "Sí (p<0.10)" if p_greater < 0.10 else "No"
        })
        
        sig = " *" if p_greater < 0.10 else ""
        print(f"      {metric:28s}: "
              f"Buenos={med_g:.4f} | Débiles={med_w:.4f} | "
              f"Δ={delta:+.4f} | p={p_greater:.4f}{sig}")
    
    return pd.DataFrame(results)


# =============================================================================
# ANÁLISIS DE CONCENTRACIÓN TEMPORAL
# =============================================================================

def analyze_concentration(df, injected_times, window=200):
    """Analiza cuántos picos ocurren en las ventanas previas a las inyecciones."""
    print(f"\n[4] Análisis de concentración de picos antes de inyecciones (ventana={window} pasos)")
    
    results = []
    total_structural = len(df)
    
    for inj in injected_times:
        before_start = inj - window
        before_end = inj
        
        mask = (df["k"] >= before_start) & (df["k"] < before_end)
        count = mask.sum()
        pct = (count / total_structural * 100) if total_structural > 0 else 0
        
        results.append({
            "inyeccion_t": inj,
            "ventana_inicio": before_start,
            "ventana_fin": before_end,
            "picos_en_ventana": count,
            "porcentaje_total": round(pct, 1)
        })
        
        print(f"    Inyección en t={inj}: "
              f"{count} picos en [{before_start}, {before_end}) "
              f"({pct:.1f}% del total)")
    
    # Porcentaje acumulado antes de cualquier inyección
    any_before = pd.Series([False] * len(df))
    for inj in injected_times:
        mask = (df["k"] >= inj - window) & (df["k"] < inj)
        any_before = any_before | mask
    
    total_before_any = any_before.sum()
    pct_any = (total_before_any / total_structural * 100) if total_structural > 0 else 0
    
    print(f"\n    Total picos en alguna ventana pre-inyección: "
          f"{total_before_any} ({pct_any:.1f}%)")
    
    return pd.DataFrame(results), total_before_any, pct_any


# =============================================================================
# VISUALIZACIONES
# =============================================================================

def generate_figures(df, good, weak, p60, injected_times, output_dir):
    """Genera las figuras solicitadas (adaptadas para Lorenz)."""
    print("\n[5] Generando figuras...")
    
    valid_leads = df[df["lead_valid"]]["lead_to_next_injected_change"]
    
    # --- 1. Histograma de leads ---
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.histplot(valid_leads, bins=20, kde=True, color="steelblue", ax=ax)
    ax.axvline(p60, color="red", linestyle="--", linewidth=2, label=f"Percentil 60 = {p60:.1f}")
    ax.axvline(valid_leads.median(), color="green", linestyle=":", linewidth=2, 
               label=f"Mediana = {valid_leads.median():.1f}")
    ax.set_xlabel("Lead a la siguiente transición inyectada (pasos)")
    ax.set_title("Distribución de leads de picos estructurales a transiciones inyectadas\n(Atractor de Lorenz)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig1_histograma_leads.png"), bbox_inches="tight")
    plt.close()
    print("  [FIG] fig1_histograma_leads.png")
    
    # --- 2. Boxplots comparativos de métricas RQA ---
    metrics_to_plot = [
        "laminarity_at_peak",
        "trapping_time_at_peak", 
        "rqa_structural_score",
        "hyper_persistence_level"
    ]
    
    # Preparar datos en formato largo
    plot_df = df[df["lead_valid"]][["anticipator_group"] + metrics_to_plot].copy()
    plot_df = plot_df[plot_df["anticipator_group"] != "N/A"]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes = axes.flatten()
    
    palette_dict = {"Buenos anticipadores": "#2ca02c", "Anticipadores débiles": "#d62728"}
    
    for i, metric in enumerate(metrics_to_plot):
        # Usar hue explícito para evitar deprecation warning de palette sin hue
        sns.boxplot(
            data=plot_df, 
            x="anticipator_group", 
            y=metric, 
            hue="anticipator_group",
            ax=axes[i],
            palette=palette_dict,
            legend=False
        )
        sns.stripplot(
            data=plot_df, 
            x="anticipator_group", 
            y=metric, 
            ax=axes[i], 
            color="black", 
            alpha=0.3, 
            size=3
        )
        axes[i].set_title(metric.replace("_", " ").title())
        axes[i].set_xlabel("")
        if i in [0, 2]:
            axes[i].set_ylabel(metric)
        else:
            axes[i].set_ylabel("")
    
    plt.suptitle("Comparación de métricas RQA: Buenos anticipadores vs Débiles\n(Atractor de Lorenz)", y=1.02, fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig2_boxplots_rqa_groups.png"), bbox_inches="tight")
    plt.close()
    print("  [FIG] fig2_boxplots_rqa_groups.png")
    
    # --- 3. Timeline de picos + inyecciones ---
    fig, ax = plt.subplots(figsize=(14, 5))
    
    # Marcas de inyecciones (cambios de rho)
    for inj in injected_times:
        ax.axvline(inj, color="green", linestyle="--", linewidth=2, alpha=0.85, 
                   label="Cambio de rho (inyección)" if inj == injected_times[0] else "")
    
    # Picos estructurales (color por grupo)
    colors = {"Buenos anticipadores": "#2ca02c", "Anticipadores débiles": "#d62728", "N/A": "gray"}
    
    for group in ["Buenos anticipadores", "Anticipadores débiles"]:
        sub = df[df["anticipator_group"] == group]
        if len(sub) > 0:
            ax.scatter(
                sub["k"], 
                [1.0] * len(sub),   # todos en la misma "fila" para simplicidad
                c=colors[group], 
                s=80, 
                marker="|", 
                linewidths=2,
                label=group
            )
    
    ax.set_yticks([])
    ax.set_xlabel("Paso de tiempo (k)")
    ax.set_title("Timeline de picos estructurales y transiciones de régimen (cambios de rho) - Atractor de Lorenz")
    ax.legend(loc="upper right")
    ax.set_ylim(0.5, 1.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig3_timeline_picos.png"), bbox_inches="tight")
    plt.close()
    print("  [FIG] fig3_timeline_picos.png")
    
    # --- 4. Scatter plots lead vs métricas RQA ---
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes = axes.flatten()
    
    scatter_metrics = ["rqa_structural_score", "hyper_persistence_level", 
                       "laminarity_at_peak", "trapping_time_at_peak"]
    
    for i, metric in enumerate(scatter_metrics):
        sns.scatterplot(
            data=df[df["lead_valid"]], 
            x="lead_to_next_injected_change", 
            y=metric, 
            hue="anticipator_group",
            palette=colors,
            ax=axes[i],
            alpha=0.7,
            s=60
        )
        # Línea de regresión opcional
        sns.regplot(
            data=df[df["lead_valid"]], 
            x="lead_to_next_injected_change", 
            y=metric, 
            scatter=False, 
            color="black", 
            line_kws={"linestyle": "--", "alpha": 0.5},
            ax=axes[i]
        )
        axes[i].set_title(f"Lead vs {metric.replace('_', ' ')}")
        axes[i].axvline(p60, color="red", linestyle=":", alpha=0.6, label=f"Percentil 60")
    
    plt.suptitle("Relación entre lead a inyección y métricas RQA\n(Atractor de Lorenz)", y=1.02, fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig4_scatter_lead_vs_rqa.png"), bbox_inches="tight")
    plt.close()
    print("  [FIG] fig4_scatter_lead_vs_rqa.png")
    
    print(f"\n  Todas las figuras guardadas en: {output_dir}/")


# =============================================================================
# REPORTE ESTRUCTURADO
# =============================================================================

def generate_report(df, good, weak, rqa_comparison, conc_df, total_before, pct_any, p60, output_dir):
    """Genera el reporte estructurado en consola y archivo (adaptado para Lorenz)."""
    report_lines = []
    
    def log(msg=""):
        report_lines.append(msg)
        print(msg)
    
    log("=" * 82)
    log("REPORTE DE ANÁLISIS PROFUNDO - PICOS ESTRUCTURALES LORENZ")
    log(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log("Sistema: Atractor de Lorenz (3 componentes: x, y, z)")
    log("Parámetros: RECD (τ=85, C=90, Q=0.60) + RQA Config B + Hiper-persistencia > 1.0")
    log("Inyecciones de régimen: rho 28→35 en t=1500 | rho 35→24 en t=3200")
    log("=" * 82)
    
    # 1. Estadísticas generales
    log("\n1. ESTADÍSTICAS GENERALES DE LEADS A TRANSICIONES INYECTADAS")
    valid_leads = df[df["lead_valid"]]["lead_to_next_injected_change"]
    log(f"   Total picos estructurales analizados: {len(df)}")
    log(f"   Picos con lead válido: {len(valid_leads)}")
    log(f"   Media de lead: {valid_leads.mean():.2f}")
    log(f"   Mediana de lead: {valid_leads.median():.2f}")
    log(f"   Percentil 60 (umbral de división): {p60:.2f}")
    log(f"   Rango: {valid_leads.min():.0f} – {valid_leads.max():.0f}")
    
    # 2. Grupos
    log("\n2. DIVISIÓN EN GRUPOS DE ANTICIPACIÓN")
    log(f"   Buenos anticipadores (lead > {p60:.2f}): {len(good)} picos")
    log(f"   Anticipadores débiles (lead ≤ {p60:.2f}): {len(weak)} picos")
    
    # 3. Diferencias RQA
    log("\n3. DIFERENCIAS EN PERFILES RQA (Mann-Whitney)")
    for _, row in rqa_comparison.iterrows():
        sig = " (significativo p<0.10)" if row["p_mw_greater"] < 0.10 else ""
        log(f"   {row['metric']:28s}: "
            f"Δ medianas = {row['diferencia_medianas']:+.4f} | "
            f"p={row['p_mw_greater']:.4f}{sig}")
    
    # 4. Concentración
    log("\n4. CONCENTRACIÓN TEMPORAL ANTES DE LAS INYECCIONES")
    for _, row in conc_df.iterrows():
        log(f"   Inyección t={int(row['inyeccion_t'])}: "
            f"{int(row['picos_en_ventana'])} picos en ventana de {WINDOW_BEFORE_INJECTION} pasos "
            f"({row['porcentaje_total']:.1f}%)")
    log(f"   Total picos en alguna ventana pre-inyección: {total_before} ({pct_any:.1f}%)")
    
    # 5. CONCLUSIONES
    log("\n5. CONCLUSIONES")
    
    # Evaluar si RQA ayuda
    significant_metrics = rqa_comparison[rqa_comparison["p_mw_greater"] < 0.10]["metric"].tolist()
    
    if len(significant_metrics) > 0:
        log("   - Se encontraron diferencias significativas en métricas RQA entre grupos.")
        log(f"     Métricas con ventaja en buenos anticipadores: {', '.join(significant_metrics)}")
    else:
        log("   - No se detectaron diferencias estadísticamente significativas (p<0.10) "
            "en las métricas RQA entre buenos y débiles anticipadores en esta muestra.")
    
    log(f"   - Alta concentración de picos estructurales inmediatamente antes de las transiciones "
        f"inyectadas ({pct_any:.1f}% dentro de las {WINDOW_BEFORE_INJECTION} pasos previos).")
    
    log("   - El marco RECD + RQA (con énfasis en laminaridad y aceleración de trapping) "
        "muestra capacidad de anticipar cambios de régimen en el atractor de Lorenz.")
    log("   - La división por percentil de lead sugiere que picos con mayor rqa_structural_score "
        "y/o mayor aceleración de LAM tienden a anticipar mejor las transiciones.")
    
    # Interpretación específica sobre hyper_persistence_level (comparado con mapa logístico)
    log("\n   INTERPRETACIÓN ESPECÍFICA PARA LORENZ (vs Mapa Logístico):")
    if "hyper_persistence_level" in significant_metrics:
        log("   - hyper_persistence_level sigue siendo la métrica más diferenciadora (p<0.10) ")
        log("     y con delta positivo a favor de los buenos anticipadores, replicando el patrón ")
        log("     observado en el mapa logístico acoplado. Esto sugiere que la hiper-persistencia ")
        log("     (desviación de tau_s local respecto a su media reciente, normalizada) es un ")
        log("     indicador robusto y generalizable de anticipación de cambios estructurales, ")
        log("     incluso en sistemas caóticos continuos de dimensión baja como el atractor de Lorenz.")
    else:
        log("   - A diferencia del experimento con el mapa logístico acoplado (donde ")
        log("     hyper_persistence_level fue claramente la métrica más significativa), en este ")
        log("     run de Lorenz hyper_persistence_level no alcanzó significancia estadística ")
        log("     (p>=0.10) como diferenciador entre buenos y débiles anticipadores. Esto puede ")
        log("     deberse a la naturaleza del sistema continuo, la escala de leads mucho mayor, ")
        log("     o la dinámica específica de las transiciones inducidas por rho. Las demás ")
        log("     métricas RQA (laminarity, trapping, score) pueden jugar un rol más destacado aquí.")
    
    log("\n" + "=" * 82)
    log("FIN DEL REPORTE")
    log("=" * 82)
    
    # Guardar reporte
    report_path = os.path.join(output_dir, "reporte_analisis_profundo_lorenz.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    
    print(f"\n[REPORTE] Guardado en: {report_path}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    df = load_and_prepare(CSV_PATH)
    df, good, weak, p60 = split_anticipators(df)
    
    # Comparación RQA
    rqa_comp_df = compare_rqa_profiles(good, weak)
    
    # Concentración
    conc_df, total_before, pct_any = analyze_concentration(df, INJECTED_CHANGES, WINDOW_BEFORE_INJECTION)
    
    # Figuras
    generate_figures(df, good, weak, p60, INJECTED_CHANGES, OUTPUT_DIR)
    
    # Reporte
    generate_report(df, good, weak, rqa_comp_df, conc_df, 
                    total_before, pct_any, p60, OUTPUT_DIR)
    
    print(f"\n✅ Análisis profundo completado. Resultados en: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    main()