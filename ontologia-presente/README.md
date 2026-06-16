# Hacia una ontología del presente en sistemas complejos

**RECD, persistencia intensificada y la dinámica de la fragmentación**

**Repositorio de versiones controladas del manuscrito**

---

## ⚠️ POLÍTICA DE VERSIONES (congelada desde junio 2026)

**De ahora en adelante esta es nuestra versión base / congelada.**

- La **versión oficial base / congelada e inmutable** está en:
  ```
  versions/v0.1.12/
  ```
  Contiene el manuscrito completo (fuentes + `main.pdf` final de 14 páginas con Índice y Referencias), figuras (incluyendo la Figura 4 en su estado preferido y equilibrado), bibliografía, suplemento y documentación de esta versión.

- **Todo el trabajo futuro** (cambios de redacción, nuevas figuras, revisiones, feedback de revista, etc.) **se realizará exclusivamente** copiando esta versión base a subcarpetas nuevas dentro de `versions/`.

  Ejemplo:
  - `cp -a versions/v0.1.12/ versions/v0.1.13-mi-revision/`

- **Nunca se editan** los archivos directamente en la raíz ni dentro de `versions/v0.1.12/`.

- La raíz de `ontologia-presente/` funciona solo como **índice y documentación de versiones** + archivos de metadatos (CHANGELOG global, CITATION.cff, este README).

Ver también: `versions/README.md` (catálogo actualizado de versiones y procedimiento).

---

## Versión base actual

**v0.1.12** (15 junio 2026) — Nueva versión base oficial del manuscrito.

- Ubicación: `versions/v0.1.12/`
- Estado: 14 páginas, compilación limpia con TOC ("Índice") y sección "Referencias" completos. Figura 4 (diagrama de las tres capas) en el estado visual preferido y perfectamente ajustado a márgenes. Todo el pulido de fluidez ligero aplicado. Lista como base para revisión, citación y preparación de preprint/revista.
- Características principales: marco ontológico de tres capas con filtrado probabilístico bidireccional como concepto central, antisincronización como regulador, definiciones rigurosas, evidencia empírica integrada, terminología precisa en español.

Para compilar o trabajar con esta versión base, entra en `versions/v0.1.12/manuscript/` y ejecuta la secuencia completa de 4 pases (ver README dentro de la versión). 

La raíz (`ontologia-presente/manuscript/`, `references/`, `supplementary/`) ahora contiene una **copia sincronizada** de los fuentes y el PDF de la versión base v0.1.12 para vista rápida y compilación de conveniencia. Esta copia en la raíz **no es la versión canónica** ni debe editarse directamente.

**Nunca editar directamente la base.** Para cualquier cambio futuro: copiar primero desde `versions/v0.1.12/` a una nueva subcarpeta en versions/.

---

## Estructura general del repositorio (nueva)

```
ontologia-presente/
├── versions/
│   ├── v0.1.0-frozen/          ← VERSIÓN CONGELADA (inmutable)
│   │   ├── manuscript/
│   │   ├── references/
│   │   ├── supplementary/
│   │   ├── README.md (marcado como frozen)
│   │   └── ...
│   └── vX.Y.Z-xxx/             ← Futuras versiones (solo aquí se edita)
├── README.md                   ← Este archivo (índice + política)
├── CHANGELOG.md                ← Historial global de versiones
├── CITATION.cff                ← Metadatos de la versión base
├── .gitignore
└── versions/README.md          ← Guía de cómo crear y trabajar con nuevas versiones
```

---

## Cómo compilar una versión

**Importante**: Todas las compilaciones se hacen **dentro de la carpeta de la versión específica**.

Ejemplo para la versión congelada:

```bash
cd versions/v0.1.0-frozen/manuscript

# Limpieza obligatoria
rm -f main.aux main.log main.out main.toc main.bbl main.blg

pdflatex main
bibtex main
pdflatex main
pdflatex main
```

El PDF aparecerá como `main.pdf` dentro de esa misma carpeta.

Ver el README dentro de cada versión para detalles específicos de esa revisión. Las reglas de "nunca olvides TOC y Referencias" (secuencia completa de 4 pases) aplican a **todas** las versiones.

**Notas de compilación generales** (válidas para todas las versiones):
- Clase `article` + paquetes estándar.
- `\sloppy` aplicado en el bloque de Referencias.
- Secuencia completa de pdflatex + bibtex + pdflatex + pdflatex **siempre** requerida para que aparezcan el Índice y la sección Referencias correctamente.

---

## Estado de las versiones

