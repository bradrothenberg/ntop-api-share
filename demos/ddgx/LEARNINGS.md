# Recorded lessons

This is an edited record of prior work. Its native results apply to those recorded revisions.
Local machine paths and omitted artifact links were removed for this public handoff.
Historical tool and artifact names below describe the source work. Use README.md for the runnable commands and files in this checkout.

# DDG(X) public concept reconstruction

Open `models/DDGX_Concept.ntop` in nTop. Open `reports/index.html` for the
native views, source notes, and validation status.

Revision 4, 10 September 2026, corrects the lower hull-to-bulb transition.
The hull and bulb share a lower rail. A narrow blend starts gradually at the
bulb root. Native samples show no downward reversal in three longitudinal cuts
over x/L = 0.70 to 0.89. Each cut also has a smaller maximum adjacent tangent
change than revision 3. All 17 native field checks pass.
The report includes matching before/after views and the measured contours.
Previous deliverables are omitted from this handoff.

The target is the attached 2022 PEO Ships concept. The model uses a normalized
one-metre hull. Actual DDG(X) length and hidden sections are not established by
the available reference. The requested 99% orthographic match remains unverified.

## Rebuild in this handoff

From the repository root, run:

```powershell
uv run --locked python scripts/build.py ddgx
uv run --locked python scripts/stage.py ddgx
```

Follow the staged command in a dedicated, empty nTop notebook. See [setup](../../docs/SETUP.md).
The editable source is in scripts/. Generated recipes and controls go to output/build/.
The report retains recorded native results. This public package does not include the full historical render pipeline.

The local loft helper copies originate in the earlier Lockheed_A-12 and F16
work. This project does not import code from retired folders.

`scripts/fair_forward_guides.py` runs the constrained keel fit during recipe
generation. Its objective and candidate results are in
`validation/loft_optimization.json`. This is a geometric fairing metric.
It is not a drag or reference-fidelity score.

## Native contour verification

`tools/probe_contour.py` evaluates the combined native hull field. Use `--csv`
to import sample coordinates through native Import Points. The point-block
route expands slowly at large sample counts. A 36-point benchmark confirmed
both routes agree within 3.5e-18 m. CSV coordinates use millimetres; returned
field values use metres. The shape remains a native implicit loft.

`tools/analyze_contour.py` extracts the first outside-to-inside crossing on
each vertical line. It writes the contour figure and comparison record.
The final grid uses x spacing 0.003 L and z spacing 0.0002 L. These are finite
sampling checks. They do not certify global curvature continuity.

The tested blend choices are in `validation/contour_tuning.json`. The selected
radius is 0.0015 L, introduced from x/L = 0.74 to 0.82. The blend then increases
to 0.009 L near the forward stem. The source recipe retains all controls.
