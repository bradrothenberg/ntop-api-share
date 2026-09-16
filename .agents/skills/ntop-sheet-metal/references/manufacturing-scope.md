# Manufacturing scope and defensible claims

Use this reference when choosing a development method, reviewing a sheet-metal
design, or describing generated parts, blanks, tooling and animations.

## Define the process and the evidence

Identify material and temper, thickness, intended forming operations and release
directions where known. Keep missing choices as explicit assumptions. A geometric
study can proceed with provisional inputs; qualify the resulting claims to that
scope. Constant normal thickness is a target geometry assumption, not a prediction
that a stamped sheet will retain that thickness.

| Output | What the current workflow establishes | What further evidence is needed |
| --- | --- | --- |
| Nominal part | Editable analytic profiles and implicit geometry, with native probes and mesh checks at recorded inputs | Material response and process-specific formability |
| Bend-development estimate | Tangent lengths plus bend allowance using an explicit K-factor | Material, grain direction, tooling and bend-process calibration; coupon or shop data |
| Drawn/embossed geometric preform | A prescribed starting shape for illustration | Material-flow-based blank development, draw-in and trim allowances; validation of the forming sequence |
| Release envelope | Conservative separation from the accepted final native mesh along stated withdrawal directions | Working contact surfaces, access to undercuts, intermediate-stage collision checks and feasible operations |
| Working die design | Only claim this when an actual process and contact tooling have been developed | Holding strategy, radii/gaps, friction, force/capacity, piercing/trim sequence, springback compensation and tryout appropriate to the process |

Developable bends and drawn corners need different treatment. Do not apply a
K-factor unfold to closed bead ends, dimples or drawn corners and label it a
released cutting blank. Area or volume equivalence alone does not recover the
blank outline. The animation preforms use geometric midsurface lengths, not the
separate K-factor developments. See [the analytic method](method.md) and
[advanced construction](advanced.md).

## Embed selected constraints

For thickness, inside radius, relief, ligament, draft or clearance, record the
value and units, source, applicable material/process and assumed or calibrated
status. Identify whether the rule is a native input/dependency, a domain check,
or documentation only. Evaluate nominal and changed inputs, including a rejected
or out-of-domain case where the check supports rejection.

The 3-degree draft in the worked revision is provisional. State the pull direction
and which straight walls it covers; it is not a universal stamping requirement.
An open brake-bent wall does not automatically require draw draft. Returns and
two-ended bridges may need separate forming operations or segmented tool access.
The 0.5 mm release separation in [draft and release](draft-release.md) is an
envelope bound relative to a mesh, not punch-to-die working clearance or blanking
clearance. Successful release from the final part does not prove that the tools
can form it.

For process predictions, use suitable material plasticity and anisotropy, contact,
friction, holding forces and operation sequence. Evaluate relevant draw-in,
thinning, splits, wrinkling, springback and sensitivity, then correlate with
physical results. Name which checks were performed rather than declaring the
part manufacturable from geometric checks alone.

## Reports, animations and public descriptions

Prefer "implicit modeling" when describing this mixed analytic-profile and
field workflow. Boolean and mapped fields are not necessarily exact Euclidean
signed distance fields everywhere; their magnitude is not a global thickness or
clearance measurement.

Describe achieved outputs separately from proposed extensions. "Parameterized
parts with selected geometric constraints" and "tooling concepts" fit these
examples. A connected part, blank-development and tooling workflow is a goal;
the current stamped examples do not establish production blanks or qualified
dies. Do not claim a measured speed advantage without a defined comparison.

Keep animation scope inside the frames so it survives sharing. For example:
"Illustrative forming motion; translucent release envelopes; no material solver."
Where actually checked, add: "Final-state release clearance checked against the
native mesh; forming contact and tool access remain unqualified."
Use the same scope in the report and share caption. An illustrative motion loop
does not become a forming simulation because tools are shown.

## Primary-source context

- [nTop: implicits and fields](https://www.ntop.com/resources/blog/implicits-and-fields-for-beginners/) explains the geometric representation.
- [AutoForm Forming](https://www.autoform.com/en/products/autoform-forming/) separates feasibility, die-face development, blank/trim optimization, forming analysis and springback compensation.

These sources provide context for the workflow boundary. They do not validate
the authored example dimensions, process assumptions or tool envelopes.
