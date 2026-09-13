# Rebuild the shared propeller gallery using only adjacent public assets.
from pathlib import Path
import html,json
ROOT=Path(__file__).resolve().parents[3]
DEMO=ROOT/'demos/propellers'

def render():
    manifest=json.loads((DEMO/'manifest.json').read_text())
    css=(ROOT/'templates/report.css').read_text()
    css+='''
:root[data-theme="light"]{color-scheme:light;--paper:#f7f8fa;--ink:#262626;--muted:#59616b;--rule:#d5dae0;--card:white}
:root[data-theme="dark"]{color-scheme:dark;--paper:#171b21;--ink:#eef0f4;--muted:#b2bac5;--rule:#3e4755;--card:#20262e}
nav,.filters{display:flex;flex-wrap:wrap;gap:14px;margin:20px 0}button{font:inherit;padding:8px 13px;background:var(--card);color:var(--ink);border:1px solid var(--rule);cursor:pointer}button[aria-pressed=true]{outline:2px solid var(--accent)}.card{border:1px solid var(--rule);background:var(--card);padding:20px}.card img{border:1px solid var(--rule)}.card h3{margin:6px 0 18px}a,code{overflow-wrap:anywhere}.meta{font:12px ui-monospace,monospace;color:var(--muted)}.hidden{display:none}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%}th,td{padding:10px;text-align:left;border-bottom:1px solid var(--rule)}
'''
    cards=[]
    for item in manifest['cases']:
        if item['group']=='assembly':continue
        k=item['id'];g=item['recorded_geometry'];title=html.escape(item['title'])
        family='Airfoil candidate' if item['group']=='airfoil' else 'Original section study'
        note=item['description']
        if item.get('half_twist_degrees')==180:note+=' The section edges exchange after one circuit. Two overlapping half sweeps close each petal.'
        elif k.endswith('10_folded_loop'):note+=' This retained earlier version has no Mobius half-turn.'
        if item['natural_tips']:note+=' Radial clipping is inactive; the tips retain the swept shape.'
        cards.append(f'''<article class="card" data-family="{item['group']}" id="{k}"><p class="meta">{family} / {html.escape(item['profile'])}</p><h3>{title}</h3><img src="{item['image'].removeprefix('reports/')}" alt="Recorded native nTop view: {title}, {family}"><p>{html.escape(note)}</p><p>{g['swept_diameter_mm']:.3f} mm measured diameter. {g['triangles']:,} triangles. {g['components']} watertight component.</p><nav><a href="../{item['recipe']}">Saved construction recipe</a><a href="../{item['design']}">Profile and rails</a><a href="../{item['measurements']}">Recorded measurements</a></nav><code>--case {k}</code></article>''')
    body=f'''<nav><a href="../README.md">Setup and replay</a><a href="../manifest.json">All files and hashes</a><a href="../CFD_PLAN.md">Optimization plan</a><a href="../../../reports/index.html">Report catalogue</a><button id="theme">Switch theme</button></nav>
<div class="note"><strong>Recorded geometry, ready for native replay.</strong><p>Twenty-two complete construction graphs cover the eight-inch assembly, separate spinner, ten original section studies, and ten airfoil candidates. The two assembly notebooks retain their native caches. Large cached blade notebooks and STL files are generated locally by replay.</p><p>Source models were evaluated with nTop build 42926. Public packaging and replay checks run offline. No accepted aerodynamic optimum, acoustic prediction, or safe-speed qualification is claimed.</p></div>
<h2><span class="num">01</span> Mounting and spinner retention</h2>
<p>The baseline uses an eight-inch diameter, assumed four-inch pitch, NACA 0015 blade section, and a 5.10 mm shaft bore. The motor reference is the documented Scorpion SII-2212 adapter interface. Both clamp faces stay flat through the adjacent root blends.</p>
<div class="grid"><figure><img src="assets/spinner_mount.png" alt="Native nTop view of the spinner and motor assembly"><figcaption>Recorded native assembly view. The spinner remains a separate part.</figcaption></figure><figure><img src="assets/retention_cutaway.png" alt="Native nTop cutaway of the spinner screw and adapter"><figcaption>A central M3 screw retains the spinner on a custom M5 extension nut. The nut clamps the propeller independently.</figcaption></figure></div>
<nav><a href="../models/assembly.ntop">Assembly notebook</a><a href="../models/spinner.ntop">Spinner notebook</a><a href="../RETENTION.md">Retention dimensions and assembly order</a><a href="../evidence/sources.json">Public dimensions and assumptions</a></nav>
<p>Prepare working copies before opening the tracked notebooks. Their export paths use the repository's portable path notation. Thread flanks and manufacturing tolerances are not modeled.</p>
<h2><span class="num">02</span> Inspect the twenty blade studies</h2>
<p>Each study uses native Sweep along Two Rails. The center rail locates the section; the other rail controls chord and rotation. The original studies use elliptical sections. The airfoil set uses NACA 0015 or an explicitly labeled symmetric NACA-derived profile where a half twist exchanges the edges.</p>
<div class="filters" role="group" aria-label="Blade family"><button data-filter="all" aria-pressed="true">All twenty</button><button data-filter="airfoil" aria-pressed="false">Airfoil candidates</button><button data-filter="elliptical" aria-pressed="false">Original studies</button></div><div class="grid">{''.join(cards)}</div>
<h2><span class="num">03</span> Reproduce and inspect</h2>
<pre>uv run --locked python demos/propellers/scripts/replay.py --case airfoil_07_three_petal</pre>
<p>Review the generated import script, then dispatch it into an empty task-owned notebook. The script writes a working notebook, recipe readback, and mesh exports under the ignored output folder. Wait for completion before reading them. Collapse a separate final notebook after the native save.</p>
<p>The saved graphs preserve functions, connections, literal values, units, and guide points. Replay does not rerun the original design-generation algorithm or CFD workflow. Native screenshots and measurements on this page remain recorded evidence of their identified source revisions.</p>
<h2><span class="num">04</span> Flow optimization and remaining work</h2>
<p>A rotating FUN3D smoke test completed, and the wall velocities matched the prescribed rotation. The longer trial reached 956 iterations before its runtime cutoff. Boundary-layer mesh qualification, converged performance, adjoint gradient checks, unsteady wake output, and acoustic prediction remain open.</p>
<p>The <a href="../CFD_PLAN.md">optimization plan</a> defines the operating points and staged validation. It carries no cloud credentials or solver binaries. The unusual shapes are candidates for comparison, not established improvements.</p>
<p>Geometry references: <a href="https://ntrs.nasa.gov/citations/20010088092">Gilinsky, Seiner, and Backley, AIAA/CEAS 98-2260</a>; <a href="https://personal.math.ubc.ca/~CLP/CLP4/clp_4_vc/sec_orientation.html">UBC half-twist construction</a>. Supplied reference photographs are excluded from this public collection.</p>'''
    template=(ROOT/'templates/report.html').read_text()
    values={'title':'Propellers built with two rails','dek':'A retained spinner, conventional blades, and closed-loop experiments in the native Notebook API.',
            'css':css,'body':body,'footer':'Build 42926 / source work recorded September 2026 / public graph replay and offline audit'}
    for key,value in values.items():template=template.replace('{{'+key+'}}',value)
    script='''<script>document.querySelectorAll('[data-filter]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));document.querySelectorAll('[data-family]').forEach(c=>c.classList.toggle('hidden',b.dataset.filter!=='all'&&c.dataset.family!==b.dataset.filter));});document.getElementById('theme').onclick=()=>{let r=document.documentElement;let dark=r.dataset.theme==='dark'||(!r.dataset.theme&&matchMedia('(prefers-color-scheme:dark)').matches);r.dataset.theme=dark?'light':'dark';};</script>'''
    target=DEMO/'reports/index.html';target.write_text(template.replace('</body>',script+'</body>'),encoding='utf-8')
    return target

if __name__=='__main__':print(render())
