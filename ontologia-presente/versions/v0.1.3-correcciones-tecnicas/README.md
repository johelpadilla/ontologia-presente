# Hacia una ontología del presente en sistemas complejos

**RECD, persistencia intensificada y la dinámica de la fragmentación**

**⚠️ VERSIÓN DE TRABAJO v0.1.2-mejoras-adicionales — EDITAR SOLO AQUÍ**

Esta carpeta es una **versión de trabajo** creada por copia limpia de `versions/v0.1.1-mejoras-ontologicas/` (junio 2026).  
Contiene el manuscrito con mejoras adicionales de rigor ontológico: primacía del concepto de filtrado probabilístico (con «resistencia» como heurístico secundario), clarificación del estatus relacional/transicional de la Capa 2, explicitación de propiedades irreductibles por capa, Sec. 7.3 más concisa, mejor flujo evidencia-ontología, abstract más económico y consistencia terminológica general.

**La versión oficial congelada e inmutable sigue siendo** `versions/v0.1.0-frozen/`.  
**Nunca editar** la congelada ni la raíz del proyecto. Todo trabajo futuro va en nuevas subcarpetas.

---

**Estado de esta versión**: 14 páginas (compilación limpia), TOC y Referencias completos, 0 errores LaTeX / Overfull críticos significativos. Mejoras detalladas en el CHANGELOG.md de esta carpeta. Cambios adicionales deben ir en **otra** subcarpeta nueva.

Este repositorio contiene el manuscrito académico que sintetiza el marco ontológico del **Reloj Extramental Discreto (RECD)** con la noción de presente estratificado en tres capas, el rol regulador de la antisincronización, la dinámica de resistencia bidireccional y la memoria activa. El artículo está escrito en español, con rigor terminológico y matemático, e integra validaciones empíricas previas (mapas logísticos acoplados r=3.8, atractor de Lorenz con inyecciones de ρ, robustez al ruido y análisis explícito de antisincronización).

---

## Estructura del repositorio

```
ontologia-presente/
├── manuscript/
│   ├── main.tex                 # Documento principal (compilable)
│   ├── sections/                # Secciones modulares (introducción, fundamentos, capas, etc.)
│   └── figures/                 # Diagramas conceptuales (TikZ u externos)
├── supplementary/               # Material suplementario (tablas detalladas, código de validación resumido)
├── references/
│   └── references.bib           # Bibliografía curada (clásicos + obras del autor en Zenodo/Preprints)
├── CITATION.cff
├── README.md
├── .gitignore
└── CHANGELOG.md
```

---

## Cómo compilar el artículo

### Requisitos
- TeX Live (o MacTeX / MiKTeX) reciente con soporte para:
  - `amsmath`, `amssymb`, `booktabs`, `tcolorbox`, `tikz`, `hyperref`, `geometry`, `enumitem`
  - `biblatex` + `biber` (recomendado) **o** BibTeX tradicional
- `make` (opcional, para flujos futuros)

### Compilación recomendada (biblatex + biber)

```bash
cd manuscript
pdflatex main
biber main
pdflatex main
pdflatex main   # para referencias y tabla de contenidos
```

### Compilación alternativa (BibTeX clásico)

```bash
cd manuscript
# LIMPIEZA OBLIGATORIA (evita .toc/.bbl stale)
rm -f main.aux main.log main.out main.toc main.bbl main.blg

pdflatex main
bibtex main
pdflatex main
pdflatex main
```

**CRÍTICO — Nunca olvides TOC ni Referencias:**

La Tabla de Contenidos (`\tableofcontents`) y la sección "Referencias" (con `\section*{Referencias}\addcontentsline{toc}{section}{Referencias}` + `\bibliography`) **solo aparecen completas y sin citas ??** si ejecutas **siempre la secuencia completa de 4 comandos** después de limpiar auxiliares. 

- Un solo `pdflatex` deja el Índice vacío o incompleto y las referencias sin expandir.
- Después de cambios en `.bib` o secciones, **repite la secuencia completa**.
- El PDF final debe tener: página "Índice" con todas las secciones + sección "Referencias" al final con entradas reales (DOIs visibles).

El PDF resultante aparecerá como `manuscript/main.pdf`.

**Notas de compilación:**
- El manuscrito utiliza `article` class con paquetes estándar para facilitar adaptación a clases de revista (elsarticle, revtex, IEEEtran, etc.).
- `\sloppy` se aplica localmente en el bloque de Referencias para evitar overfulls en títulos largos + URLs/DOIs.
- Para producción final, se recomienda activar `\usepackage[spanish]{babel}` y ajustar márgenes/longitud según la revista objetivo.

---

## Estado actual del manuscrito (v0.1.1-mejoras-ontologicas)

- **Versión**: v0.1.1-mejoras-ontologicas (versión de trabajo con mejoras ontológicas y terminológicas; 14 páginas).
- **Idioma**: Español.
- **Longitud**: 14 páginas (compilado final limpio).
- **Mejoras principales de esta versión** (ver CHANGELOG.md para detalle completo):
  - Definición estricta, operacional y no metafórica de «resistencia» como efecto estructural de filtrado probabilístico (sin fuerza activa ni agente).
  - Definiciones de las tres capas del presente más rigurosas, con marcadores operacionales explícitos y no reductibilidad ontológica débil reforzada.
  - Subsección «Limitaciones y objeciones al marco propuesto» con respuestas honestas a 5 objeciones válidas (reificación, metáfora, causación descendente, circularidad, subdeterminación).
  - Eliminación completa de la frase “Primera versión formal para publicación (junio 2026).”.
  - Consistencia terminológica total (sin lenguaje antropomórfico residual); correcciones técnicas (bib, paquetes, sin Overfull críticos).
