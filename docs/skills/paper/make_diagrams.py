"""Create the paper skill maps with the nTop document design system.

Use NTOP_REPORT_FONT_DIR for licensed Aeonik variable fonts. The bundled report
style selects portable fallback fonts when those files are unavailable. PDF text
remains selectable. SVG lettering is outlined when TrueType outlines are present.
No font source files are copied into the output.
"""
import argparse
import io
import json
import math
from pathlib import Path
import sys
from xml.sax.saxutils import escape, quoteattr

from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / '.agents/skills/engineering-report/scripts'))
from report_style import F_BODY, F_HEAD, F_MONO, NT

W, H = 504, 648
FONT_CACHE = {}


def color_hex(color):
    return '#%02x%02x%02x' % tuple(round(v * 255) for v in (color.red, color.green, color.blue))


def outline_text(value, font_name, size, x, y, color):
    """Render the used letters as SVG paths, with an accessible text label."""
    face = pdfmetrics.getFont(font_name).face
    data = getattr(face, '_ttf_data', None)
    if data is None:
        family = 'monospace' if font_name == F_MONO else 'Arial, sans-serif'
        weight = '600' if font_name == F_HEAD else '400'
        return (f'<text x="{x:g}" y="{y:g}" font-family="{family}" '
                f'font-size="{size:g}" font-weight="{weight}" fill="{color_hex(color)}">{escape(value)}</text>')
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    if font_name not in FONT_CACHE:
        FONT_CACHE[font_name] = TTFont(io.BytesIO(data))
    font = FONT_CACHE[font_name]
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    pen = SVGPathPen(glyphs)
    cursor = 0
    for char in value:
        glyph_name = cmap.get(ord(char), '.notdef')
        glyphs[glyph_name].draw(TransformPen(pen, (1, 0, 0, 1, cursor, 0)))
        cursor += font['hmtx'].metrics[glyph_name][0]
    scale = size / font['head'].unitsPerEm
    return (f'<g aria-label={quoteattr(value)}><title>{escape(value)}</title>'
            f'<path fill="{color_hex(color)}" transform="translate({x:g},{y:g}) scale({scale:g},-{scale:g})" '
            f'd={quoteattr(pen.getCommands())}/></g>')


class Figure:
    def __init__(self, name, title):
        self.name, self.title = name, title
        self.drawing = Drawing(W, H)
        self.svg = []
        self.texts = []
        self.rect(0, 0, W, H, fill=NT.paper)

    def rect(self, x, y, w, h, fill=NT.white, stroke=None, dash=None):
        self.drawing.add(Rect(x, H-y-h, w, h, fillColor=fill, strokeColor=stroke,
                              strokeWidth=.6, strokeDashArray=dash))
        attrs = f' fill="{color_hex(fill) if fill else "none"}" stroke="{color_hex(stroke) if stroke else "none"}" stroke-width=".6"'
        if dash:
            attrs += ' stroke-dasharray="' + ' '.join(map(str, dash)) + '"'
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}"{attrs}/>')

    def line(self, x1, y1, x2, y2, color=NT.rule, dash=None, width=.6):
        self.drawing.add(Line(x1, H-y1, x2, H-y2, strokeColor=color,
                             strokeWidth=width, strokeDashArray=dash))
        extra = ' stroke-dasharray="' + ' '.join(map(str, dash)) + '"' if dash else ''
        self.svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color_hex(color)}" stroke-width="{width}"{extra}/>')

    def arrow(self, x1, y1, x2, y2, color=NT.muted, dash=None):
        self.line(x1, y1, x2, y2, color=color, dash=dash)
        angle = math.atan2(y2-y1, x2-x1)
        points = [(x2, y2)] + [(x2-3.3*math.cos(angle+a), y2-3.3*math.sin(angle+a)) for a in (-.45, .45)]
        self.drawing.add(Polygon([c for x,y in points for c in (x, H-y)], fillColor=color, strokeColor=None))
        self.svg.append(f'<polygon points="{" ".join(f"{x:g},{y:g}" for x,y in points)}" fill="{color_hex(color)}"/>')

    def text(self, x, y, value, size=9, font=F_BODY, color=NT.text, anchor='start', limit=None):
        width = pdfmetrics.stringWidth(value, font, size)
        if limit is not None:
            assert width <= limit, (value, width, limit)
        start = x if anchor == 'start' else x-width/2 if anchor == 'middle' else x-width
        assert 8 <= start and start+width <= W-8 and 12 <= y <= H-9, (value, start, width, y)
        self.drawing.add(String(start, H-y, value, fontName=font, fontSize=size, fillColor=color))
        self.svg.append(outline_text(value, font, size, start, y, color))
        self.texts.append({'text': value, 'font': font, 'size_pt': size, 'x': start, 'y': y, 'width_pt': width})

    def label(self, x, y, value, color=NT.accent, limit=None):
        self.text(x, y, value, 8, font=F_MONO, color=color, limit=limit)

    def header(self, number, category, title, subtitle, scope):
        self.label(24, 24, f'{number} / {category}')
        self.text(24, 58, title, 27, font=F_HEAD, color=NT.black, limit=456)
        self.text(24, 80, subtitle, 10.5, color=NT.muted, limit=456)
        self.text(24, 99, scope, 8.2, font=F_MONO, color=NT.muted, limit=456)
        self.line(24, 111, 480, 111)

    def save(self, out, canvas):
        renderPDF.draw(self.drawing, canvas, 0, 0)
        canvas.showPage()
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="504pt" height="648pt" viewBox="0 0 504 648" role="img" aria-labelledby="title desc">\n'
        svg += f'<title id="title">{escape(self.title)}</title>\n'
        svg += '<desc id="desc">nTop engineering skill map. Labels retain accessible text; TrueType lettering is outlined for consistent display.</desc>\n'
        svg += '\n'.join(self.svg) + '\n</svg>\n'
        (out / (self.name + '.svg')).write_text(svg, encoding='utf-8', newline='\n')
        return {'figure': self.name, 'width_pt': W, 'height_pt': H,
                'minimum_font_pt': min(t['size_pt'] for t in self.texts), 'text': self.texts}


