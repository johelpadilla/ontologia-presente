# The Joint Episode as an Ontological-Temporal Unit

**Title (working):**  
The Joint Episode as an Ontological-Temporal Unit: Mathematical Characterization, Structural Properties, and Transitions in Complex Systems

This repository contains the dedicated development of the **Joint Episode** as a central technical and ontological concept.

## Scope
- Primarily **technical-mathematical** paper at the level of prior Systemic Tau (RECD) preprints.
- Rigorous formal definitions, metrics, and properties.
- Well-integrated ontological section (Section 7) grounded in the three-layer framework (Layer 1 intensification, Layer 2 permeability/coherence, Layer 3 reorganization).
- Synthetic validation (coupled logistic map, Lorenz attractor) in Section 6. Empirical real-world (dengue) deferred.
- Literature engagement on recurrence, structural transitions, and temporal concepts in nonlinear dynamics.

## Project Organization
- `manuscript/` — LaTeX source (main.tex + sections/)
- `notes/` — development notes, derivations, literature notes
- `references/` — master .bib and working references
- `supplementary/` — technical reports, code, additional figures, protocols
- `versions/` — clean snapshots (cp -a) of the full project at major milestones
- `CHANGELOG.md` — all changes

## Version Control Policy (strict)
- Never edit "base" directories directly for permanent work.
- For significant advances, create fresh `versions/vX.Y-description/` via `cp -a`.
- Update only `CHANGELOG.md` at the root of `joint-episode-paper/`.
- **Always recompile LaTeX** after any meaningful content change (full clean 4-pass: remove aux/bbl/blg/toc + pdflatex + bibtex + 2×pdflatex). 
- **Compiled PDF rule**: After every significant advance (new section content, important definitions, structural changes, etc.), a freshly compiled PDF of the current state of the manuscript will **always** be produced and placed in `manuscript/` (as `main.pdf`) and also copied to the project root with a descriptive name (e.g., `Joint-Episode-Paper-Draft-vX.Y.pdf`). The PDF is part of the deliverable for that step.
- This paper is a focused outgrowth of the RECD + Ontología del Presente program.

## Current Status
See `CHANGELOG.md` for the latest entry.

**PDF rule in force**: Every significant deliverable includes a freshly compiled PDF.

Initial iteration (2026-06-18): structure creation + refined outline + abstract draft + key definitions list + first compiled PDF.

**Latest (2026-06-18):** Added complete modular `code/` for J vs J_{0.7} empirical comparison on coupled logistic synthetic data. First experiment executed (50 realizations), results + docs in place. See CHANGELOG.md and `code/README.md`.

## Related Prior Work
- RECD / Tau Sistémico framework (see parent `ontologia-presente/` and `preprints/recd_dengue_joint_episodes_2026/`)
- Three-layer ontological framework
- Joint Score, Confidence Score, A(k) antisynchrony, Systemic Tau τ_s, M (critical mass)

Author: Dr. Johel Padilla Villaunueva (ontologia-presente research program)
