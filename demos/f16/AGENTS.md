# F-16 R6: local agent

Read the root AGENTS.md, this README, and the shared Notebook API skill.

- The saved recipe contains the complete native construction graph. It does not depend on a sibling workspace.
- Use `uv run --locked python scripts/build.py f16` from the repository root to replay and check the graph.
- Use `uv run --locked python scripts/stage.py f16` to prepare an import for an empty nTop notebook.
- Edit native controls in a working copy. Save new work under output/ or root .local/.
- Keep numerical comparison results tied to their recorded revision. Geometry edits require fresh checks.
- The reports preserve incomplete validation and failed targets. Do not claim production or flight qualification.
- Reference photos and photo composites are excluded from this public repository.
- Collapse authored blocks and sections after the final save, in a separate deliverable.
