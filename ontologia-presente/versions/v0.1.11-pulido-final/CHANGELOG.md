# Changelog

All notable changes to this repository and the manuscript will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.11-pulido-final] - 2026-06-15

### Polished (última y muy corta ronda de pulido: fluidez ligera en introducción, implicaciones y jerarquía; refinamiento final del espaciado en Figura 4; copia limpia de v0.1.10)
- **Pulido ligero de fluidez en Introducción**: Ajustes quirúrgicos mínimos en el segundo y tercer párrafo (`introduccion.tex`): simplificación de conectores ("convergen en que", "Así") y adición de coma para mejor ritmo en la descripción de la Capa 2, sin alterar ideas ni tono.
- **Pulido ligero de fluidez en "Implicaciones para la ontología"** (final de Evidencia empírica): Reemplazo quirúrgico de una repetición ("convergen en esa motivación" → "sustentan esa motivación") para mejorar el cierre del puente empírico → tres capas (`evidencia_empirica.tex`).
- **Pulido ligero de fluidez en "Jerarquía y no reductibilidad"**: Remoción de "aquí" innecesario y aligeramiento de la frase inicial de la explicación de no reductibilidad (`capas_presente.tex`), buscando mayor naturalidad sin modificar el contenido.
- **Refinamiento final visual de la Figura 4**: Mayor espaciado vertical entre cajas (gaps de centros ~1.8 cm, posiciones y ajustadas), mayor aire lateral para flechas y etiquetas (xshift y ++() ampliados), más margen interno en cajas (inner sep=6pt, dimensiones ligeramente mayores), side annotation más alejada y con espaciado interno incrementado. TikZ actualizado idénticamente en `capas_presente.tex` y `layers_diagram.tex`. Diagrama más aireado, equilibrado y elegante; contenido y estructura intactos.
- Restricciones estrictas respetadas: solo cambios de estilo/ritmo indicados y espaciado visual en Figura 4; sin modificaciones conceptuales, sin tocar otras secciones ni elementos.
- Compilación final limpia (secuencia completa de 4 pases) dentro de `manuscript/`. 14 páginas, TOC y Referencias presentes. CHANGELOG actualizado.

## [0.1.10-pulido-final] - 2026-06-15

### Polished (última ronda de pulido: fluidez quirúrgica en secciones específicas y refinamiento visual de la Figura 4; copia limpia de v0.1.9)
- **Mejora de fluidez en Sección 6.1**: Reescritura ligera y quirúrgica de oraciones densas en «Memoria como retención activa» (`memoria_tiempo.tex`) para lograr mejor ritmo y fluidez entre las ideas de trapping e hiper-persistencia, sin alterar el contenido conceptual ni las definiciones.
- **Mejora de fluidez en Sección 7.1**: Pulido del párrafo que explica las limitaciones de la analogía del huracán (`discusion.tex`) para que sea más directo, natural y elegante, manteniendo toda la precisión original.
- **Mejora de la introducción en Sección 7.2**: Se añadió una transición ligera y elegante al inicio de «Preguntas abiertas» (`discusion.tex`) que permite que la sección fluya de forma más natural desde la subsección anterior, sin introducir contenido conceptual nuevo.
- **Refinamiento visual de la Figura 4**: Rediseño del diagrama TikZ (actualizado de forma idéntica en `capas_presente.tex` y `figures/layers_diagram.tex`). Se aumentó sustancialmente el espaciado vertical entre las tres capas (separación de centros ~1.7 cm), se amplió el «aire» alrededor de las cajas (mayor inner sep, min height/width y text width), se incrementó el alcance horizontal de las flechas para mayor separación lateral, se alejó y ajustó la anotación lateral de antisincronización, y se afinaron los yshifts y alineaciones de etiquetas. El resultado es un diagrama notablemente más espaciado, equilibrado, limpio y profesional, preservando exactamente toda la información, jerarquía, flechas y etiquetas previas.
- Se respetaron estrictamente las restricciones: cambios exclusivamente de estilo/fluidez y espaciado visual; ninguna modificación conceptual, ninguna otra sección tocada, sin alterar definiciones, resultados, terminología ni referencias.
- Compilación final limpia (secuencia completa de 4 pases: rm auxiliares + pdflatex + bibtex + pdflatex + pdflatex) dentro de `manuscript/`. 14 páginas, TOC («Índice») y sección «Referencias» presentes y verificados.
- CHANGELOG.md actualizado dentro de la carpeta de versión.

