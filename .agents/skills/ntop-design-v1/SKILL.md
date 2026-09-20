---
name: ntop-design-v1
description: "Apply nTop typography, color, and layout conventions to engineering documents, figures, and presentations, using the repository reporting templates and offline font fallbacks."
---

# nTop document design

Use [engineering-html](../engineering-html/SKILL.md) for implemented report components and [ntop-docs-v1](../ntop-docs-v1/SKILL.md) for document structure.
Use the local [CSS](../../../templates/report.css) and [HTML template](../../../templates/report.html).
This public adaptation preserves the repository's blue-highlight preference.

| Role | Value |
|---|---|
| Primary highlight on light backgrounds | `#16489D` |
| Highlight on dark backgrounds | `#248AFF` |
| Page | `#F7F8FA` |
| Surface | `#FFFFFF` |
| Panel | `#F0F2F5` |
| Body ink | `#262626` |
| Heading ink | `#0A0A0A` |
| Muted text | `#6D6C6A` |
| Hairline | `#E4E7EC` |
| Strong rule | `#CBD0D8` |

Use Aeonik where licensed and locally available, with Inter and system sans-serif fallbacks.
Use Aeonik Fono or IBM Plex Mono where available, with system monospace fallbacks for labels and code.
Do not bundle commercial fonts or require a remote font download.

Use sentence-case headings, readable body text, generous space, and hairline section rules.
Use one main highlight per visual group. Keep scientific scales and pass/fail colors meaningful.
Tables use clear headers and horizontal rules. Wide tables scroll within their own container.
Verify text contrast, dark mode, small-screen layout, and keyboard access.

For presentations, the source grammar uses cream, near-black, or blue backgrounds and open layouts.
Use blue emphasis, large supported claims, restrained metadata, and clear figure labels.
For journal figures, follow the publication's figure rules before house styling. Preserve vector text and lines where practical.
Do not add corporate legal claims, attribution, or template assets without confirming their relevance and rights.
Pair all visual work with [ntop-writing-style](../ntop-writing-style/SKILL.md).
