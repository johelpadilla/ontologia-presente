# Hacia una ontología del presente en sistemas complejos

**RECD, persistencia intensificada y la dinámica de la fragmentación**

**⚠️ VERSIÓN CONGELADA v0.1.0 — INMUTABLE — NO EDITAR ESTA CARPETA**

Esta es la versión oficial congelada del manuscrito (junio 2026).  
Sirve como base para citación, revisión interna, envío a revista y registro en Zenodo.

**Cualquier trabajo posterior se realizará en subcarpetas nuevas bajo `versions/`** (ver `../README.md` en la raíz del proyecto y `versions/README.md`).

---

Primer borrador formal para publicación académica (v0.1.0, junio 2026).

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

## Estado actual del manuscrito

- **Versión**: 0.1.0-draft (primer borrador formal listo para revisión interna y envío).
- **Idioma**: Español.
- **Longitud aproximada**: ~6500–7500 palabras (ajustable).
- **Contenido**:
  - Definiciones precisas y rigurosas de RECD, τ_s (Tau Sistémico), hiper-persistencia, trapping estructural (RQA Config B), intensidad compuesta I, antisincronización y fragmentación del presente.
  - Tres capas del presente claramente diferenciadas.
  - Evidencia empírica resumida (121 picos estructurales en logístico r=3.8; 123 en Lorenz; reducción significativa de antisincronización cerca de picos; robustez hasta 10–15 % de ruido).
  - Dinámica de resistencia bidireccional y memoria activa.
  - Analogía limitada con sistemas de múltiples escalas (huracán maduro) y preguntas abiertas.
- **Referencias**: Todas las referencias no clásicas provienen de los trabajos del autor, con DOIs de Zenodo y Preprints.org cuando están disponibles.
- **Próximos pasos recomendados**:
  1. Revisión interna y adición de 1–2 figuras conceptuales adicionales.
  2. Selección de revista objetivo y adaptación de clase / longitud / estilo de referencias.
  3. Generación de material suplementario detallado (tablas de métricas por régimen y nivel de ruido).
  4. Asignación de DOI definitivo mediante Zenodo (ver instrucciones abajo).

---

## Cómo citar este trabajo (placeholder)

**Formato APA (recomendado mientras se asigna el DOI de Zenodo):**

Padilla-Villanueva, J. (2026). *Hacia una ontología del presente en sistemas complejos: RECD, persistencia intensificada y la dinámica de la fragmentación* (v0.1.0-draft). Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX

**BibTeX / BibLaTeX entry (placeholder):**

```bibtex
@article{padilla_ontologia_presente_2026,
  author  = {Padilla-Villanueva, Johel},
  title   = {Hacia una ontología del presente en sistemas complejos: RECD, persistencia intensificada y la dinámica de la fragmentación},
  year    = {2026},
  publisher = {Zenodo},
  doi     = {10.5281/zenodo.XXXXXXX},
  url     = {https://doi.org/10.5281/zenodo.XXXXXXX},
  version = {0.1.0-draft}
}
```

Reemplaza `XXXXXXX` por el identificador real una vez publicado en Zenodo.

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

*Documento generado como primer borrador formal (2026).*
