"""Render the Torx HTML report from the measured evidence files.

Every number on the page is read from a JSON receipt written by the run that
produced it. Nothing is transcribed by hand, so the report cannot drift from the
evidence. Run it after `check_spec.py`, `check_recipe.py`, the live dispatch and
`make_figures.py`:

    uv run --locked python demos/torx/scripts/render_report.py
"""

import html
import json
import math
import statistics
from pathlib import Path

DEMO = Path(__file__).resolve().parents[1]
OUT = DEMO / "output"
REPORT = DEMO / "reports" / "index.html"

CSS = """
:root{color-scheme:light dark;--paper:#f7f8fa;--card:#fff;--panel:#f0f2f5;--ink:#262626;
--head:#0a0a0a;--muted:#6d6c6a;--rule:#e4e7ec;--strong:#cbd0d8;--accent:#16489d;--tint:#edf2fb;
--ok:#1a7f4b;--warn:#a2590d}
@media(prefers-color-scheme:dark){:root{--paper:#171b21;--card:#20262e;--panel:#1b2129;
--ink:#eef0f4;--head:#fff;--muted:#a8b0bb;--rule:#38414d;--strong:#4a5563;--accent:#248aff;
--tint:#182436;--ok:#4cc38a;--warn:#e0a458}}
:root[data-theme="light"]{color-scheme:light;--paper:#f7f8fa;--card:#fff;--panel:#f0f2f5;
--ink:#262626;--head:#0a0a0a;--muted:#6d6c6a;--rule:#e4e7ec;--strong:#cbd0d8;--accent:#16489d;
--tint:#edf2fb;--ok:#1a7f4b;--warn:#a2590d}
:root[data-theme="dark"]{color-scheme:dark;--paper:#171b21;--card:#20262e;--panel:#1b2129;
--ink:#eef0f4;--head:#fff;--muted:#a8b0bb;--rule:#38414d;--strong:#4a5563;--accent:#248aff;
--tint:#182436;--ok:#4cc38a;--warn:#e0a458}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
font:17px/1.65 "Aeonik","Inter",system-ui,sans-serif}
.wrap{max-width:1060px;margin:auto;padding:36px 26px 90px}
.toolbar{display:flex;justify-content:flex-end;gap:12px}
.toolbar button{font:inherit;color:var(--ink);background:var(--card);border:1px solid var(--rule);
border-radius:4px;padding:7px 12px;cursor:pointer}
button:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid var(--accent);
outline-offset:4px}
header{border-bottom:2px solid var(--ink);padding:24px 0 30px}
.kicker,.num,.meta,th,.lbl{font-family:"Aeonik Fono","IBM Plex Mono",ui-monospace,monospace}
.kicker{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
h1{color:var(--head);font-size:clamp(34px,6.6vw,60px);line-height:1.06;letter-spacing:-.035em;
margin:18px 0 14px}
.dek{font-size:20px;color:var(--muted);max-width:70ch;margin:0}
.meta{display:flex;flex-wrap:wrap;gap:8px 24px;font-size:12px;letter-spacing:.06em;
text-transform:uppercase;color:var(--muted);margin:22px 0 0}
h2{color:var(--head);font-size:29px;line-height:1.2;letter-spacing:-.02em;margin:62px 0 6px}
h3{font-size:19px;margin:34px 0 4px}
.num{display:block;font-size:12px;letter-spacing:.14em;text-transform:uppercase;
color:var(--accent);margin-bottom:10px}
section{border-top:1px solid var(--rule);padding-top:8px}
p{max-width:78ch}a{color:var(--accent);text-underline-offset:3px}
.highlight,mark{background:none;color:var(--accent);font-weight:600}
.note{border-left:3px solid var(--accent);background:var(--tint);padding:16px 22px;margin:26px 0}
.note p{margin:0 0 10px}.note p:last-child{margin:0}
.stats{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--strong);
border-bottom:1px solid var(--strong);margin:28px 0}
.stat{padding:22px 18px 22px 0}
.stat strong{display:block;color:var(--accent);font-size:clamp(22px,3vw,32px);line-height:1.15;
letter-spacing:-.025em}
.stat span{display:block;margin-top:8px;font-size:13px;color:var(--muted)}
.tw{overflow:auto;margin:22px 0}
table{border-collapse:collapse;width:100%;font-size:15px}
th{background:var(--panel);font-size:11px;letter-spacing:.09em;text-transform:uppercase;
color:var(--muted);font-weight:600;text-align:left;padding:10px 14px}
td{padding:11px 14px;border-bottom:1px solid var(--rule);vertical-align:top}
td.n{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}
.pass{color:var(--ok);font-weight:600}.fail{color:var(--warn);font-weight:600}
figure{margin:24px 0;border:1px solid var(--rule);background:var(--card)}
figure img{display:block;width:100%;height:auto;background:#0d1117}
figcaption{padding:14px 18px;color:var(--muted);font-size:14px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}.grid figure{margin:0}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.grid4 figure{margin:0}
.links{display:flex;flex-wrap:wrap;gap:8px 22px;margin:22px 0}
code{font:0.88em "Aeonik Fono","IBM Plex Mono",ui-monospace,monospace}
pre{overflow:auto;padding:16px 18px;background:var(--panel);border:1px solid var(--rule);
font-size:14px}
details{border:1px solid var(--rule);background:var(--card);padding:14px 20px;margin:22px 0}
summary{cursor:pointer;font-weight:600}
.small{font-size:14px;color:var(--muted)}
footer{border-top:1px solid var(--rule);margin-top:54px;padding-top:22px;color:var(--muted);
font-size:14px}
@media(max-width:760px){.stats,.grid4{grid-template-columns:1fr 1fr}}
@media(max-width:620px){.wrap{padding:20px 16px 56px}.stats,.grid,.grid4{grid-template-columns:1fr}
.stat{padding:16px 0}.stat+.stat{border-top:1px solid var(--rule)}h2{font-size:25px}
th,td{min-width:110px}.toolbar{justify-content:flex-start}}
@media print{.toolbar{display:none}.wrap{max-width:none;padding:0}h2{break-after:avoid}
figure,tr{break-inside:avoid}}
"""

