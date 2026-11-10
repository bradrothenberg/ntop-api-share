# Clean delivery without changing the accepted shape

Use this after the user selects a current result or requests removal of obsolete
versions. Model cleanup and folder deletion are separate operations.

## Prune the notebook by dependencies

Identify the saved current output and record its hash. Walk its ordered input
references recursively. Keep every reached node, required literal, imported
custom block, nested custom dependency, and external asset. Visibility is not a
dependency test. A hidden loft may still define the final shape.

Remove unreachable alternatives and stale measurement branches. Rebuild the
root order, section boundaries, visibility entries, and collapsed-state paths.
Keep one visible final body and only the construction used by it. Never flatten
the accepted result into a mesh merely to reduce the notebook tree.

For a verified saved-container editor, prove a byte-exact read/write round trip
before editing. Do not assume a fixed file-header length. Preserve unknown
metadata and ordered input property chains. Use the current view-state/API
workflow available in the target environment; reject unknown container layouts.

Compare every retained geometry node and literal with the selected source.
Ignore only deliberate presentation changes such as names and nesting flags.
Do not remove a variable alias by rewiring unless the graph semantics are known.
Then load the full saved notebook, render it natively, and compare field samples
at the inlet, root skins, wing edges, tail, and protected regions.

Exact dependency equality is stronger than sampled equality alone. A reduced
measurement notebook does not prove the full delivery notebook loads correctly.
Record both results and tie each receipt to the model hash.

## Remove obsolete folders only when requested

Resolve an explicit list of old revision directories under the intended project.
Do not recursively delete by a broad name pattern across the user's computer.
Reject junctions or symlinks that lead outside the allowed scope. Review any
unrelated files mixed into an old revision directory before removing it.

First consolidate the current model, current construction source, small useful
verification records, and the tools needed to reproduce them. Rewrite imports,
hard-coded paths, source snapshots, and documentation that point into retired
folders. Check the retained package independently of those folders.

If source reconstruction uses a saved graph bundle, call it that. Reserializing
an accepted graph is not an independent geometry reconstruction. Verify the
regenerated notebook hash, native load, and relevant sampled fields.

Respect explicit cleanup authorization; do not invent a second approval step.
Keep a path/count/size/hash manifest of what was removed. Do not keep a hidden
copy of every obsolete model while claiming that the old versions were removed.
Preserve unrelated projects, the user's external reference model, and annotation
records. Do not remove a shared viewer cache or other task's source automatically.

Preserve annotations before closing an obsolete owned renderer. Do not terminate
a user desktop session to release a folder lock. If all obsolete files are gone
but the desktop holds an empty working directory, report that remaining folder.

Finish by searching the retained project for stale active dependencies and old
model duplicates. Historical evidence can name a retired file, but executable
tools and current instructions must use retained paths. Report any remaining
design question separately from cleanup completion.