## [0.1.9-pulido-final] - 2026-06-15

### Polished (última ronda de pulido: fluidez ligera, metalenguaje residual y mejora visual de la Figura 4; copia limpia de v0.1.8)
- **Pulido de fluidez y metalenguaje residual**: Revisión ligera y precisa en Introducción, Memoria activa y Discusión (con ajustes quirúrgicos mínimos en otras secciones). Se eliminaron residuos como participios autorreferenciales y se mejoró el ritmo de oraciones y transiciones entre párrafos para lograr un flujo más natural y elegante, sin alterar el contenido conceptual ni el tono académico maduro.
- **Mejora significativa de la Figura 4**: Se rediseñó completamente el diagrama conceptual de las tres capas (en `capas_presente.tex` y el archivo fuente `layers_diagram.tex`) utilizando un TikZ limpio, jerárquico y profesional. El nuevo esquema muestra con claridad la jerarquía vertical (Capa 3 arriba → Capa 2 → Capa 1 abajo), las flechas de integración (derecha, sólidas) y las de filtrado probabilístico bidireccional (izquierda, punteadas), junto con la anotación lateral del rol de la antisincronización. El pie de figura se reescribió para ser conciso, elegante y preciso, enfatizando la jerarquía y el filtrado sin repeticiones.
- Se respetaron estrictamente todas las restricciones: sin cambios conceptuales, sin modificación de la estructura ni de la Sección 7, y sin adición ni eliminación de autores o referencias.
- Compilación final limpia (secuencia completa de 4 pases) dentro de `manuscript/`. 14 páginas. CHANGELOG.md actualizado.

## [0.1.8-pulido-fluidez] - 2026-06-15

### Polished (última ronda focalizada de estilo: eliminación de metalenguaje residual y mejora de fluidez; copia limpia de v0.1.7)
- **Eliminación de metalenguaje residual**: Se suprimieron las últimas expresiones de autorreferencialidad o anuncio de estructura que persistían, entre ellas «Quedan abiertas varias líneas de investigación:» (discusión), «se articula como» y «se caracteriza ontológicamente como» (introducción y abstract), participios como «articulada en torno al marco» (conclusión) y «Se describe, de manera estrictamente operacional» (resistencia). Se sustituyeron por formulaciones directas y elegantes.
- **Mejora de fluidez**: Ajustes quirúrgicos en transiciones y ritmo de oraciones, especialmente en Introducción (mejor enlace entre la observación empírica y la caracterización de las capas), Discusión (paralelismo y ritmo en el párrafo sobre limitaciones de la analogía del huracán) y Memoria activa (división de oraciones largas y eliminación de giros interpretativos autorreferenciales). Cambios análogos, aunque mínimos, en evidencia empírica (evitación de paréntesis excesivamente largos) y capas (sustitución de «se formulan» por «se establecen»).
- Se prestó atención prioritaria a Introducción, Memoria activa y Discusión, sin reescribir secciones completas ni alterar significado, estructura conceptual, referencias ni la sección de limitaciones (ya ausente).
- Se respetaron estrictamente todas las restricciones: sin cambios conceptuales, sin adición o eliminación de autores o referencias, y sin modificaciones en la Sección 7.3.
- Compilación final limpia (4 pases completos) dentro de manuscript/. CHANGELOG.md actualizado.

## [0.1.7-pulido-final] - 2026-06-15

