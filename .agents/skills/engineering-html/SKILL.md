---
name: engineering-html
description: Build self-contained HTML engineering reports for these nTop demonstrations with readable evidence, native geometry figures, accessible controls, and explicit validation limits.
---

# Engineering HTML reports

Use templates/report.html and templates/report.css as the local starting point.
The included demo reports show native geometry, assembly inspections, and before/after comparisons.

Lead with the model and its purpose. Use a restrained paper-and-ink palette, one orange accent,
system sans-serif text, monospace metadata, numbered evidence sections, and clear table rules.
Keep the page readable at desktop and phone widths. Make controls keyboard-operable and label them.
Support light and dark themes without remote font or script dependencies.

Use actual model renders for geometry evidence. Label host-rendered, native-rendered, and recorded figures correctly.
Keep captions adjacent to figures. Separate chosen dimensions, calculations, measured readbacks, and open findings.
Display the relevant source revision and the scope of each check. Do not imply that a screenshot validates a mesh,
that finite samples prove global continuity, or that an appearance reconstruction is production geometry.

Use [the current build 42926 API reference](../../../docs/API_REFERENCE.md) when describing API capabilities.
Keep supplied documentation, recorded native results, offline checks, and new native execution distinct.
A current documentation baseline does not change an older model's build number or validate its replay on the newer build.
Historical failures need their original build label and a link to current behavior when that behavior has changed.

For comparisons, keep camera and scale fixed. Preserve a failure when changing the metric or sample locations.
Prefer compact embedded images for a standalone report. Keep large movies and generated mesh archives out of Git.
Retain third-party license notices for bundled viewers. Use authored figures or assets with documented redistribution terms.

Before delivery, check all local links and images, inspect the page at desktop and phone sizes, and exercise controls.
Remove private machine paths, source photos without clear permission, session identifiers, and unavailable artifact links.

## Public collections

For a multi-report handoff, share content-addressed local assets under `reports/assets/` and provide an offline catalogue. Test the complete downloaded tree. State clearly when an HTML depends on adjacent assets.

Audit visible images, inline JavaScript image maps, data-URL downloads, compressed viewer payloads, and image metadata. Removing a visible photo does not remove an embedded copy. Retain source credits when the image itself is excluded.

Remove photo-dependent controls when producing an edition without reference photos. Keep native view switches, calculations, and comparisons functional. Label recorded revisions, historical failures, and any omitted large media.
