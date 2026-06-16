# Versiones del manuscrito

Este directorio contiene las versiones controladas del artículo **"Hacia una ontología del presente en sistemas complejos"**.

## Política de versionado (a partir de junio 2026)

- **v0.1.12/** — Nueva versión base / congelada oficial (junio 2026).  
  Esta es ahora la instantánea de referencia para citación, envío a revista y Zenodo.  
  14 páginas, TOC + Referencias completos, Figura 4 en estado preferido y ajustado a márgenes.  
  **No se realizan modificaciones directamente aquí.** Copiar a nueva subcarpeta para cualquier trabajo futuro.

- Todas las modificaciones, experimentos, revisiones, nuevas figuras o cambios de redacción **se realizarán en nuevas subcarpetas** dentro de `versions/` (ej. `v0.1.1-revision-figuras/`, `v0.2.0-ampliacion-empirica/`, etc.).

- Cada nueva versión suele partir de una copia limpia de la versión anterior (normalmente de la última estable o de la congelada).

- El directorio raíz del proyecto (`ontologia-presente/`) contiene solo documentación de alto nivel (este índice, CHANGELOG general, CITATION de la versión base) y ya **no** es el lugar de trabajo activo.

## Lista de versiones

- `v0.1.12/` — Nueva versión base oficial. Incluye pulido final de fluidez (Introducción, evidencia, jerarquía), restauración de la Figura 4 al render perfecto de v0.1.10 (sin overflow, espaciado equilibrado y elegante), 14 páginas con TOC y Referencias. Establecida como base para uso futuro. Junio 2026.
- `v0.1.0-frozen/` — Borrador formal inicial + correcciones de compilación (TOC, Referencias, breakurl, neologismos en « », integración de figuras de ruido y antisincronización). 13 páginas. Junio 2026. (histórica)
- `v0.1.1-mejoras-ontologicas/` — Versión de trabajo con mejoras ontológicas y terminológicas: definición estricta operacional de «resistencia» como efecto estructural de filtrado probabilístico (sin lenguaje antropomórfico), definiciones más rigurosas y explícitamente no reductibles de las tres capas, nueva subsección «Limitaciones y objeciones al marco propuesto» con respuestas honestas a 5 objeciones válidas, eliminación de la frase de versión formal, correcciones técnicas y consistencia terminológica. Compilación produce 14 páginas con TOC y Referencias completas. Basada en copia limpia de la congelada. Junio 2026.
- `v0.1.2-mejoras-adicionales/` — Nueva versión de trabajo centrada en rigor ontológico adicional: reevaluación y jerarquización del término «resistencia» (primacía del concepto de «filtrado probabilístico ascendente/descendente» como noción operativa principal; «resistencia» reducida a nombre heurístico secundario entre comillas); clarificación del estatus ontológico de la Capa 2 como capa relacional/transicional plena que introduce coherencia de escalas irreducible; fortalecimiento explícito de qué propiedades nuevas introduce cada capa superior; Sec. 7.3 (objeciones) más concisa y directa; mejoras de flujo entre evidencia empírica e interpretación ontológica; consistencia terminológica y economy en abstract; actualizaciones menores de lenguaje. 14 páginas. Basada en copia de v0.1.1. Junio 2026.
- `v0.1.3-correcciones-tecnicas/` — Versión enfocada en correcciones técnicas y pulido final: corrección del texto truncado en 3.3 «Robustez al ruido» (completado para listar claramente los niveles 0 %, 5 %, 10 % y 15 % con redacción fluida y renderizado completo); revisión y fixes de overflow/maquetación (párrafos, tcolorbox, figuras, References); mejora ligera de fluidez en transiciones Sec. 3 → Seccs. 4-5 y pulido general de claridad/economía de lenguaje (sin cambios conceptuales). Compilación limpia de 14 páginas sin texto cortado. Basada en copia de v0.1.2. Junio 2026.
- `v0.1.4-pulido-final/` — Ronda final de pulido maduro: Sección 7.3 (Limitaciones y objeciones) hecha significativamente más concisa y directa (sin repeticiones ni tono defensivo); reducción adicional de la prominencia de «resistencia ascendente/descendente» (prioridad clara al «filtrado probabilístico bidireccional» como término principal; términos entre comillas solo como etiquetas heurísticas secundarias y ocasionales, especialmente en abstract y Secc. 5); mejora de fluidez argumentativa entre Secc. 3 (Evidencia empírica: picos, antisincronización, robustez) y Seccs. 4-5 (capas y dinámica de filtrado), con transiciones más naturales y coherentes. Sin cambios conceptuales ni reducción de extensión. 14 páginas, compilación limpia. Basada en copia de v0.1.3. Junio 2026.

## Cómo trabajar con una versión

1. Copia la versión base deseada a una nueva carpeta:
   ```bash
   cp -a v0.1.0-frozen/ v0.1.1-mi-cambio/
   ```
2. Edita solo dentro de `v0.1.1-mi-cambio/`.
3. Actualiza el CHANGELOG **de esa versión** y el README de la versión si aplica.
4. Compila dentro de su propio `manuscript/`.
5. Documenta el nuevo estado en el CHANGELOG de la raíz si corresponde.

Esto garantiza trazabilidad completa y control estricto de versiones para publicación académica.