### Polished (versión final de pulido: eliminación sistemática de metalenguaje, reescritura elegante de la Sección 7.3, incorporación de referentes clásicos y actualización de referencias; copia limpia de v0.1.6)
- **Eliminación sistemática de metafrases y metalenguaje**: Se revisó exhaustivamente todo el documento. Se suprimieron expresiones como «El presente trabajo articula…», «La contribución principal consiste en…», «La Sección 2 expone…», «Las Secciones 4 y 5 desarrollan…», «El marco deja abiertas…», «La ontología propuesta se sustenta en…», «Las secciones siguientes articulan…» y formulaciones análogas de autorreferencialidad o roadmap. Las transiciones se reescribieron en un tono académico maduro y fluido, sin que el texto resultara seco o telegramático.
- **Reescritura de la Sección 7.3**: Se reescribió por completo la subsección «Limitaciones y objeciones al marco propuesto» (discusion.tex) para que fuera corta y elegante (aprox. ½ página). Se eliminó cualquier listado explícito de objeciones y todo tono defensivo. El reconocimiento de las limitaciones se integra de forma natural y serena: dependencia de umbrales operativos, carácter estructural del filtrado probabilístico sin mecanismos causales detallados, solapamiento entre métricas y afirmaciones ontológicas, alcance de los datos y valor dependiente de predicciones y diálogo con tradiciones filosóficas.
- **Incorporación de autores clásicos**: Se enriqueció la Introducción con referencias breves pero significativas a Ilya Prigogine (estructuras disipativas y flecha temporal en sistemas alejados del equilibrio), Edward Lorenz (atractores deterministas y sensibilidad a condiciones iniciales) y Mitchell Feigenbaum (universalidad en la transición al caos). Las menciones se integran de manera contextual y natural en el desarrollo argumentativo. En el abstract solo se mantuvo la caracterización central sin sobrecarga adicional.
- **Actualización de referencias**: Se incorporaron al archivo `references.bib` (dentro de manuscript/) las entradas canónicas y ampliamente reconocidas de Prigogine (1980), Prigogine & Stengers (1984), Lorenz (1963) y Feigenbaum (1978), con citas correspondientes en el texto de la Introducción. No se añadieron referencias no verificadas.
- Se respetaron estrictamente las restricciones: sin cambios conceptuales en la ontología (definiciones de capas, no-reductibilidad, estatus de la Capa 2 como puente relacional/transicional, memoria activa, filtrado probabilístico bidireccional como concepto primario y «resistencia» como etiqueta heurística secundaria) y mantenimiento de la consistencia terminológica.
- Compilación final limpia (secuencia completa de 4 pases) dentro de manuscript/. 14 páginas. TOC y Referencias presentes. CHANGELOG.md actualizado.

## [0.1.6-pulido-elegante] - 2026-06-15

### Polished (refinamiento estilístico de alto nivel: reescritura elegante de la Sección 7.3 y eliminación de metalenguaje; copia limpia de v0.1.5)
- **Reescritura completa de la Sección 7.3**: La subsección «Limitaciones y objeciones al marco propuesto» (discusion.tex) se reescribió de forma integral para ser significativamente más corta (aprox. ½–¾ de página). Se eliminó toda estructura de listado explícito de objeciones («Riesgo de reificación…», «Carácter heurístico…», etc.). El reconocimiento de las limitaciones del marco se integra ahora de manera natural y fluida en prosa académica madura, directa y no defensiva. El texto confía en que las definiciones operacionales, las distinciones ontológicas y las caracterizaciones previas del cuerpo del artículo responden implícitamente a la mayoría de las objeciones legítimas. El tono es elegante, sin rastro de justificación ni enumeración defensiva.
- **Eliminación de metafrases y metalenguaje**: Se revisó todo el documento, con atención especial a las secciones de discusión, conclusión, introducción, abstract, evidencia empírica y capas. Se eliminaron expresiones autorreferenciales y de comentario sobre el propio texto tales como «Este artículo ha presentado…», «La ontología del presente que se ha esbozado…», «El marco aquí propuesto…», «Las definiciones y relaciones aquí establecidas…», «no se interpretan aquí como…», «La evidencia de la Sección 3…», «La robustez al ruido documentada en la Sección 3…», «El artículo se estructura de la siguiente manera…», «El presente artículo desarrolla esta observación…», «Se sostiene que…» y formulaciones análogas. Las transiciones y roadmaps se reescribieron en voz más directa y activa, sin autorreferencialidad innecesaria. El resultado es un texto limpio, elegante y maduro.
- Se mantuvo estrictamente la consistencia terminológica (primacía del filtrado probabilístico bidireccional; «resistencia» como etiqueta heurística secundaria y ocasional) y no se introdujeron cambios conceptuales en la ontología (capas, no-reductibilidad, estatus de la Capa 2, memoria activa, etc.). No se acortaron otras secciones.
- Compilación final limpia (secuencia completa de 4 pases) dentro de manuscript/. CHANGELOG.md actualizado.

