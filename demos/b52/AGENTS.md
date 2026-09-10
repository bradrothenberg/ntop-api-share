# B52 fuselage: agent instructions

Read the root AGENTS.md, the shared Notebook API skill, and this demo's README.md.
The R7 fair nose blend and accepted cockpit loft. Geometry is derived from a GPL-2.0 artist model, not production aircraft data.

- scripts/ contains the standalone source. inputs/ contains the minimal rebuild data.
- models/ contains retained native snapshots. Use output/ and root .local/ for new work.
- reports/index.html contains the public report. LEARNINGS.md contains the edited project record.
- Build from the repository root with `uv run --locked python scripts/build.py b52`.
- Use `uv run --locked python scripts/stage.py b52` for a new empty nTop notebook.
- Validate units and graph dependencies before evaluating large geometry.
- Read measured scalar values and inspect the final geometry after native execution.
- Keep geometry fit, selected dimensions, numerical checks, and engineering qualification distinct.
- Finish with collapsed authored blocks and sections in a separate saved deliverable.
