# Changelog

All notable changes to this repository and the manuscript will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.12] - 2026-06-15

### Base (nueva versión base oficial / congelada)

- Se establece `versions/v0.1.12/` como la **nueva versión base** del manuscrito (reemplaza a v0.1.0-frozen como referencia principal).
- Carpeta renombrada de `v0.1.12-correccion-figura4` a `v0.1.12` para nombre limpio y permanente.
- Metadatos actualizados (READMEs de la versión y de la raíz, versions/README.md, CITATION.cff en raíz y en la versión, CHANGELOGs) para reflejar consistentemente que v0.1.12 es la base actual.
- Figura 4 restaurada al estado que compiló perfectamente (sin desbordamiento de margen derecho, buen equilibrio visual y espaciado) según preferencia del autor (estado de v0.1.10).
- Todo el pulido ligero de fluidez de rondas previas preservado.
- Compilación limpia de 14 páginas con TOC y Referencias dentro de `versions/v0.1.12/manuscript/`.
- Política actualizada: trabajo futuro solo en copias a nuevas subcarpetas bajo versions/.

## [0.1.0] - 2026-06-15

### Added
- First formal draft for academic journal submission.
- Complete manuscript (`manuscript/main.tex`) transforming the ontological synthesis into a rigorous, self-contained academic article in Spanish.
- Modular section structure under `manuscript/sections/`.
- Curated `references/references.bib` with classical sources and author works preferentially referenced via Zenodo DOIs and Preprints.org (including Bayesian accumulator formulation, Tau Sistémico RECD framework, Feigenbaum reduction, Polo dialogue, and RQA integration).
- Professional `CITATION.cff` prepared for Zenodo/GitHub integration.
- Comprehensive `README.md` with compilation instructions, citation placeholder, and Zenodo connection guidance.
- `.gitignore` and initial `CHANGELOG.md`.
- Directory skeleton: `supplementary/`, `manuscript/figures/` (ready for TikZ or external diagrams of the three layers and resistance dynamics).

### Notes
- This draft presents the conceptual synthesis of the RECD framework, the definition of the three layers of the present, the role of antisynchronization as a regulator of fragmentation, bidirectional resistance, and active memory.
- Empirical grounding is summarized from prior validated pipelines (logistic r=3.8, Lorenz with ρ-injections, noise robustness up to 10–15 %, and explicit antisynchronization analysis) without process meta-language.
- Ready for internal review, figure polishing, and target-journal adaptation (class, length, reference style).
- Next steps: addition of 1–2 conceptual figures (layer diagram + resistance schema), expansion of empirical table if required by target journal, and assignment of final Zenodo DOI upon first public release.

## [Unreleased]
- Planned: English version / extended abstract for broader dissemination.
- Planned: Supplementary material with detailed numerical tables from the 121 / 123 structural peak validations and antisynchronization statistics.

## [0.1.1-mejoras-ontologicas] - 2026-06-15 (working copy under versions/)
- Nueva subcarpeta de trabajo creada por copia limpia de v0.1.0-frozen/.
- Mejoras ontológicas: definición estricta de «resistencia» (efecto estructural de filtrado probabilístico, sin antropomorfismo, neologismos en « »); definiciones de capas más rigurosas + no reductibilidad explícita; subsección «Limitaciones y objeciones al marco propuesto» con 5 respuestas honestas.
- Eliminada frase “Primera versión formal para publicación (junio 2026).”.
- Correcciones técnicas (bib fractal, order de paquetes, 0 errores/Overfull críticos), 14 páginas con TOC y Referencias.
- CHANGELOG y README actualizados dentro de la subcarpeta.
- Ver detalles completos en versions/v0.1.1-mejoras-ontologicas/CHANGELOG.md .

## [0.1.2-mejoras-adicionales] - 2026-06-15 (working copy under versions/)
- Nueva subcarpeta creada por copia limpia de v0.1.1-mejoras-ontologicas/.
- Reevaluación de «resistencia»: primacía del filtrado probabilístico (ascendente/descendente) como concepto operativo riguroso; «resistencia» como heurístico secundario entre comillas.
- Capa 2 clarificada como capa relacional/transicional plena («puente ontológico») con propiedad irreducible de coherencia de escalas.
- No-reductibilidad fortalecida con explicitación de la propiedad nueva que introduce cada capa superior.
- Sec. 7.3 acortada y más directa; flujo evidencia-ontología mejorado; abstract más económico; consistencia terminológica.
- 14 páginas, compilación limpia, docs internas actualizadas.
- Detalles en versions/v0.1.2-mejoras-adicionales/CHANGELOG.md y su README.

## [0.1.1] - 2026-06-15
### Fixed
- Compilación: se reforzó que **TOC (Índice) y sección Referencias nunca se omitan**. La secuencia completa obligatoria ahora está documentada explícitamente en README (limpieza de aux + pdflatex + bibtex + pdflatex + pdflatex). 
- Se añadió `\sloppy` (con restauración) dentro del bloque de Referencias en `main.tex` para eliminar los overfull hbox en entradas largas con títulos + DOI/URL (incluyendo el caso del preprint de dimensión fractal).
- Verificación post-compilación: `main.toc` registra todas las secciones + "Referencias" (pág. 12); el PDF muestra "Índice" poblado en pág. 2; todas las citas resueltas como `[Padilla-Villanueva, 2026a,e]` etc. (sin ??); la lista de Referencias aparece completa al final con entradas reales y DOIs.
- Se actualizó el proceso mental de compilación: **nunca compilar con pases incompletos**. Los archivos `main.pdf`, `main.toc` y `main.bbl` se regeneran siempre con la secuencia de 4 pases después de rm de auxiliares.

## [0.1.0-frozen] - 2026-06-15
### Changed (major policy)
- **Se declara v0.1.0 como versión congelada oficial.**
- Se implementa control estricto de versiones mediante subcarpetas:
  - Se creó `versions/v0.1.0-frozen/` con una copia limpia e inmutable del estado completo (fuentes, `main.pdf` final de 13 páginas con TOC y Referencias correctos, figuras de los experimentos de ruido/antisincronización, bibliografía con DOIs, suplemento).
  - Se excluyeron deliberadamente todos los archivos auxiliares de compilación de LaTeX del snapshot.
  - Se actualizó el `README.md` de la raíz para convertirlo en índice de versiones + documentación de la nueva política ("de ahora en adelante todo el trabajo futuro va en subcarpetas bajo versions/").
  - Se creó `versions/README.md` con el procedimiento exacto para crear y trabajar con nuevas versiones.
  - Se marcó explícitamente el README dentro de `v0.1.0-frozen/` como "VERSIÓN CONGELADA — INMUTABLE — NO EDITAR".
- A partir de este punto, **cualquier modificación solicitada** se implementará creando una nueva carpeta de versión (ej. copiando v0.1.0-frozen y editando solo dentro de la copia).
- Esto proporciona trazabilidad completa y control de versiones para fines de publicación académica y registro en Zenodo.

### Previous entries below refer to development leading to the freeze.