## [0.1.5-pulido-fino] - 2026-06-15

### Polished (última ronda de pulido fino: concisión, uniformidad terminológica y fluidez argumentativa; copia limpia de v0.1.4)
- **Objetivo 1 – Mayor concisión en la Sección 7.3**: Se redujo aún más la subsección «Limitaciones y objeciones al marco propuesto» (discusion.tex). Se eliminaron las últimas redundancias y frases ligeramente elaboradas; cada objeción se expresa ahora con máxima economía y precisión (oraciones más directas, sin repeticiones de limitaciones). Se mantuvo el tono claro, honesto y profesional, sin rastro de lenguaje justificativo. Todas las cinco objeciones principales se conservan intactas.
- **Objetivo 2 – Uniformidad en el tratamiento de «resistencia»**: Se revisaron exhaustivamente todos los usos de «resistencia ascendente» y «resistencia descendente» (abstract en main.tex, introducción, cajas «Resultado clave» de evidencia_empirica.tex y capas_presente.tex, Sección 5/resistencia.tex completa, conclusión, discusion 7.3). Se uniformizaron las expresiones de cautela a un patrón consistente: siempre subordinado explícitamente al **filtrado probabilístico bidireccional** como concepto primario; fórmulas como «con valor heurístico secundario», «solo ocasionalmente como etiquetas heurísticas secundarias», «denominado ocasionalmente» o «se conocen ocasionalmente» aplicadas de forma uniforme. El lector percibe consistentemente que «resistencia» es un término secundario y heurístico, nunca central. Atención especial a los recuadros y a la Sección 5.
- **Objetivo 3 – Mejorar fluidez en la Sección 5**: Se reescribieron los párrafos de «Dinámica de filtrado probabilístico entre capas» (resistencia.tex) para que la caracterización del filtrado ascendente y descendente fluya directamente de la evidencia empírica de la Sección 3. Se añadieron puentes explícitos y económicos que anclan las explicaciones en hallazgos concretos (reducción de antisincronización previa a picos con $p=0.0229$ y valores más bajos en pre-100 pasos para el ascendente; descenso de picos pero invariancia de Frobenius bajo ruido 0--15 % para el descendente). Se eliminó sensación de repetición o desconexión; las subsecciones ahora se leen como interpretación natural y motivada de los resultados empíricos (antisincronización como regulador, robustez estructural).
- Se respetaron estrictamente las restricciones: sin cambios conceptuales en la ontología (capas, no-reductibilidad, estatus de Capa 2 como puente relacional/transicional, memoria activa, etc.), sin reducción de extensión del documento, mantenimiento de la precisión terminológica y del estatus estrictamente secundario/heursítico de «resistencia».
- Compilación final limpia (4 pases completos) dentro de manuscript/: 14 páginas verificadas, TOC y Referencias presentes, sin errores ni Overfull críticos. CHANGELOG.md actualizado.

## [0.1.4-pulido-final] - 2026-06-15

