# Changelog

All notable changes to this repository and the manuscript will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2-mejoras-adicionales] - 2026-06-15

### Changed (rigor ontológico adicional, copia limpia de v0.1.1)
- **Reevaluación de «resistencia»**: El concepto primario y riguroso es ahora el de **filtrado probabilístico ascendente/descendente** (bidireccional). Se define explícitamente como efecto estructural sin fuerza ni agente. Los términos «resistencia ascendente» y «resistencia descendente» se subordinan como nombres heurísticos secundarios entre comillas (útiles para la intuición pero no centrales). Se actualizó el título de sección, subsecciones y todas las referencias cruzadas (abstract, introducción, evidencia, capas, discusión, conclusión) para reflejar la jerarquía conceptual.
- **Claridad de la Capa 2**: Se resolvió la ambigüedad ontológica. La Capa 2 se caracteriza como capa de **estatus ontológico pleno pero primariamente relacional y transicional** («puente ontológico»). Introduce la propiedad irreducible de coherencia/alineación de escalas de persistencia $\tau_s$ (no localizable en módulos individuales), pero su rol principal es habilitar o bloquear la transición Capa 1 → Capa 3. Se añadió párrafo explícito tras su definición y se reforzó en la sección de Jerarquía.
- **Fortalecimiento de no-reductibilidad**: En «Jerarquía y no reductibilidad» se explicitó, para cada capa superior, **qué propiedad nueva e irreducible** introduce que no se deduce de las inferiores (Capa 2: alineación de $\tau_s$ como propiedad del acoplamiento; Capa 3: magnitud de cambio en la geometría relacional global medida por norma de Frobenius). Se enfatizó que la Capa 2 no es «mero estado» sino capa relacional con peso ontológico propio.
- **Otras mejoras**:
  - Sección 7.3 («Limitaciones y objeciones»): acortada significativamente; respuestas más directas, concisas y menos defensivas (1-2 frases por objeción, admisiones claras de lagunas).
  - Flujo evidencia → ontología: reforzado el puente argumental al final de la subsección «Implicaciones para la ontología» (Sección 3) y coherencia con Secciones 4-5.
  - Consistencia terminológica: unificado uso de «filtrado probabilístico», «permeabilidad entre capas», «transición entre capas» y «fragmentación» en todo el documento.
  - Abstract: reescrito para mayor economy y precisión (destaca filtrado probabilístico como noción central, aclara brevemente estatus de Capa 2, reduce redundancias).
  - Lenguaje: eliminados o suavizados residuos de formulaciones especulativas o poco operacionales.
- Actualización interna de CHANGELOG.md y README.md de la carpeta. Copia base: v0.1.1-mejoras-ontologicas/.

### Technical
- Compilación limpia (secuencia completa de 4 pases) dentro de manuscript/. 14 páginas verificadas, TOC y Referencias generados correctamente, sin errores LaTeX fatales ni Overfull críticos nuevos. Cualquier ajuste menor de longitud se realizó priorizando rigor conceptual.

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

## [0.1.1-mejoras-ontologicas] - 2026-06-15

### Added / Changed (editorial improvements, strictly inside this working copy)
- **Copia limpia**: esta carpeta `v0.1.1-mejoras-ontologicas/` se generó como copia exacta de `v0.1.0-frozen/` (cp -a). Todo el trabajo de edición, compilación y documentación se realizó exclusivamente aquí, respetando la política de versiones congeladas.
- **Definición estricta de «resistencia»** (reescritura completa de `sections/resistencia.tex` y referencias cruzadas): 
  > “Resistencia” se entiende como un **efecto estructural de filtrado probabilístico** emergente de la configuración de acoplamiento entre componentes. No se postula ninguna fuerza activa ni agente. Se describe una variación observable y medible en la probabilidad de que una intensificación local genere reorganización estructural según el nivel de antisincronización del sistema.
  - Eliminado todo lenguaje antropomórfico («protege», «resiste activamente», «protección de la diversidad local», «inercia ontológica» activa, etc.).
  - Los términos se mantienen entre comillas («resistencia ascendente», «resistencia descendente») como neologismos operacionales claramente definidos en términos de probabilidades de transición estructural.
  - Actualizaciones de consistencia en `introduccion.tex`, `evidencia_empirica.tex` (importantbox), `capas_presente.tex` (importantbox y diagrama), `discusion.tex` (analogía y preguntas), `conclusion.tex`, `main.tex` (abstract) y figura legacy `layers_diagram.tex`.