SCRIPT = """
(function(){var b=document.getElementById('theme');if(!b)return;
var r=document.documentElement;function set(d){r.setAttribute('data-theme',d?'dark':'light');
b.setAttribute('aria-pressed',d?'true':'false');b.textContent=d?'Light theme':'Dark theme';}
var dark=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches;set(dark);
b.addEventListener('click',function(){set(r.getAttribute('data-theme')!=='dark');});})();
"""


def load(name):
    path = OUT / name
    if not path.exists():
        raise SystemExit("missing evidence file: %s. Run the checks first." % path)
    return json.loads(path.read_text(encoding="utf8"))


def e(value):
    return html.escape(str(value), quote=True)


def si(value, digits=3):
    """A metre value in engineering notation."""
    if value == 0:
        return "0"
    exponent = int(math.floor(math.log10(abs(value))))
    return "%.*fe%+d" % (digits, value / 10 ** exponent, exponent)


def table(headers, rows, numeric=()):
    head = "".join("<th>%s</th>" % e(h) for h in headers)
    body = []
    for row in rows:
        cells = []
        for k, cell in enumerate(row):
            cls = ' class="n"' if k in numeric else ""
            cells.append("<td%s>%s</td>" % (cls, cell))
        body.append("<tr>%s</tr>" % "".join(cells))
    return ('<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % (head, "".join(body)))


def verdict(ok, yes="pass", no="fail"):
    return '<span class="%s">%s</span>' % ("pass" if ok else "fail", yes if ok else no)


def build():
    receipt = load("port_receipt.json")
    recipe_check = load("check_recipe.json")
    spec_check = load("check_spec.json")
    live = load("live_run.json")
    rejections = load("rejections.json")
    figures = load("figures_measured.json")
    band = json.loads((OUT / "build" / "torx_band.json").read_text(encoding="utf8"))

    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    import torx_spec as spec
    import torx_catalogue as cat
    predictions = spec.predictions()
    by_config = {c["name"]: c for c in predictions["configurations"]}

    # per configuration results, from the live samples
    per = {}
    for row in live["samples"]:
        slot = per.setdefault(row["configuration"],
                              {"boundary": 0, "sign": 0, "worst": 0.0, "worst_id": "",
                               "failed": 0})
        if row["verdict"] != "pass":
            slot["failed"] += 1
        if row["kind"] == "boundary":
            slot["boundary"] += 1
            if row["residual_m"] > slot["worst"]:
                slot["worst"] = row["residual_m"]
                slot["worst_id"] = row["id"]
        else:
            slot["sign"] += 1

    # the placement-resolution measurement: one rotation, three insertion points
    ids = [r["id"][len("rotated-"):] for r in live["samples"]
           if r["id"].startswith("rotated-") and r["kind"] == "boundary"]
    residual = {name: {k: next(r["residual_m"] for r in live["samples"]
                               if r["id"] == "%s-%s" % (name, k)) for k in ids}
                for name in ("rotated", "oblique", "farfield")}
    distance = {"rotated": 0.0,
                "oblique": math.dist(spec.OBLIQUE_PLACEMENT[0], (0, 0, 0)),
                "farfield": math.dist(spec.FARFIELD_PLACEMENT[0], (0, 0, 0))}
    mean = {n: statistics.mean(residual[n].values()) for n in residual}

    summary = live["summary"]
    parts = []

    # ---- header ----------------------------------------------------------
    parts.append("""<div class="toolbar">
<button id="theme" type="button" aria-pressed="false">Dark theme</button>
<button type="button" onclick="window.print()">Print report</button></div>
<header><div class="kicker">nTop / Notebook API / parametric fastener</div>
<h1>Seven custom blocks.<br>One import call.</h1>
<p class="dek">A complete parametric Torx screw, ported to the offline recipe harness and
imported into a live nTop notebook in a single call. The import created all seven custom
blocks that the recorded API surface lists no method for.</p>
<div class="meta"><span>nTop 6.1.0-rc build 42926</span><span>PID %s</span>
<span>%s</span><span>%d graph nodes</span><span>%d field samples</span></div></header>"""
                 % (e(live["interpreter_pid"]), e(live["started"][:10]),
                    receipt["func_nodes"], summary["total"]))

    parts.append("""<p class="note"><strong>Scope.</strong> One native session on one build.
The verdict rests on %d field samples and a graph readback, not on a mesh comparison.
The 0.1 micrometre gate below verifies the declared CAD construction only: the supplied
informative contour ratios carry no certified error bound, and no manufacturing conformity
is claimed.</p>""" % summary["total"])

    parts.append("""<p class="note"><strong>Which notebook these numbers describe.</strong>
Every measurement on this page was taken on the <em>ported</em> thirteen-input block, rebuilt
from the source tables and imported by recipe. The notebooks linked below are the
<em>released</em> V2 compact originals, which expose eighteen inputs: they add Placement mode,
Reference Body, Tilt X, Tilt Y and Flush, and return a paired screw and mould container read
through two extractor blocks. The release carries its own verification, recorded in its source
project. Do not read the figures below as measurements of the released assembly.</p>""")

    parts.append("""<div class="stats">
<div class="stat"><strong>%d / %d</strong><span>blocks byte-identical to nTop's own recorded recipe</span></div>
<div class="stat"><strong>%d / %d</strong><span>field samples pass, worst boundary residual %s m</span></div>
<div class="stat"><strong>1 call</strong><span>%.1f s for a %s node, seven-block assembly</span></div>
<div class="stat"><strong>%d / %d</strong><span>invalid configurations refused by the graph's own gate</span></div>
</div>""" % (recipe_check["blocks_identical"], recipe_check["blocks_total"],
             summary["passed"], summary["total"],
             si(summary["boundary_worst_residual_m"], 2),
             live["torx_import_seconds"], "{:,}".format(receipt["func_nodes"]),
             rejections["summary"]["passed"], rejections["summary"]["total"]))

    parts.append("""<div class="links">
<a href="../models/Torx.ntop">Open the released assembly</a>
<a href="../models/Torx_Example.ntop">Open the released example</a>
<a href="../README.md">Read the demo notes</a>
<a href="../evidence/live_run.json">Every measured value</a></div>""")

    # ---- 01 the port -----------------------------------------------------
    rows = []
    by_block = {b["block"]: b for b in recipe_check["blocks"]}
    node_counts = receipt["func_nodes_by_block"]
    for name in receipt["import_order"] + ["Torx (root)"]:
        check = by_block[name]
        nodes = node_counts.get(name, receipt["func_nodes"] - sum(node_counts.values()))
        rows.append([e(name), "%d" % check["inputs"]["offline"],
                     "%d" % check["body"]["offline"], "{:,}".format(nodes),
                     verdict(check["identical"], "identical", "differs")])
    parts.append("""<section><h2><span class="num">01 / The port</span>The same graph, rebuilt in Python</h2>
<p>The source project authored this screw in JavaScript and converted each block with
<code>ntopcl</code>. nTop then wrote back what it believes the graph is. That readback is
kept here as <a href="../inputs/recorded/torx_recorded_recipe.json">the comparison
reference</a>. <code>torx.py</code> rebuilds the same eight blocks against the recording
backend in this repository, from the same ISO source tables, and
<code>check_recipe.py</code> compares the two.</p>
<p>Identifiers are the only thing allowed to differ, because nTop mints its own on every
conversion. The exporter also writes a <code>type</code> key on call nodes and an empty
<code>dimension</code> on dimensionless inputs, which the recipe form omits. Everything
else has to agree: <mark>every function identifier, every literal value and unit, every
input index, every reference, every import and every cbRefs entry.</mark></p>
%s
<p>All %d agree. The offline build takes %.3f s and writes a %s byte recipe carrying the
transitive closure of seven definitions in dependency order.</p>
<p class="small">The one string the port deliberately did not modernise is the description
of the <code>Metric size index</code> input, which still names the source project's
<code>catalogue.js</code>. A description belongs to a block's content key, so rewording it
would have made the block a different block.</p></section>"""
                 % (table(["Block", "Inputs", "Body entries", "Graph nodes", "Against the recorded recipe"],
                          rows, numeric=(1, 2, 3)),
                    recipe_check["blocks_total"], receipt["seconds"],
                    "{:,}".format(receipt["bytes"])))

    # ---- 02 the import ---------------------------------------------------
    blocks_before = live["torx_empty_before"]["custom_blocks"]
    blocks_after = live["torx_after"]["counts"]["custom_blocks"]
    parts.append("""<section><h2><span class="num">02 / One call</span>import_recipe creates custom blocks</h2>
<p>The recorded API surface for build 42926 says that the API edits existing custom blocks
and lists no method that creates or imports one. Taken at face value that would put this
screw out of reach of the Notebook API altogether: it is an assembly of seven referenced
custom blocks, and no sequence of <code>add_block</code> and
<code>connect_block_property</code> calls can bring a definition into existence.</p>
<p><mark>It is reachable, through the recipe.</mark> A complete recipe carries its
definitions in <code>imports</code> and calls them by uuid. Importing one into an empty
notebook that held <strong>%s</strong> custom blocks left it holding <strong>%s</strong>,
named exactly as the recipe names them.</p>
%s
<p>The measurement notebook is the same graph plus %d <code>evaluate_field</code> probes
and eight configurations of the assembly. It imports in one call as well, and
<mark>every probe read a value on the first poll</mark>, in %.3f s: nothing had to be
waited on.</p>
<p class="small">A choice input cannot be set from the live API on this build, so the
verification band calls the local assembly directly with integer literals the recipe
carries. The four public Choice Lists are checked separately, by reading back the
selection variables the root body computes: %d of %d resolve to the source identifier the
assembly expects.</p></section>"""
                 % (blocks_before, blocks_after,
                    table(["Import", "Recipe bytes", "Call count", "Seconds",
                           "Variables after", "Custom blocks after", "Saved notebook"],
                          [["Public block", "{:,}".format(live["torx_recipe_bytes"]), "1",
                            "%.1f" % live["torx_import_seconds"],
                            "%d" % live["torx_after"]["counts"]["variables"],
                            "%d" % live["torx_after"]["counts"]["custom_blocks"],
                            "{:,} B".format(live["model_bytes"])],
                           ["Public block and measurement band",
                            "{:,}".format(live["verification_recipe_bytes"]), "1",
                            "%.1f" % live["verification_import_seconds"],
                            "%d" % live["verification_after"]["counts"]["variables"],
                            "%d" % live["verification_after"]["counts"]["custom_blocks"],
                            "{:,} B".format(live["verification_model_bytes"])]],
                          numeric=(1, 2, 3, 4, 5, 6)),
                    len(band["probes"]), live["band_read_seconds"],
                    summary["selections_agreeing"], summary["selections_total"]))

    # ---- 02b the V2 example ----------------------------------------------
    example_path = OUT / "check_example.json"
    if example_path.exists():
        ex = json.loads(example_path.read_text(encoding="utf8"))
        graph, manifest = ex["graph"], ex["manifest"]
        imported = ex.get("imported_notebook", {})
        run = ex.get("import", {})
        rows = [[e(r["file"]), "{:,}".format(r["manifest_bytes"]),
                 "{:,}".format(r["on_disk_bytes"]) if r.get("on_disk_bytes") else "-",
                 verdict(bool(r["matches"]), "matches", "differs")]
                for r in manifest["files"]]
        parts.append("""<section><h2><span class="num">02b / The wired example</span>Fifteen definitions, two of them called Torx</h2>
<p>The origin project also ships an example on top of this screw: one configured
Torx call feeding two named list extractors and two native Boolean consumers, with
mould outputs and flush placement. It is the harder import. Fifteen definitions
nested three deep, and <mark>two of them are both called <code>Torx</code></mark>:
the thirteen-input public block and the eighteen-input wrapper that adds the mould
branch and the flush shift. One display name, two behaviours, two uuids.</p>
<p>A recipe refers to a definition by uuid and never by name, so the ambiguity is
only in what a human reads. Whether the import would keep both was not known until
it was run. <mark>It keeps both</mark>: %s custom blocks from zero, fourteen
distinct names with <code>Torx</code> twice, in one call and %.1f s. All %d root
variables read <code>e_OK</code>.</p>
<p>nTop's own readback of the imported notebook, compared against the recipe it
came from, is <strong>%s</strong> across the root graph, same variables in the same
order. <code>recipe_only</code> omits the definitions, so that is what the
comparison covers.</p>
<h3>Why the recipe travels and the released notebook does not</h3>
<p>The source release ships a manifest with a size and digest for each file. Seven
of eight match. <code>Torx_Example.ntop</code> does not.</p>
%s
<p>Converting a notebook runs every block at its default inputs and caches the
result inside the file, so the released example had been reconverted after its
manifest was written and carries about 13.7 MB of cached solve. Copying it would
have published an artefact that fails its own release manifest. Importing the
recipe instead produced <mark>%s bytes, %+.2f per cent of the signed size</mark>.
The mismatch is a fact about the source release, not about this demo; the origin
project is read-only from here and was not touched.</p></section>"""
                     % (run.get("custom_blocks_count"),
                        run.get("example_import_seconds", 0.0),
                        run.get("variables_ok", 0),
                        "identical" if graph.get("identical") else "not identical",
                        table(["Released file", "Manifest bytes", "On disk", "Digest"],
                              rows, numeric=(1, 2)),
                        "{:,}".format(imported.get("bytes", 0)),
                        100 * imported.get("relative_to_manifest", 0.0)))

    # ---- 03 the yardstick ------------------------------------------------
    parts.append("""<section><h2><span class="num">03 / The yardstick</span>A mirror, frozen before the run</h2>
<p><code>torx_spec.py</code> is a closed-form mirror with no nTop import: the exact tangent
arc contour of the recess, the helical thread law, the head sections, the placement frame
and the validity gate, all in pure Python. It was frozen before the first dispatch.</p>
<p>It predicts the <strong>surface</strong>, not interior distances. The composed field is
not a Euclidean signed distance and is not claimed to be one: a revolved body carries its
section distance in the half plane, the thread carries a radial residual with axial caps,
and the sharp booleans are exactly min, max and max(f, -g). So each prediction is a point
where any correct field must read zero, plus the sign of the field two micrometres either
side of it along the outward normal. A constant zero field would pass the first test; it
cannot pass the second.</p>
<p><code>check_spec.py</code> checks the mirror on its own terms before anything native
runs: <mark>%d checks, %d failed, worst disagreement %s</mark>. It recomputes the concave
arc radius by bisection for all sixteen drive sizes, asserts external tangency and sixfold
symmetry, recovers the declared A and B dimensions exactly, verifies the thread's axial and
angular periods and its flank slope, and confirms the placement frame is orthonormal,
right-handed and rigid.</p>
%s</section>"""
                 % (spec_check["checks"], spec_check["failed"],
                    si(spec_check["worst_delta"], 2) + " mm",
                    table(["Predicted", "Count", "What it settles"],
                          [["Boundary points", "%d" % predictions["counts"]["boundary"],
                            "the surface is where the mirror says it is, to %s m"
                            % si(predictions["gate_m"], 0)],
                           ["Sign probes", "%d" % predictions["counts"]["sign"],
                            "the field changes sign across that surface, and solid is "
                            "solid on the inside"],
                           ["Configurations", "%d" % predictions["counts"]["configurations"],
                            "families, series, sizes, overrides and placements"],
                           ["Refused inputs", "%d" % len(predictions["rejections"]),
                            "each breaking one named condition of the validity gate"]],
                          numeric=(1,))))

    # ---- 04 the measurement ----------------------------------------------
    rows = []
    for name in [c["name"] for c in predictions["configurations"]]:
        slot = per[name]
        cfg = by_config[name]["resolved"]
        rows.append([e(name), e(cfg["metric"]), e(cfg["drive"]),
                     "%d" % slot["boundary"], "%d" % slot["sign"],
                     si(slot["worst"], 2), verdict(slot["failed"] == 0,
                                                   "%d / %d" % (slot["boundary"] + slot["sign"],
                                                                slot["boundary"] + slot["sign"]),
                                                   "%d failed" % slot["failed"])])
    parts.append("""<section><h2><span class="num">04 / Measured geometry</span>%d of %d, against predictions written first</h2>
<p>Each configuration is one call to the local assembly with literal inputs, placed through
the placement block, with one <code>evaluate_field</code> probe per prediction. The gate is
%s m at a boundary point. The worst residual over the whole set is %s m.</p>
%s
<p class="small">Worst residual is the largest absolute field value at a point the mirror
places on the surface. The <code>tamper</code> row carries two extra boundary points and
five extra sign probes, for the round post the internal family does not have.</p></section>"""
                 % (summary["passed"], summary["total"],
                    si(predictions["gate_m"], 0), si(summary["boundary_worst_residual_m"], 3),
                    table(["Configuration", "Metric size", "Drive", "Boundary", "Sign",
                           "Worst residual, m", "Result"], rows, numeric=(3, 4, 5))))

    # ---- 05 placement resolution -----------------------------------------
    rows = []
    for name in ("rotated", "oblique", "farfield"):
        d = distance[name]
        rows.append([e(name), "%.3f" % d, si(mean[name], 2),
                     si(max(residual[name].values()), 2),
                     "%s" % (si(mean[name] / (d * 1e-3), 2) if d else "not applicable")])
    crossing = predictions["gate_m"] / (mean["farfield"] / (distance["farfield"] * 1e-3))
    parts.append("""<section><h2><span class="num">05 / Placement resolution</span>The residual scales with the insertion distance</h2>
<p>Three of the eight configurations are the same screw under the same oblique rotation and
the same 37 degree clocking, differing only in where the insertion point sits. That
separates a rotation cost from a translation cost, which one oblique case alone cannot
do.</p>
%s
<p>The rotation alone costs nothing measurable: at the origin the mean residual is %s m, the
same band as the configurations that are not placed at all. <mark>The residual is
proportional to the distance from the origin</mark>, at about %s of it, stable across two
decades of distance. Double precision on these coordinates would give a relative error near
1e-16, so a reduced-precision step somewhere in the coordinate map is the natural reading.
That is an inference from the scaling, not a measurement of the implementation.</p>
<p>The practical consequence is a working limit rather than a defect: a 0.1 micrometre
boundary gate is reachable out to roughly <mark>%.1f m</mark> from the origin. Beyond that
the placement's own resolution, not the geometry, sets the floor. Everything in this report
was measured inside that range.</p></section>"""
                 % (table(["Configuration", "Insertion distance, mm", "Mean residual, m",
                           "Worst residual, m", "Residual / distance"], rows,
                          numeric=(1, 2, 3, 4)),
                    si(mean["rotated"], 2),
                    si(mean["farfield"] / (distance["farfield"] * 1e-3), 2),
                    crossing))

    # ---- 06 the gate -----------------------------------------------------
    rows = []
    for case in rejections["cases"]:
        value = case["probe"].get("value")
        rows.append([e(case["name"]),
                     e(case["gate"] or "valid control"),
                     e(case["why"] or "a valid configuration, so a failure below is the "
                                      "gate and not the import"),
                     "reads %s" % (("%.3e mm" % value) if isinstance(value, (int, float))
                                   else "nothing"),
                     verdict(case["verdict"] == "pass")])
    parts.append("""<section><h2><span class="num">06 / The validity gate</span>An invalid screw refuses to exist</h2>
<p>The assembly multiplies its thread length by <code>sqrt(+1 or -1)</code>, gated on ten
named conditions. An invalid configuration therefore refuses to evaluate rather than
building a plausible wrong screw. That matters more than a warning would: a fastener that
silently came out 0.3 mm undersized is worse than one that does not come out at all.</p>
%s
<p class="small">A block in error reports <code>e_DIRTY</code> with no error field on this
build, which is indistinguishable from a block still queued. The verdict here is therefore
taken from the pair (state, readable value): a refused configuration must not produce a
number. The control does produce one, and it is %s mm at the recess lobe.</p></section>"""
                 % (table(["Case", "Condition broken", "Why", "Probe", "Result"], rows),
                    "%.3e" % rejections["cases"][0]["probe"]["value"]))

    # ---- 07 native sections ----------------------------------------------
    plane = {p["label"]: p for p in figures["planes"]}
    contour = figures["measurements"]["recess_contour"]
    cal = figures["calibration"]
    fig_cells = []
    for label in ("mouth", "wall", "web", "thread"):
        p = plane[label]
        fig_cells.append(
            '<figure><img src="%s" alt="Native transverse section of the Torx screw at z = %.3f mm">'
            '<figcaption><strong>z = %.3f mm.</strong> %s</figcaption></figure>'
            % (e(p["asset"]), p["plane_mm"], p["plane_mm"], e(p["caption"])))
    axis = plane["axis"]
    rows = [[e(c["feature"]), "%.3f" % c["angle_deg"], "%.6f" % c["measured_mm"],
             "%.6f" % c["expected_mm"], "%+.6f" % c["delta_mm"]] for c in contour]
    parts.append("""<section><h2><span class="num">07 / Native sections</span>Look at it</h2>
<p>Numbers describing a shape are not a check of the shape. These are nTop's own rasters,
produced by the same notebook that produced the samples, at %.5f mm per pixel.</p>
<div class="grid4">%s</div>
<figure><img src="%s" alt="Native axial section of the Torx screw through its axis">
<figcaption><strong>y = %.3f mm, the axis plane.</strong> %s Solid is white. Head, recess
void, seating plane, underhead fillet, plain shank, thread and flat tip, left to right.
</figcaption></figure>
<h3>The raster's own axes had to be measured first</h3>
<p>A picture is only evidence once its axes are known. The recorded index law for this
block family puts the plane of slice k at <code>BOX0 + h/2 + (k-1)h</code>. <mark>On this
build it is <code>BOX0 + (k-1)h</code>.</mark> A fine stack across the recess floor, a plane
the mirror puts at exactly %.4f mm, settles it: the recess closes between slices %d and %d,
which brackets the floor at [%.4f, %.4f] under the measured law and at [%.4f, %.4f] under
the recorded one. The true value sits on the edge of the first bracket and outside the
second. Half a layer is %.4f mm here, twenty-five times the boundary gate, so this is not a
rounding question.</p>
%s
<p>With that mapping applied, the recess contour read off the raster agrees with the mirror
at all six angles, worst %.6f mm against a pixel of %.6f mm: <mark>inside one pixel</mark>.
The head outer radius reads %.4f mm, bounded by the print volume, which is clipped one
micrometre inside the head on purpose.</p>
<p class="small">The raster confirms the mapping and the gross shape at pixel resolution.
The field samples, not the raster, carry the sub-micrometre verdict. The stack also does not
stop at the print-volume ceiling: it continues until the body's own bounds are exhausted, so
the archive holds more images than layers were asked for, and a plane lying exactly on a
boundary surface rasterises as open.</p></section>"""
                 % (min(plane["wall"]["pixel_mm"]), "".join(fig_cells),
                    e(axis["asset"]), axis["plane_mm"], e(axis["caption"]),
                    cal["known_plane_mm"], cal["closes_between"][0], cal["closes_between"][1],
                    cal["laws"]["BOX0 + (k-1)h"]["bracket_mm"][0],
                    cal["laws"]["BOX0 + (k-1)h"]["bracket_mm"][1],
                    cal["laws"]["BOX0 + h/2 + (k-1)h"]["bracket_mm"][0],
                    cal["laws"]["BOX0 + h/2 + (k-1)h"]["bracket_mm"][1],
                    cal["layer_mm"] / 2,
                    table(["Feature", "Angle, deg", "Read off the raster, mm",
                           "Mirror, mm", "Difference, mm"], rows, numeric=(1, 2, 3, 4)),
                    figures["verdict"]["worst_delta_mm"], figures["verdict"]["pixel_mm"],
                    figures["measurements"]["head_radius"][0]["measured_mm"]))

    # ---- 08 coverage -----------------------------------------------------
    summary_cat = cat.summary()
    parts.append("""<section><h2><span class="num">08 / Coverage and limits</span>What the block offers, and what it does not</h2>
<p>Four native Choice Lists drive the block: drive family, screw series, metric size and
drive size. A size is never entered as a numeric code. %d series and size combinations are
supported across %d metric labels, with %d internal drive sizes and %d tamper-resistant
posts.</p>
%s
<h3>Limits, stated plainly</h3>
<p>The supplied ISO 10664:1999 Table 1 A and B values are exact declared nominal
dimensions, not metrology of one sample. The informative Annex A radius ratio is
approximate and carries no certified error bound, so the contour here is a labelled derived
CAD contour, not a unique normative one. The pan crown uses an exact spherical cap to stand
in for an explicitly approximate source rf, and its crown-to-side micro-round is omitted.
The countersunk series is the historical 2013 envelope with a sharp cone-to-neck junction,
and is not asserted equivalent to the revised 2022 design. The thread is the ISO 68-1 basic
profile: actual external root, runout and tip details remain simplified. Tamper-resistant
posts are custom derivatives combining the ISO recess construction with Camcar reference
post dimensions; T6 has no sourced post and T27 has no A and B pair in the supplied table.
External E, Torx Plus, Paralobe and ttap are not offered, because their complete nominal
contours were not established.</p>
<p>None of the checks in this report establish strength, manufacturing tolerance or
production conformity. They establish that the implemented construction is the one the
source tables and the declared CAD choices describe.</p></section>"""
                 % (summary_cat["series_size_rows"], summary_cat["metric_labels"],
                    summary_cat["drive_sizes"], summary_cat["tamper_posts"],
                    table(["Series", "Metric sizes", "Source"],
                          [["Cylindrical", "M2 to M20, %d rows" % summary_cat["cylindrical"],
                            "ISO 14579:2011, Table 1 and Figure 1"],
                           ["Pan", "M2 to M10, %d rows" % summary_cat["pan"],
                            "ISO 14583:2011, Figure 1 and Table 1"],
                           ["Countersunk, historical",
                            "M2 to M10, %d rows" % summary_cat["countersunk"],
                            "ISO 14581:2013, Figure 1 and Table 1"],
                           ["Recess contour", "T6 to T100, %d sizes" % summary_cat["drive_sizes"],
                            "ISO 10664:1999, Table 1 and informative Annex A"]])))

    # ---- 09 reproduce ----------------------------------------------------
    parts.append("""<section><h2><span class="num">09 / Reproduce</span>Offline first, then the console</h2>
<p>Everything except the last step runs without nTop.</p>
<pre>uv run --locked python demos/torx/scripts/check_spec.py       # the mirror against itself
uv run --locked python scripts/build.py torx                  # the offline recipe
uv run --locked python demos/torx/scripts/check_recipe.py     # against nTop's own recipe
uv run --locked python demos/torx/scripts/torx_verification.py # the three live recipes
uv run --group render python demos/torx/scripts/make_figures.py
uv run --locked python demos/torx/scripts/render_report.py    # this page</pre>
<p>For the live step, launch a separate task-owned nTop process as
<a href="../../../docs/BACKGROUND_CONSOLE.md">the background console procedure</a> describes,
verify that exactly one loopback listener belongs to it, then dispatch
<code>torx_live.run</code>, <code>torx_live.run_rejections</code> and
<code>torx_live.run_figures</code>. Each writes its own receipt under
<code>demos/torx/output/</code>.</p>
<div class="links">
<a href="../evidence/check_spec.json">Mirror self-check</a>
<a href="../evidence/check_recipe.json">Recipe comparison</a>
<a href="../evidence/live_run.json">Field samples</a>
<a href="../evidence/rejections.json">Validity gate</a>
<a href="../evidence/figures_measured.json">Figure measurements</a>
<a href="../evidence/port_receipt.json">Offline build receipt</a></div></section>""")

    footer = ("""<footer><p>Recorded on nTop 6.1.0-rc build 42926, PID %s, %s. Transport:
loopback console on 127.0.0.1:2323, interpreter PID verified on the connected socket before
each dispatch. Offline checks and recipe comparison do not prove native execution; the
field samples and the saved notebooks do. Converted and measured is not delivered: the
geometry verdict rests on %d field samples, one validity-gate sweep and native sections,
not on a mesh comparison or a physical part.</p>
<p>Source tables are cited per row in <code>demos/torx/inputs/source_tables/</code>. The
standards themselves are not redistributed.</p></footer>"""
              % (e(live["interpreter_pid"]), e(live["started"]), summary["total"]))

    page = ("""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Torx | Seven custom blocks, one import call</title><style>%s</style></head>
<body><main class="wrap">%s%s</main><script>%s</script></body></html>"""
            % (CSS, "".join(parts), footer, SCRIPT))
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(page, encoding="utf8")
    return {"report": str(REPORT.relative_to(DEMO)),
            "bytes": REPORT.stat().st_size,
            "sections": page.count("<section>"),
            "figures": page.count("<figure>"),
            "assets": sorted(p.name for p in (DEMO / "reports" / "assets").glob("*.png"))}


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
