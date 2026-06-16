# Changelog

All notable changes to this repository and the manuscript will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [0.1.1] - 2026-06-15
### Fixed
- Compilación: se reforzó que **TOC (Índice) y sección Referencias nunca se omitan**. La secuencia completa obligatoria ahora está documentada explícitamente en README (limpieza de aux + pdflatex + bibtex + pdflatex + pdflatex). 
- Se añadió `\sloppy` (con restauración) dentro del bloque de Referencias en `main.tex` para eliminar los overfull hbox en entradas largas con títulos + DOI/URL (incluyendo el caso del preprint de dimensión fractal).
- Verificación post-compilación: `main.toc` registra todas las secciones + "Referencias" (pág. 12); el PDF muestra "Índice" poblado en pág. 2; todas las citas resueltas como `[Padilla-Villanueva, 2026a,e]` etc. (sin ??); la lista de Referencias aparece completa al final con entradas reales y DOIs.
- Se actualizó el proceso mental de compilación: **nunca compilar con pases incompletos**. Los archivos `main.pdf`, `main.toc` y `main.bbl` se regeneran siempre con la secuencia de 4 pases después de rm de auxiliares.