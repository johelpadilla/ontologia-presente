# Material Suplementario

Este directorio contiene material adicional asociado al manuscrito 
"Hacia una ontología del presente en sistemas complejos".

## Contenido actual (borrador)

- `empirical_summary.csv` (placeholder): métricas resumidas de los experimentos con mapa logístico r=3.8 (0–15 % ruido) y atractor de Lorenz.
- Scripts de referencia: los pipelines RECD + RQA Config B completos se encuentran en el repositorio principal `proyecto_prediccion2/` (archivos `test_ruido_logistic.py`, `analisis_antisincronizacion.py`, etc.).

## Cómo generar las tablas detalladas

Ejecutar los scripts de validación del repositorio padre con la configuración documentada en el manuscrito (TAU_WINDOW=85, RQA Config B, etc.) y exportar las tablas de n_picos, mean_lead, antisincronización por ventana y tests estadísticos.

## Licencia

Mismo régimen que el manuscrito principal (CC-BY-4.0 para el contenido conceptual; los datos y código conservan las licencias de los repositorios de origen).