- **Versión congelada actual (oficial, inmutable)**: `versions/v0.1.0-frozen/` (v0.1.0 — junio 2026)
  - 13 páginas
  - Índice completo + sección "Referencias" con DOIs
  - Evidencia integrada de experimentos previos (ruido, antisincronización)
  - Lista para revisión interna y posible envío / Zenodo

- **Versión de trabajo actual**: `versions/v0.1.1-mejoras-ontologicas/` (v0.1.1-mejoras-ontologicas — junio 2026)
  - 14 páginas (compilado limpio, 0 errores LaTeX críticos, 0 Overfull hbox)
  - Mejoras ontológicas y terminológicas: definición estricta de «resistencia» (efecto estructural de filtrado probabilístico emergente del acoplamiento; sin fuerza activa ni lenguaje antropomórfico); definiciones de las tres capas más rigurosas y explícitamente no reductibles; subsección «Limitaciones y objeciones al marco propuesto» con respuestas honestas a las 5 objeciones listadas; eliminación completa de la frase “Primera versión formal para publicación (junio 2026).”; correcciones técnicas y consistencia total.
  - Ver `versions/v0.1.1-mejoras-ontologicas/README.md` y su CHANGELOG.md para detalles y estado.
  - **No usar para citación oficial**; es copia de trabajo. Cambios adicionales requieren nueva subcarpeta.

- Las versiones futuras se listarán aquí y en `versions/README.md` a medida que se creen (siempre partiendo de copia de la congelada).

**Contenido base de la versión congelada**:
- Definiciones rigurosas de RECD, τ_s, hiper-persistencia, trapping (RQA Config B), I, antisincronización como regulador de fragmentación.
- Tres capas del presente + dinámica de «resistencia ascendente» / «resistencia descendente».
- Memoria activa y tiempo extramental como transiciones entre capas de persistencia.
- Referencias completas con DOIs (Zenodo + Preprints.org).

---

## Cómo citar este trabajo (placeholder)

**Usa siempre la versión congelada como base:**

Padilla-Villanueva, J. (2026). *Hacia una ontología del presente en sistemas complejos: RECD, persistencia intensificada y la dinámica de la fragmentación* (v0.1.0-frozen).  
Ubicación: `versions/v0.1.0-frozen/` del repositorio.  
Zenodo (cuando se asigne): https://doi.org/10.5281/zenodo.XXXXXXX

**BibTeX / BibLaTeX entry (placeholder):**

```bibtex
@article{padilla_ontologia_presente_2026,
  author  = {Padilla-Villanueva, Johel},
  title   = {Hacia una ontología del presente en sistemas complejos: RECD, persistencia intensificada y la dinámica de la fragmentación},
  year    = {2026},
  publisher = {Zenodo},
  doi     = {10.5281/zenodo.XXXXXXX},
  url     = {https://doi.org/10.5281/zenodo.XXXXXXX},
  version = {0.1.0-frozen}
}
```

Reemplaza `XXXXXXX` por el identificador real una vez publicado en Zenodo. Para versiones posteriores, ajusta `version` y el subdirectorio.

---

## Conexión con Zenodo (GitHub Releases)

Para la versión congelada (y futuras versiones estables):

1. Asegúrate de que el repositorio esté en GitHub.
2. Crea un *release* en GitHub:
   - Tag: `v0.1.0-frozen` (o el tag de la versión que estés liberando).
   - Sube como assets:
     - El PDF desde `versions/v0.1.0-frozen/manuscript/main.pdf`
     - Un ZIP de la carpeta de la versión (`v0.1.0-frozen/`) o del repositorio completo.
3. Conecta el repositorio a Zenodo (GitHub app) y activa el repositorio.
4. Zenodo creará el registro con DOI en el siguiente push del tag.
5. Actualiza:
   - `CITATION.cff` (en la raíz y dentro de la versión si es necesario)
   - El README de la versión y el de la raíz
   - La sección de citación

Las versiones futuras seguirán el mismo flujo pero desde su propia subcarpeta bajo `versions/`.

---

## Licencia y derechos

El contenido conceptual y textual está bajo licencia **CC-BY-4.0** (ver `CITATION.cff`). El código de soporte (si se añade en `supplementary/`) se publicará bajo la misma licencia o MIT según decisión del autor.

---

## Contacto / Contribuciones

Las contribuciones y revisiones se gestionan creando **nuevas versiones** en subcarpetas (ver `versions/README.md`).

Este repositorio ahora prioriza el control estricto de versiones para publicación académica.

**Autor**: Johel Padilla-Villanueva  
Universidad de Puerto Rico, Recinto de Ciencias Médicas

---

*Versión congelada declarada: junio 2026. Política de subcarpetas de versiones activa a partir de esta fecha.*
