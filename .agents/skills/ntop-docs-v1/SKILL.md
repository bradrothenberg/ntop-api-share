---
name: ntop-docs-v1
description: "Structure and deliver nTop engineering HTML reports with evidence, captions, source links, limitations, accessible tables, and a verified rendered preview."
---

# nTop engineering documents

Use [engineering-html](../engineering-html/SKILL.md) as the implemented report workflow.
Use [ntop-design-v1](../ntop-design-v1/SKILL.md) for design and [ntop-writing-style](../ntop-writing-style/SKILL.md) for prose.
The repository's [HTML template](../../../templates/report.html) and [CSS](../../../templates/report.css) replace duplicated boilerplate from the original skill.

## Content and evidence

Lead with the artifact, its purpose, revision, and measured outcome.
Use a short summary followed by the engineering evidence needed to assess it.
Keep supplied dimensions, assumptions, calculations, measured native results, and open questions distinct.
Show sources and units adjacent to important values.
Link native notebooks, scripts, receipts, and compact figures where available.
Preserve failed checks and explain the limits of each analysis.

Use numbered sections only when they help navigation.
Place captions next to figures. Label native renders, host renders, recorded evidence, and conceptual diagrams accurately.
Keep camera and scale consistent in comparisons. A geometry picture does not establish structural adequacy.
Use tables for requirements, measured comparisons, and checks with explicit criteria.
Keep build-specific findings attached to their original revision.

## Rendered delivery

Use local assets and fonts with offline fallbacks. Keep document width responsive and wide tables contained.
Verify light/dark themes, links, keyboard controls, and the rendered layout.
When the user requests an HTML report, start a local HTTP preview from the report root and verify the exact URL in a browser.
Put that live preview link first in the report delivery. A file panel showing source does not count as a rendered preview.
Keep the preview process available for the user.
For a PDF artifact, use [engineering-report](../engineering-report/SKILL.md) and inspect the rendered pages.

The blue highlight in this repository overrides the orange document accent in the original source skill.
