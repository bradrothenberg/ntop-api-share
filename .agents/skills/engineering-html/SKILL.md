---
name: engineering-html
description: Build self-contained HTML engineering reports for these nTop demonstrations with readable evidence, native geometry figures, accessible controls, and explicit validation limits.
---

# Engineering HTML reports

Use templates/report.html and templates/report.css as the local starting point.
The included demo reports show native geometry, assembly inspections, and before/after comparisons.
For PDF output, use [engineering-report](../engineering-report/SKILL.md).

Lead with the model and its purpose. Follow the nTop document design rules below.
Keep the page readable at desktop and phone widths. Make controls keyboard-operable and label them.
Support light and dark themes without remote font or script dependencies.

## nTop report design

Use the tokens from the local `ntop-design-v1` and `ntop-docs-v1` skills.
The values below keep this shared skill usable without those local skills.
The user's report preference makes nTop blue the primary highlight color, including in light mode.
This overrides the orange document accent in the source design guidance.

- Highlight text, links, section numbers, key values, and callout labels use nTop blue `#16489D`.
  On dark surfaces, use the design skill's lighter blue `#248AFF`.
  Use `--accent` and the `.highlight` class (or `mark`) for highlighted text.
  Keep ordinary bold text in the body text color. Use blue for selected emphasis.
- Use a cool grey page `#F7F8FA`, white surfaces `#FFFFFF`, and panel grey `#F0F2F5`.
  Use ink `#262626`, headline ink `#0A0A0A`, and muted text `#6D6C6A`.
  Use hairlines `#E4E7EC` and stronger rules `#CBD0D8`.
  Blue callouts use the pale tint `#EDF2FB` and a 3px blue left rule.
- Use `"Aeonik", "Inter", system-ui, sans-serif` for headings and body.
  Use `"Aeonik Fono", "IBM Plex Mono", ui-monospace, monospace` for labels, section numbers, and code.
  Use locally available fonts and system fallbacks. Do not bundle licensed fonts or require a font download.
- Use a large, tight, sentence-case title, a short purpose statement, and a mono metadata row.
  Separate numbered evidence sections with hairline rules. Keep generous space between sections.
- Use mono uppercase table headers on the grey panel, horizontal row rules, and plain white rows.
  Wrap wide tables in `.table-wrap` or `.tw`. Keep the page within the viewport.
- Use one blue highlight per visual group. For categorical charts, use blue for the featured series
  and neutral colors for context. Keep scientific color scales and explicit pass/fail colors meaningful.
- Keep the report anatomy suited to engineering evidence: purpose, summary, measured results,
  figures, limitations, and next steps. Use the deck's blue emphasis with the document layout.

The template supports the system theme and explicit `data-theme="light"` or `data-theme="dark"`
on the root element. Verify highlight contrast and table readability in both themes.

## Engineering evidence

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
