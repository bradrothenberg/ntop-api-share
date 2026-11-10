# CarShell measured case

This is the local 8 October 2026 car-shell reconstruction record. Measurements apply to this saved revision only.
The package manifest was written on 9 October UTC, still 8 October in the task's local timezone.
Use this record to locate reusable mechanisms and known limits, not to infer success on another car.

Start with SHELL_QUALITY.md (source-project artifact; not bundled) and
SHELL_MANIFEST.json (source-project artifact; not bundled).
The older SPEC.md (source-project artifact; not bundled) includes historical V1 sections.
Resolve current delivery status from the shell manifest and its bound evidence, not an old candidate paragraph.

## Selected deliverable

- Editable native model: CarShell.ntop (source-project artifact; not bundled).
- Controls: CarShell.controls.json (source-project artifact; not bundled).
- API recipe: CarShell.recipe.json (source-project artifact; not bundled).
- Native preview: CarShell.png (source-project artifact; not bundled).
- Source photograph: reference/source.jpg (source-project artifact; not bundled).
- Frozen reference: reference_lock.json (source-project artifact; not bundled).

The model uses a 20 by 12 cubic tensor control net, crowned ends, thin wheel-house returns, and an open underside.
One notebook metre represents one design length; actual vehicle dimensions were not supplied.
The final notebook has nine named sections and 1,960 collapsed non-root records. Its root is expanded.

Notebook SHA-256:
`700445f099d0f9ba13e2a47889493ab296bf6f728467e4a7155d27fdf302340a`.

Native geometry fingerprint:
`9234f9600cc69afec1af2f96713a6fe2528c5beeb4d62c65babdb0cf484578b7`.

## Results and their scope

| Measurement | Result | Scope |
|---|---|---|
| Native silhouette IoU | 99.1736704005% | Supplied 1206 by 814 view only |
| Intersection / union | 372,293 / 375,395 pixels | Frozen mask; no uncertainty exclusion |
| Missing / excess | 2,223 / 879 pixels | Same native image and camera |
| Native field witnesses | 124 passed; maximum difference 1.7862447632e-14 L | Finite independent sample set |
| Normal thickness | 23 samples, 0.0037026862 to 0.0039996087 L | Mathematical normal crossings, not global extrema |
| Skin curvature-variation energy / V1 | 0.1403037691 | Same 241 by 161 untrimmed-skin grid |
| Composite regularity | 118 sampled locations; minimum gradient magnitude 0.1250302289 | Sampled regions only |
| Excluded trial witnesses | 26 | 24 removed by another trim; two unbracketed normal crossings |
| Full fine display mesh | Cancelled for resource pressure | No completed full fine mesh delivered |
| Class A acceptance | Not established | Tolerances and full-surface evidence remain incomplete |

The fairness result excludes caps, wheel transitions, offsets, and reflection continuity.
Global reach, minimum thickness, self-intersection freedom, and whole-surface regularity remain unverified.
The largest sampled curvature change on halving the differentiation step was 9.272447 inverse design lengths; no acceptance limit was set.

The native camera used a 1206 by 5412 sensor image and an exact central integer crop to 1206 by 814.
Rows 2299 through 3112 were retained, equivalent to slice `[2299:3113]`.
No image interpolation or warp was used.
The mask contained 374,516 foreground pixels, including the nominal uncertainty region.

Bound evidence:
native comparison (source-project artifact; not bundled),
native audit (source-project artifact; not bundled),
witness expectations (source-project artifact; not bundled),
fairness (source-project artifact; not bundled).

## Case parameters are not defaults

The selected shell used these normalized field controls:

```json
{
  "field_depth": 0.004,
  "opening_rise": 0.006,
  "lip_blend_width": 0.003,
  "wheel_depth_blend_width": 0.01,
  "underside_blend_width": 0.0008,
  "through_wheels": false,
  "band_after_wheels": true
}
```

Wheel definitions still determine which openings span the width; the switch alone does not describe every cut.
Do not reuse these values as physical thicknesses, blend radii, or universal settings.

## What changed the outcome

The earlier smooth shell had only about 98.54% native silhouette overlap.
Camera-only fitting did not recover the target.
The successful fit differentiated the actual crowned composite boundary, including exact cubic closest points and nested blend weights.
It retained fixed fairness and arch gates, then fitted the physical camera and validated native pixels.
Raw loft boundary sensitivities had missed cap-influenced regions.

The V1 solid achieved a slightly higher silhouette score, 99.2103457994%, but did not have the refined shell's shape quality or hollow construction.
V1 files were retained unchanged. This illustrates why silhouette alone cannot select a Class A body.

## Display limit and continuation caution

A fine central-strip AT mesh reduced the serrated underside preview locally.
A coarse strip passed basic topology checks but still looked serrated.
The fine strip took about 666 seconds and contained small components at artificial clip corners.
Neither pilot established full-body display quality.

The full fine mesh remained active after more than 20 minutes, with little system memory available.
Only the verified task-owned authoring process was stopped; the delivered notebook hash stayed unchanged.
See the cancellation receipt (source-project artifact; not bundled).
Historical process IDs, session records, timings, tolerances, and memory figures must not become defaults for a new session.

The helpers remain in the separate source project. Many have fixed source paths, model assumptions, or import-time side effects.
Inspect them before execution. Preserve this completed evidence while adapting copies for another model or experiment.