- **Precisión ontológica y terminológica** (`sections/capas_presente.tex`):
  - Definiciones de las tres capas reescritas con marcadores operacionales más rigurosos y explícitos (hiper-persistencia como desviación positiva de $\tau_s$ del propio módulo + RQA Config B; antisincronización como desviación estándar de $\tau_s$; norma de Frobenius como cambio en geometría relacional global).
  - Reforzada la explicación de no reductibilidad: cada capa superior "introduce propiedades relacionales o globales que no son deducibles a partir del análisis de los componentes de la capa inferior tomados aisladamente"; "ontológicamente irreducible"; "no reductibilidad ... en sentido ontológico débil".
  - Actualizado diagrama conceptual (fbox + \sloppy) y textos de apoyo.
- **Objeciones válidas** (`sections/discusion.tex`): nueva/ampliada subsección «Limitaciones y objeciones al marco propuesto» con respuestas breves, honestas y bien redactadas a las cinco objeciones:
  1. Riesgo de reificación de las «capas».
  2. Carácter metafórico del término «resistencia».
  3. Ausencia de mecanismo detallado de causación descendente.
  4. Posible circularidad entre métricas y ontología.
  5. Subdeterminación de la ontología por los datos.
  - Cada respuesta reconoce limitaciones actuales del marco sin defensividad excesiva.
- **Eliminación de frase específica**: removida completamente “Primera versión formal para publicación (junio 2026).” de `sections/conclusion.tex` (y por tanto del PDF). La frase no aparece en el PDF final.
- **Correcciones técnicas**:
  - Corregido title del preprint de dimensión fractal en ambas copias de `references.bib` (cambio de `\approx` crudo por `$\approx$` + normalización de mayúsculas y puntuación) para eliminar errores de compilación (Missing $ inserted, Command invalid in math mode, etc.) y mejorar renderizado.
  - Reorden de paquetes en `main.tex` (url/breakurl antes de hyperref) para resolver "Option clash for package url".
  - Mantenido \sloppy + breaklinks + secuencia completa de compilación. Sin Overfull \hbox críticos en el log final; solo underfulls normales.
  - Verificada generación correcta de Índice (TOC) y sección "Referencias" (con \section* + \addcontentsline).
- **Compilación final**: secuencia completa (rm auxiliares + pdflatex + bibtex + pdflatex + pdflatex) produce **14 páginas** (531 KB aprox.), sin la frase eliminada, con TOC poblado, Referencias completas y DOIs, y sin ?? en citas.
- **Documentación interna**: actualizados CHANGELOG.md y README.md de esta carpeta para reflejar que es versión de trabajo con mejoras ontológicas y terminológicas.

### Notes
- La versión oficial congelada sigue siendo `versions/v0.1.0-frozen/`. Esta `v0.1.1-mejoras-ontologicas/` es la copia de trabajo para refinamiento ontológico.
- El manuscrito es ahora más preciso, riguroso y académicamente defendible (definiciones operacionales estrictas, reconocimiento explícito de limitaciones, consistencia terminológica total).
- Próximos pasos (en nuevas subcarpetas si procede): revisión por pares interna, posible envío, asignación de DOI Zenodo sobre la versión estable elegida.

## [0.1.1] - 2026-06-15 (compile fixes inherited from base copy)
### Fixed
- Compilación: se reforzó que **TOC (Índice) y sección Referencias nunca se omitan**. La secuencia completa obligatoria ahora está documentada explícitamente en README (limpieza de aux + pdflatex + bibtex + pdflatex + pdflatex). 
- Se añadió `\sloppy` (con restauración) dentro del bloque de Referencias en `main.tex` para eliminar los overfull hbox en entradas largas con títulos + DOI/URL (incluyendo el caso del preprint de dimensión fractal).
- Verificación post-compilación: `main.toc` registra todas las secciones + "Referencias"; el PDF muestra "Índice" poblado; todas las citas resueltas (sin ??); la lista de Referencias aparece completa al final con entradas reales y DOIs.
- Se actualizó el proceso mental de compilación: **nunca compilar con pases incompletos**. Los archivos `main.pdf`, `main.toc` y `main.bbl` se regeneran siempre con la secuencia de 4 pases después de rm de auxiliares.