### Polished (ronda final de madurez redaccional y fluidez, copia limpia de v0.1.3)
- **Concisión de la Sección 7.3**: La subsección «Limitaciones y objeciones al marco propuesto» se reescribió para ser significativamente más corta y directa. Se eliminaron repeticiones y expresiones defensivas («se reconoce honestamente», «de forma directa», etc.). Cada objeción se expresa ahora de manera económica y precisa, manteniendo las cinco objeciones válidas pero con un tono honesto, riguroso y sin justificación excesiva.
- **Reducción adicional de la prominencia de «resistencia»**: Se redujo aún más el uso y la visibilidad de «resistencia ascendente» y «resistencia descendente». El concepto de **filtrado probabilístico bidireccional** (y sus variantes ascendente/descendente) es ahora el término principal en todo el documento. Los términos entre comillas aparecen solo de forma secundaria y ocasional como etiquetas heurísticas (en paréntesis, al final de cajas importantes, o en cláusulas subordinadas). Se revisaron y ajustaron especialmente el abstract, la Sección 5 (Dinámica de filtrado probabilístico), las cajas importantes de evidencia y capas, las preguntas de la discusión, introducción y conclusión.
- **Mejora de fluidez entre evidencia e interpretación**: Se reforzó la transición al final de la Sección 3 («Implicaciones para la ontología») para que los resultados empíricos concretos (picos en contextos de baja antisincronización, adelanto significativo, robustez al ruido) se vinculen de forma explícita y natural con la partición en tres capas y la caracterización del filtrado probabilístico como regulador de la probabilidad de transición. Se añadió una oración puente al inicio de la Sección 4 («Las tres capas del presente») que retoma directamente esos patrones empíricos y explica por qué motivan la ontología de capas. El paso de la Sección 3 a las 4 y 5 resulta ahora más coherente y menos abrupto.
- Se respetaron estrictamente las restricciones: no se redujo la extensión del documento, no se introdujeron cambios conceptuales en la ontología (definiciones de capas, no-reductibilidad, memoria activa, etc.), y se mantuvo el estatus secundario y heurístico del término «resistencia».
- Compilación final limpia de 14 páginas con TOC y Referencias completos. CHANGELOG.md actualizado.

## [0.1.3-correcciones-tecnicas] - 2026-06-15

### Fixed / Polished (enfoque técnico y maquetación, copia limpia de v0.1.2)
- **Corrección prioritaria de texto truncado**: Se localizó y corrigió el problema en la subsección 3.3 «Robustez al ruido». El párrafo se reescribió en oraciones más cortas y fluidas que mencionan explícitamente todos los niveles probados (0 %, 5 %, 10 % y 15 % de la desviación estándar de cada componente), los resultados clave (descenso de 121 a 100 picos, invariancia de cambios por Frobenius) y la conclusión sobre estabilidad estructural. El cambio (junto con la compilación limpia) asegura que el texto aparezca completo y sin cortes en el PDF final.
- **Revisión de maquetación y overflow**: Se verificó todo el documento (párrafos en evidencia_empirica, tcolorbox en capas_presente, figuras, bloque de Referencias y secciones con contenido técnico largo). No se encontraron Overfull hbox críticos que afecten legibilidad (log limpio). El uso de oraciones más cortas en el párrafo problemático eliminó el riesgo de truncamiento por líneas demasiado largas o ajustes deficientes.
- **Pulido de fluidez y consistencia**: Se mejoró ligeramente la transición al final de la subsección «Implicaciones para la ontología» (Secc. 3) para conectar de forma más fluida y económica los resultados numéricos con las secciones ontológicas (4 y 5). Pulido general de redacción en evidencia y capas para mayor claridad y economía de lenguaje (sin modificar el contenido conceptual ni la estructura ontológica establecida en v0.1.2).
- Compilación final: secuencia completa de 4 pases dentro de manuscript/ produce exactamente **14 páginas**, con TOC y Referencias correctos, sin texto truncado visible y maquetación profesional.
- CHANGELOG.md y (si aplica) README interno actualizados.

### Notes
- No se realizaron cambios conceptuales mayores. La estructura ontológica, definiciones y terminología de v0.1.2 se mantienen estables.
- Esta versión resuelve problemas técnicos pendientes y deja el documento en estado pulido para revisión interna o envío.

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