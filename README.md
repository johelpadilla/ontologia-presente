# Proyecto: Test Empírico de la Predicción 2 (RECD + Estructura Espacial)

Análisis completo del marco **RECD + estructura espacial** aplicado al dataset real **DengAI** (predicción de brotes de dengue en San Juan e Iquitos).

## Objetivo

Evaluar la predicción:

> "Los picos fuertes de intensidad I_i(k) preceden cambios en la estructura de relaciones del sistema con mayor adelanto que otros detectores ordinales."

## Estructura del proyecto

```
proyecto_prediccion2/
├── data/
│   └── datos_dengai_completo.csv          # se genera automáticamente
├── prepare_dengai_data.py                 # script auxiliar de descarga + merge
├── test_prediccion2_real.py               # script principal (¡ejecuta esto!)
├── README.md
└── resultados_prediccion2/                # se crea al correr el análisis
    ├── sj_fig1_tau_s_series.png
    ├── sj_fig2_I_intensity.png
    ├── ...
    └── iq_*.png (si analizas ambas ciudades)
```

## Uso más simple (mínimo esfuerzo)

```bash
cd proyecto_prediccion2
python test_prediccion2_real.py
```

El script se encarga de todo:
- Busca o prepara automáticamente los datos.
- Filtra por ciudad (San Juan / Iquitos / ambas).
- Ejecuta el pipeline completo de la Predicción 2.
- Genera las 6 figuras principales.
- Imprime un resumen claro con test estadístico.

## Configuración rápida

Edita solo estas líneas al principio de `test_prediccion2_real.py`:

```python
CITY = "sj"          # "sj" = San Juan
                     # "iq" = Iquitos
                     # None = ambas ciudades (se analizan por separado)
```

Otras opciones ajustables (ventanas, percentiles, etc.) también están claramente marcadas al inicio del script.

## Cómo obtener los datos

### Opción recomendada (automática)

1. Ejecuta:
   ```bash
   python prepare_dengai_data.py
   ```

2. Si la descarga automática falla (común por login requerido en DrivenData), el script te dará instrucciones claras.

### Opción manual (siempre funciona)

1. Ve a: https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/data/
2. Descarga (registro gratuito):
   - `dengue_features_train.csv`
   - `dengue_labels_train.csv`
3. Colócalos en la carpeta `data/`:
   ```
   data/
   ├── dengue_features_train.csv
   └── dengue_labels_train.csv
   ```
4. Ejecuta:
   ```bash
   python test_prediccion2_real.py
   ```
   (El script unirá automáticamente los archivos y creará `datos_dengai_completo.csv`).

## Qué hace el pipeline

- Carga y limpia los datos reales de DengAI (incidencia + variables climáticas).
- Define **3 regiones temáticas** (Incidencia+Temperatura, Incidencia+Humedad+Precip, Clima+NDVI).
- Calcula métricas RECD:
  - `tau_s` local por región (ventana deslizante + entropía de permutación).
  - Reloj local `T_i(k)`.
  - Coherencia inter-regional `C_ij(k)`.
  - Densidad espacial `rho_i(k)`.
  - Peso y Gamma (basados en hiper-persistencia).
  - Producto de intensidad `I_i(k)`.
- Detecta **picos fuertes** de `I_i` (donde los 3 componentes están altos simultáneamente).
- Detecta **cambios estructurales** mediante distancia de Frobenius entre matrices de coherencia.
- Calcula **adelantos** (lead times) de los picos de I_i vs otros detectores ordinales.
- Realiza test estadístico no paramétrico (Mann-Whitney + permutation test).
- Genera y guarda las 6 figuras principales.

## Figuras generadas

Todas se guardan en `resultados_prediccion2/` con prefijo de ciudad (`sj_` o `iq_`) cuando corresponde:

- `fig1_tau_s_series.png`
- `fig2_I_intensity.png`
- `fig3_coherence_matrices.png`
- `fig4_lead_distributions.png`
- `fig5_mean_leads.png`
- `fig6_coherence_distance.png`

## Requisitos

```bash
pip install numpy pandas matplotlib seaborn scipy
```

## Notas

- El código es completamente modular y está fuertemente comentado.
- Si ejecutas con `CITY = None` obtendrás resultados independientes para San Juan e Iquitos.
- Los resultados (número de picos, adelantos, significancia estadística) dependerán de los datos reales y de los parámetros elegidos.
- Este proyecto está diseñado para que un usuario final pueda obtener el análisis completo con el menor esfuerzo posible.

## Autor / Contexto

Implementación del test empírico de la **Predicción 2** del marco RECD + estructura espacial aplicado a un sistema socio-ecológico real (dengue).

¡Listo para ejecutar!
```bash
python test_prediccion2_real.py
```
---

## Código Python de soporte para el manuscrito ontológico

Este repositorio también contiene los experimentos sintéticos y análisis que fundamentan el artículo académico:

**"Hacia una ontología del presente en sistemas complejos: RECD, persistencia intensificada y la dinámica de la fragmentación"**

### Experimentos clave

- `test_ruido_logistic.py` — Test de robustez al ruido (0 %, 5 %, 10 %, 15 % gaussiano) en mapa logístico acoplado (r=3.8). Incluye RECD (τ_s Bandt-Pompe), RQA Config B, detección de picos y métricas.
- `analisis_antisincronizacion.py` — Análisis central de antisincronización (desviación estándar de τ_s) como regulador de la transición de intensificaciones locales a reorganización global. Tests Mann-Whitney, ventanas, picos.
- `analisis_refinado_rqa_logistic_feigenbaum*.py` y `analisis_refinado_rqa_lorenz*.py` — Análisis refinado con universalidad de Feigenbaum, atractor de Lorenz, norma de Frobenius, adelantos estadísticos y evidencia de las tres capas.

### Manuscrito teórico (versión base actual)

La ontología formal de tres capas (Capa 1: presente local intensificado, Capa 2: coherencia relacional / puente ontológico, Capa 3: reorganización estructural) con el mecanismo de **filtrado probabilístico bidireccional** está en:

```
ontologia-presente/
└── versions/
    └── v0.1.12/          ← Versión base oficial (junio 2026)
        ├── manuscript/
        │   └── main.pdf  (14 páginas, TOC + Referencias)
        └── ...
```

Esta es la versión recomendada para revisión, citación y trabajo futuro.

### Cómo citar el código

Si utilizas los scripts o los resultados empíricos, por favor cita el manuscrito y este repositorio.