- **Contenido base heredado y mejorado**:
  - RECD, τ_s, hiper-persistencia, RQA Config B, antisincronización como regulador de permeabilidad.
  - Evidencia empírica (121/123 picos, reducción significativa de antisincronización, robustez al ruido 0-15 %).
  - Dinámica de filtrado probabilístico bidireccional («resistencia ascendente/descendente»).
  - Analogía heurística (huracán), preguntas abiertas y ahora objeciones honestas.
- **Referencias**: Completas, con DOIs de Zenodo (10.5281/zenodo.XXXX) y Preprints.org (10.20944/...) para obras del autor + clásicos. Formato verificado y sin errores de parseo.
- **Próximos pasos**: Revisión interna adicional, posible condensación o expansión según revista objetivo, generación de release/Zenodo **desde una versión estable** (no desde esta carpeta de trabajo en curso). Cualquier cambio adicional debe hacerse en **otra** subcarpeta nueva bajo versions/.

---

## Cómo citar este trabajo (placeholder)

**Importante**: Para citación oficial use siempre la versión congelada (`v0.1.0-frozen`). Esta `v0.1.2-mejoras-adicionales` es una versión de trabajo interna con refinamientos ontológicos adicionales (filtrado probabilístico como concepto primario, Capa 2 como relacional/transicional, etc.).

**Formato APA (esta versión de trabajo):**

Padilla-Villanueva, J. (2026). *Hacia una ontología del presente en sistemas complejos: RECD, persistencia intensificada y la dinámica de la fragmentación* (v0.1.2-mejoras-adicionales, working copy with additional ontological refinements). Ubicación: `versions/v0.1.2-mejoras-adicionales/` del repositorio.

**BibTeX / BibLaTeX entry (placeholder para esta versión):**

```bibtex
@article{padilla_ontologia_presente_2026,
  author  = {Padilla-Villanueva, Johel},
  title   = {Hacia una ontología del presente en sistemas complejos: RECD, persistencia intensificada y la dinámica de la fragmentación},
  year    = {2026},
  publisher = {Zenodo},
  doi     = {10.5281/zenodo.XXXXXXX},
  url     = {https://doi.org/10.5281/zenodo.XXXXXXX},
  version = {0.1.2-mejoras-adicionales}
}
```

Reemplaza `XXXXXXX` por el identificador real una vez publicado en Zenodo (asignar sobre la versión estable elegida, no sobre copias de trabajo).

---

## Conexión con Zenodo (GitHub Releases)

1. Asegúrate de que el repositorio esté en GitHub (público o privado según preferencia).
2. Crea un *release* en GitHub:
   - Ve a la pestaña "Releases" → "Draft a new release".
   - Elige un tag (ej. `v0.1.0-draft`).
   - Sube el PDF compilado (`main.pdf`) y el archivo ZIP del repositorio completo como assets.
3. Conecta el repositorio a Zenodo:
   - En [zenodo.org](https://zenodo.org) inicia sesión con tu cuenta GitHub.
   - Ve a "GitHub" en la barra lateral → selecciona el repositorio `ontologia-presente`.
   - Activa "Enable" para el repositorio.
4. En el siguiente push de un tag/release, Zenodo creará automáticamente un registro con DOI.
5. Actualiza:
   - `CITATION.cff` (campo `doi`)
   - `README.md` (sección de citación)
   - Cualquier mención interna al DOI.

Una vez asignado el DOI de Zenodo, el trabajo queda permanentemente citable y versionado.

---

## Licencia y derechos

El contenido conceptual y textual está bajo licencia **CC-BY-4.0** (ver `CITATION.cff`). El código de soporte (si se añade en `supplementary/`) se publicará bajo la misma licencia o MIT según decisión del autor.

---

## Contacto / Contribuciones

Este es un borrador en desarrollo del autor principal. Sugerencias de mejora, correcciones terminológicas o adiciones empíricas son bienvenidas mediante issues o pull requests una vez el repositorio esté público.

**Autor**: Johel Padilla-Villanueva  
Universidad de Puerto Rico, Recinto de Ciencias Médicas

---

---

**Nota de versión de trabajo (v0.1.2-mejoras-adicionales)**

Esta carpeta implementa la ronda adicional de mejoras de rigor ontológico:
- Reevaluación del término «resistencia»: primacía del «filtrado probabilístico bidireccional/ascendente/descendente» como concepto operativo central; «resistencia» reducida a heurístico secundario entre comillas.
- Clarificación del estatus de la Capa 2 (relacional/transicional plena, «puente ontológico» que introduce coherencia de escalas irreducible).
- Fortalecimiento explícito de las propiedades nuevas e irreductibles introducidas por cada capa superior.
- Sección 7.3 más concisa y directa; flujo mejorado entre evidencia (Sec. 3) e interpretación ontológica (Secs. 4-5); abstract más económico; consistencia terminológica y limpieza de lenguaje.
- Documentación actualizada dentro de la carpeta (CHANGELOG + README).

La política de versiones se respeta estrictamente: ediciones solo dentro de subcarpetas nuevas; la congelada `v0.1.0-frozen/` permanece inmutable.

*Compilado final: 14 páginas, junio 2026. Ver CHANGELOG.md de esta carpeta para el registro detallado de cambios.*