def current_figure():
    f = Figure('current-engineering-skills', 'Current skills for nTop engineering experiments')
    f.header('01', 'CURRENT WORKFLOW', 'Engineering skill system',
             'Native models, notebook execution, analysis and evidence.',
             '18 NAMED SKILLS  /  INVENTORY: 16 SEP 2026')
    f.label(24, 131, 'AUTHOR AND MODEL')
    for x in (24, 180, 336):
        f.rect(x, 141, 144, 105)

    f.text(34, 161, 'ntop-notebook-api', 10.3, font=F_HEAD, color=NT.accent, limit=124)
    for y, value in [(179, 'Schemas, units and recipes'), (192, 'Native graph and controls'),
                     (205, 'Background command bridge'), (225, 'Rendering, AT + Sharpen'), (238, 'Saved-file organization')]:
        f.text(34, y, value, 8.7, limit=124)

    f.text(190, 161, 'ntop-csg-modeling', 10.3, font=F_HEAD, color=NT.accent, limit=124)
    f.text(190, 179, 'Primitives, cuts and fillets', 8.7, limit=124)
    f.text(190, 192, 'Source-fidelity verification', 8.7, limit=124)
    f.rect(186, 204, 132, 36, fill=NT.bg_hdr)
    f.text(192, 219, 'Lofting + two-rail sweeps', 8.5, font=F_HEAD, limit=120)
    f.text(192, 232, 'Conic / spline; chord / twist', 8.3, limit=120)

    f.text(346, 160, 'ntop-assembly-modeling', 9.3, font=F_HEAD, color=NT.accent, limit=124)
    f.text(346, 177, 'Part contracts and placements', 8.2, limit=124)
    f.text(346, 189, 'Shared families; import updates', 8.2, limit=124)
    f.line(346, 199, 470, 199, dash=[2, 2], color=NT.rule_lt)
    f.text(346, 216, 'ntop-custom-assembly', 9.3, font=F_HEAD, color=NT.accent, limit=124)
    f.text(346, 229, 'KestrelSAT-specific contracts', 8.2, limit=124)
    f.text(346, 241, 'and native example pilots', 8.2, limit=124)

    for x in (96, 252, 408):
        f.line(x, 246, x, 256)
    f.line(96, 256, 408, 256)
    f.arrow(252, 256, 252, 266)
    f.rect(24, 266, 456, 27, fill=NT.accent_soft)
    f.rect(24, 266, 2, 27, fill=NT.accent)
    f.text(252, 284, 'Editable notebooks, native geometry and measured parameters',
           10.6, font=F_HEAD, anchor='middle', limit=432)
    f.line(252, 293, 252, 304)
    f.line(135, 304, 369, 304)
    f.arrow(135, 304, 135, 316)
    f.arrow(369, 304, 369, 316)

    for x in (24, 258):
        f.rect(x, 316, 222, 141)
    f.label(34, 333, 'EXECUTE AND STUDY', limit=202)
    f.label(268, 333, 'MESH AND SOLVE', limit=202)
    left = [
        ('run-ntop-automate + ntop-automate', 'Prepared notebook runs with ntopcl'),
        ('ntop-doe-sweep', 'Reproducible parameter studies and retries'),
        ('ntop-orchestrate', 'Remote notebook jobs and result collection'),
        ('open-ntop-gui', 'Interactive review at a selected input set'),
    ]
    right = [
        ('AFLR3 Mesh Generator', 'Surface-to-volume boundary-layer meshing'),
        ('Fun3D CFD Runner + fun3d-gcp', 'FUN3D execution and refine adaptation'),
        ('ntop-nektar-cfd', 'High-order meshing, solves and field analysis'),
        ('run-lava', 'LAVA mesh routes, solves and postprocessing'),
    ]
    for x, rows in ((34, left), (268, right)):
        for index, (name, role) in enumerate(rows):
            y = 353 + index*25
            f.text(x, y, name, 9.3, font=F_HEAD, color=NT.accent, limit=202)
            f.text(x, y+12, role, 8.5, limit=202)
    f.line(135, 457, 135, 468)
    f.line(369, 457, 369, 468)
    f.line(135, 468, 369, 468)
    f.arrow(252, 468, 252, 480)

    f.rect(24, 480, 456, 57, fill=NT.bg_hdr)
    f.label(34, 495, 'ANALYSIS AND OPTIMIZATION METHODS', color=NT.text, limit=432)
    for y, value in [
        (508, 'Ski-A170: section / beam bending and torsion. Aircraft: FEA and buckling screens.'),
        (520, 'Jet20lbf: cycle matching and performance trades. Propellers: CFD study workflows.'),
        (532, 'Field analysis, mass / stiffness comparisons, sensitivity and geometry feedback.'),
    ]:
        f.text(34, y, value, 8.5, limit=432)
    f.line(24, 510, 12, 510)
    f.line(12, 510, 12, 190)
    f.arrow(12, 190, 24, 190)

    f.label(24, 551, 'POSTPROCESS AND REPORT')
    for x, name, line1, line2 in [
        (24, 'engineering-report', 'Scientific figures,', 'field plots and PDFs'),
        (141, 'ntop-docs-v1', 'Report structure', 'and evidence'),
        (258, 'ntop-design-v1', 'Visual design', 'and typography'),
        (375, 'ntop-writing-style', 'Factual technical', 'writing'),
    ]:
        f.rect(x, 561, 105, 47)
        f.text(x+8, 577, name, 8.5, font=F_HEAD, color=NT.accent, limit=89)
        f.text(x+8, 591, line1, 8.5, limit=89)
        f.text(x+8, 602, line2, 8.5, limit=89)
    f.line(24, 616, 480, 616)
    f.text(24, 628, 'Verification at every stage: source, graph, geometry, mesh, solver and result checks.', 8.3, font=F_HEAD, limit=456)
    f.text(24, 638, 'Blue names: skills. Grey panels: methods with case-specific evidence and limits.', 8, color=NT.muted, limit=456)
    return f


