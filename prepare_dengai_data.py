#!/usr/bin/env python3
"""
Script auxiliar para descargar y preparar los datos del dataset DengAI.

Uso:
    python prepare_dengai_data.py

Este script:
- Intenta descargar automáticamente los archivos desde fuentes públicas.
- Si falla, muestra instrucciones claras para descarga manual.
- Une dengue_features_train.csv + dengue_labels_train.csv
- Guarda el resultado en data/datos_dengai_completo.csv

Después de ejecutar este script (o colocar los archivos manualmente),
puedes correr directamente:
    python test_prediccion2_real.py
"""

import os
import sys
import requests
import pandas as pd
from io import StringIO

DATA_DIR = "data"
FEATURES_FILE = os.path.join(DATA_DIR, "dengue_features_train.csv")
LABELS_FILE = os.path.join(DATA_DIR, "dengue_labels_train.csv")
MERGED_FILE = os.path.join(DATA_DIR, "datos_dengai_completo.csv")

# Algunas URLs públicas conocidas donde la gente ha subido los CSVs de DengAI (raw GitHub).
# Si fallan, el script cae elegantemente a instrucciones manuales.
PUBLIC_URLS = {
    "features": [
        "https://raw.githubusercontent.com/drivendata/dengue-forecasting/master/dengue_features_train.csv",
        # Fallbacks adicionales si existen en otros repos (puedes agregar más)
    ],
    "labels": [
        "https://raw.githubusercontent.com/drivendata/dengue-forecasting/master/dengue_labels_train.csv",
    ]
}

def download_file(url: str, dest_path: str, description: str) -> bool:
    """Intenta descargar un archivo con requests."""
    print(f"[DESCARGA] Intentando descargar {description} desde {url} ...")
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200 and len(resp.content) > 10000:  # sanity check
            with open(dest_path, "wb") as f:
                f.write(resp.content)
            print(f"[OK] Descargado: {dest_path} ({len(resp.content)} bytes)")
            return True
        else:
            print(f"[WARN] Descarga fallida (status={resp.status_code})")
    except Exception as e:
        print(f"[WARN] Error en descarga: {e}")
    return False


def try_auto_download():
    """Intenta descargar features y labels desde URLs públicas."""
    os.makedirs(DATA_DIR, exist_ok=True)

    features_ok = os.path.exists(FEATURES_FILE)
    labels_ok = os.path.exists(LABELS_FILE)

    if not features_ok:
        for url in PUBLIC_URLS["features"]:
            if download_file(url, FEATURES_FILE, "features (entrenamiento)"):
                features_ok = True
                break

    if not labels_ok:
        for url in PUBLIC_URLS["labels"]:
            if download_file(url, LABELS_FILE, "labels (total_cases)"):
                labels_ok = True
                break

    return features_ok and labels_ok


def merge_and_save():
    """Une features + labels y guarda el archivo combinado."""
    if not (os.path.exists(FEATURES_FILE) and os.path.exists(LABELS_FILE)):
        print("[ERROR] No se encontraron los archivos de features y labels para unir.")
        return False

    print("[PREPARACIÓN] Leyendo archivos...")
    features = pd.read_csv(FEATURES_FILE)
    labels = pd.read_csv(LABELS_FILE)

    print(f"    Features: {features.shape}")
    print(f"    Labels:   {labels.shape}")

    # Unir por las claves comunes
    merged = pd.merge(
        features,
        labels,
        on=["city", "year", "weekofyear"],
        how="left"
    )

    # Ordenar cronológicamente
    merged = merged.sort_values(["city", "year", "weekofyear"]).reset_index(drop=True)

    # Guardar
    merged.to_csv(MERGED_FILE, index=False)
    print(f"[OK] Archivo combinado guardado en: {MERGED_FILE}")
    print(f"    Total filas: {len(merged)}")
    print(f"    Ciudades: {merged['city'].unique().tolist()}")
    print(f"    Rango de semanas: {merged['year'].min()}-{merged['weekofyear'].min()} "
          f"a {merged['year'].max()}-{merged['weekofyear'].max()}")

    return True


def print_manual_instructions():
    """Instrucciones claras para el usuario si la descarga automática falla."""
    print("\n" + "=" * 70)
    print("DESCARGA MANUAL REQUERIDA (DrivenData DengAI)")
    print("=" * 70)
    print("""
1. Ve a la página de la competencia (registro gratuito):
   https://www.drivendata.org/competitions/44/dengai-predicting-disease-spread/data/

2. Descarga estos dos archivos:
   - dengue_features_train.csv
   - dengue_labels_train.csv

3. Colócalos dentro de la carpeta 'data/' de este proyecto:
   proyecto_prediccion2/
   └── data/
       ├── dengue_features_train.csv
       └── dengue_labels_train.csv

4. Vuelve a ejecutar este script:
       python prepare_dengai_data.py

   O ejecuta directamente el análisis (el script principal intentará unirlos):
       python test_prediccion2_real.py

El script unirá automáticamente ambos archivos y creará:
   data/datos_dengai_completo.csv
""")
    print("=" * 70 + "\n")


def main():
    print("\n=== Preparación de datos DengAI (Predicción 2) ===\n")

    os.makedirs(DATA_DIR, exist_ok=True)

    # Si ya existe el archivo final, no hacemos nada
    if os.path.exists(MERGED_FILE):
        print(f"[INFO] Ya existe {MERGED_FILE}. No es necesario preparar de nuevo.")
        print("       Si quieres regenerarlo, bórralo y vuelve a ejecutar.")
        return

    # Paso 1: intentar descarga automática
    auto_success = try_auto_download()

    if not auto_success:
        # Paso 2: verificar si los archivos ya están en data/ (descarga manual previa)
        if os.path.exists(FEATURES_FILE) and os.path.exists(LABELS_FILE):
            print("[INFO] Se encontraron los archivos de features y labels en data/. Se procederá a unirlos.")
            auto_success = True
        else:
            print("[INFO] No fue posible descargar automáticamente los datos.")
            print_manual_instructions()
            sys.exit(1)

    # Paso 3: unir y guardar
    if merge_and_save():
        print("\n[LISTO] Datos preparados correctamente.")
        print("        Ahora puedes ejecutar: python test_prediccion2_real.py\n")
    else:
        print("[ERROR] No se pudo preparar el archivo combinado.")
        sys.exit(1)


if __name__ == "__main__":
    main()