def future_figure():
    g = Figure('proposed-engineering-skills', 'Potential future engineering skills')
    g.header('02', 'PROPOSED EXTENSION', 'Future engineering skills',
             'Coordinated expertise around a shared aircraft design.',
             '10 PROPOSED BRIEFS  /  NOT INSTALLED OR VALIDATED')
    g.rect(24, 122, 456, 47, fill=NT.accent_soft)
    g.rect(24, 122, 2, 47, fill=NT.accent)
    g.text(36, 139, 'Shared aircraft design contract', 12, font=F_HEAD, limit=432)
    g.text(36, 152, 'Mission, geometry, interfaces, materials, loads, mass, units and coordinate frames.', 8.7, limit=432)
    g.text(36, 164, 'Every result retains assumptions, sources, revision identity and uncertainty.', 8.7, limit=432)
    g.line(252, 169, 252, 573, dash=[2, 3])
    cards = [
        ('George Irving configurator', ['Capture George-reviewed configuration rules.', 'Generate coordinated aircraft layouts.', 'Expose editable design choices and constraints.']),
        ('Expert airframing', ['Define spars, frames, ribs and longerons.', 'Coordinate joints and structural load paths.', 'Check access and removable skin panels.']),
        ('Propulsion and installation', ['Match engine or propulsor to the mission.', 'Model cycle, power and installed losses.', 'Coordinate inlets, exhausts and cooling.']),
        ('Weights and mass properties', ['Maintain component mass and growth ledgers.', 'Calculate CG, inertia and loading cases.', 'Track uncertainty and configuration changes.']),
        ('Stability and control (S&C)', ['Estimate derivatives, trim and static margins.', 'Assess modes and control authority.', 'Map limits across the flight / CG envelope.']),
        ('Loads and aeroelasticity', ['Build maneuver, gust and ground load cases.', 'Transfer distributed loads into the structure.', 'Screen stiffness coupling and flutter risk.']),
        ('Structural sizing and joints', ['Size members, fasteners and connections.', 'Check stress, buckling, fatigue and damage.', 'Retain allowables and failure-mode coverage.']),
        ('Aerodynamics and mission', ['Build polars and performance models.', 'Compare range, endurance and field performance.', 'Assess model fidelity and sensitivity.']),
        ('Manufacturing and assembly', ['Evaluate forming, machining and printing routes.', 'Define tolerances, tooling and assembly access.', 'Estimate process-driven mass, cost and risk.']),
        ('Verification and trade studies', ['Enforce shared constraints across disciplines.', 'Run benchmarks and uncertainty studies.', 'Rank candidates with traceable evidence.']),
    ]
    for index, (title, lines) in enumerate(cards):
        x = 24 if index % 2 == 0 else 260
        y = 181 + (index // 2)*87
        g.rect(x, y, 220, 76, stroke=NT.rule, dash=[3, 3])
        g.arrow(252, y+38, 244 if index % 2 == 0 else 260, y+38, dash=[2, 2])
        g.text(x+10, y+19, title, 10.5, font=F_HEAD, color=NT.accent, limit=200)
        for row, value in enumerate(lines):
            g.text(x+10, y+36+13*row, value, 8.7, limit=200)
    g.line(24, 617, 480, 617)
    g.text(24, 629, 'Reviewed results can update the shared design and drive new notebook variants.', 8.4, font=F_HEAD, limit=456)
    g.text(24, 639, 'Dashed boxes: proposals requiring bounded pilots, expert review and documented limits.', 8, color=NT.muted, limit=456)
    return g


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / '.local/skill-figures')
    parser.add_argument('--dpi', type=int, default=450)
    args = parser.parse_args()
    if args.dpi <= 0:
        parser.error('--dpi must be positive')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    pdf = out / 'ntop-engineering-skills.pdf'
    canvas = Canvas(str(pdf), pagesize=(W, H), invariant=1)
    canvas.setTitle('nTop engineering experiment skills: current and proposed')
    canvas.setAuthor('nTop engineering experiment workflow')
    figures = [current_figure(), future_figure()]
    records = [figure.save(out, canvas) for figure in figures]
    canvas.save()
    import pypdfium2 as pdfium
    with pdfium.PdfDocument(str(pdf)) as document:
        for index, figure in enumerate(figures):
            page = document[index]
            bitmap = page.render(scale=args.dpi/72)
            bitmap.to_pil().save(out/(figure.name+'.png'), dpi=(args.dpi, args.dpi))
            bitmap.close()
            page.close()
    receipt = {'design': 'ntop-design-v1 document grammar with blue report highlights',
               'fonts': {'body': F_BODY, 'heading': F_HEAD, 'labels': F_MONO},
               'dpi': args.dpi, 'figures': records}
    (out/'figure-layout-check.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'pages': 2, 'size_inches': [7, 9], 'dpi': args.dpi,
                      'fonts': receipt['fonts'], 'minimum_font_pt': min(r['minimum_font_pt'] for r in records)}))


if __name__ == '__main__':
    main()
