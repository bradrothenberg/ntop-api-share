"""Create current and proposed engineering skill maps as vector artwork."""
from pathlib import Path
import json
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.graphics import renderPDF, renderSVG
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor, Color

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, default=Path('.local/skill-figures'))
parser.add_argument('--dpi', type=int, default=450)
args = parser.parse_args()
if args.dpi <= 0:
    parser.error('--dpi must be positive')
OUT = args.out.resolve()
OUT.mkdir(parents=True, exist_ok=True)
W,H=504,648
INK=HexColor('#20252b'); MUTED=HexColor('#49525d'); RULE=HexColor('#8995a1')
BLUE=HexColor('#16489d'); PALE=HexColor('#f1f4f7'); BLUE_PALE=HexColor('#edf2fb')
WHITE=Color(1,1,1)
records=[]

class Figure:
    def __init__(self,name):
        self.name=name; self.d=Drawing(W,H); self.texts=[]
        self.rect(0,0,W,H,fill=WHITE,stroke=None)
    def text(self,x,y,s,size=9,bold=False,color=INK,anchor='start',limit=None):
        font='Helvetica-Bold' if bold else 'Helvetica'
        width=stringWidth(s,font,size)
        if limit is not None: assert width<=limit,(s,width,limit)
        start=x if anchor=='start' else x-width/2 if anchor=='middle' else x-width
        assert start>=0 and start+width<=W and 0<y<H,s
        self.d.add(String(x,H-y,s,fontName=font,fontSize=size,fillColor=color,textAnchor=anchor))
        self.texts.append({'text':s,'size_pt':size,'x':x,'y':y,'width':width})
    def rect(self,x,y,w,h,fill=WHITE,stroke=RULE,dash=None):
        self.d.add(Rect(x,H-y-h,w,h,fillColor=fill,strokeColor=stroke,strokeWidth=.7,strokeDashArray=dash))
    def line(self,x1,y1,x2,y2,color=MUTED,dash=None):
        self.d.add(Line(x1,H-y1,x2,H-y2,strokeColor=color,strokeWidth=.7,strokeDashArray=dash))
    def arrow(self,x1,y1,x2,y2,color=MUTED,dash=None):
        import math
        self.line(x1,y1,x2,y2,color,dash)
        a=math.atan2(y2-y1,x2-x1); p=[x2,H-y2]
        for da in (-.5,.5):p.extend([x2-4*math.cos(a+da),H-(y2-4*math.sin(a+da))])
        self.d.add(Polygon(p,fillColor=color,strokeColor=None))
    def label(self,x,y,s):self.text(x,y,s,8.7,True,BLUE)
    def save(self,canvas):
        renderSVG.drawToFile(self.d,str(OUT/(self.name+'.svg')))
        renderPDF.draw(self.d,canvas,0,0);canvas.showPage()
        records.append({'figure':self.name,'width_pt':W,'height_pt':H,'minimum_font_pt':min(t['size_pt'] for t in self.texts),'text':self.texts})

f=Figure('current-engineering-skills')
f.text(20,24,'Current skills for nTop engineering experiments',13.3,True)
f.text(20,42,'18 named skills, with lofting and project analysis methods shown explicitly.',9.0,color=MUTED)
f.label(20,64,'AUTHORING AND MODELING')
for x in (20,178,336):f.rect(x,74,148,117)
f.text(29,91,'ntop-notebook-api',9.7,True,BLUE,limit=130)
for i,s in enumerate(['Schemas, units and recipes','Native graph and controls','Background command bridge']):f.text(29,109+13*i,s,8.6,limit=130)
f.text(29,157,'Included methods',8.4,True,color=MUTED)
f.text(29,170,'Rendering, AT + Sharpen,',8.5,limit=130)
f.text(29,182,'saved-file organization',8.5,limit=130)

f.text(187,91,'ntop-csg-modeling',9.6,True,BLUE,limit=130)
f.text(187,108,'Primitives, cuts and fillets',8.7,limit=130)
f.text(187,121,'Source-fidelity verification',8.7,limit=130)
f.rect(184,133,136,51,fill=PALE,stroke=None)
f.text(190,148,'Lofting and two-rail sweeps',8.7,True,limit=124)
f.text(190,162,'Guide-driven conic / spline',8.4,limit=124)
f.text(190,175,'surfaces; blade chord / twist',8.4,limit=124)

f.text(345,91,'ntop-assembly-modeling',8.8,True,BLUE,limit=130)
f.text(345,109,'Part contracts and placements',8.6,limit=130)
f.text(345,122,'Shared families; import updates',8.6,limit=130)
f.line(345,134,474,134,dash=[3,2])
f.text(345,151,'ntop-custom-assembly',9,True,BLUE,limit=130)
f.text(345,168,'KestrelSAT-specific contracts',8.6,limit=130)
f.text(345,181,'and native example pilots',8.6,limit=130)

f.line(20,202,484,202);f.arrow(252,202,252,215)
f.rect(20,215,464,31,fill=BLUE_PALE,stroke=BLUE)
f.text(252,235,'Editable notebooks, native geometry and measured parameter sets',10.1,True,anchor='middle')
f.line(252,246,252,255);f.line(136,255,368,255)
f.arrow(136,255,136,268);f.arrow(368,255,368,268)

f.rect(20,268,225,144);f.rect(259,268,225,144)
f.label(30,284,'NOTEBOOK EXECUTION AND STUDIES')
f.label(269,284,'MESHING AND CFD')
left=[
('run-ntop-automate + ntop-automate','Prepared notebook runs with ntopcl'),
('ntop-doe-sweep','Reproducible parameter studies and retries'),
('ntop-orchestrate','Remote notebook jobs and result collection'),
('open-ntop-gui','Interactive review at a selected input set')]
for i,(name,role) in enumerate(left):
    y=302+i*27
    f.text(30,y,name,8.9,True,BLUE,limit=205);f.text(30,y+12,role,8.5,limit=205)
right=[
('AFLR3 Mesh Generator','Surface-to-volume boundary-layer meshing'),
('Fun3D CFD Runner + fun3d-gcp','FUN3D execution and refine adaptation'),
('ntop-nektar-cfd','High-order meshing, solves and field analysis'),
('run-lava','LAVA mesh routes, solves and postprocessing')]
for i,(name,role) in enumerate(right):
    y=302+i*27
    f.text(269,y,name,8.9,True,BLUE,limit=205);f.text(269,y+12,role,8.5,limit=205)

f.line(136,412,136,420);f.line(368,412,368,420);f.line(136,420,368,420);f.arrow(252,420,252,430)
f.rect(20,430,464,78,fill=PALE)
f.text(30,447,'ANALYSIS AND OPTIMIZATION METHODS',8.7,True)
f.text(474,447,'Project scripts and references',8.2,color=MUTED,anchor='end')
f.text(30,463,'Ski-A170: section / beam bending and torsion. Aircraft: FEA and buckling screens.',8.6,limit=444)
f.text(30,477,'Jet20lbf: cycle matching and performance trades. Propellers: CFD study workflows.',8.6,limit=444)
f.text(30,491,'Field analysis, mass / stiffness comparisons, sensitivity and geometry feedback.',8.6,limit=444)
f.text(30,502,'Project methods retain their own assumptions, model fidelity, validation records and limits.',8.1,color=MUTED,limit=444)

f.arrow(252,508,252,522)
f.label(20,536,'POSTPROCESSING AND REPORTING')
for x in (20,138,256,374):f.rect(x,545,110,53)
for x,name,l1,l2 in [
    (20,'engineering-report','Scientific figures,','field plots and PDFs'),
    (138,'ntop-docs-v1','Report structure','and evidence'),
    (256,'ntop-design-v1','Visual design','and typography'),
    (374,'ntop-writing-style','Factual technical','writing')]:
    f.text(x+7,560,name,8.8,True,BLUE,limit=96)
    f.text(x+7,577,l1,8.7,limit=96);f.text(x+7,590,l2,8.7,limit=96)
f.line(20,610,484,610)
f.text(252,625,'Verification at every stage: source, graph, geometry, mesh, solver and result checks.',8.7,True,anchor='middle')
f.text(252,638,'Blue names identify skills. Gray method panels identify supporting guidance and project implementations.',8.0,color=MUTED,anchor='middle')
# Explicit return path for verified geometry and analysis changes.
f.line(20,472,8,472);f.line(8,472,8,121);f.arrow(8,121,20,121)

g=Figure('proposed-engineering-skills')
g.text(20,24,'Potential future engineering skills',14,True)
g.text(20,42,'Ten proposed skill briefs. These are not installed or validated capabilities.',9.4,color=MUTED)
g.rect(20,61,464,56,fill=BLUE_PALE,stroke=BLUE)
g.text(252,79,'Shared aircraft design contract',11,True,anchor='middle')
g.text(252,95,'Mission, geometry, interfaces, materials, loads, mass, units and coordinate frames',9,anchor='middle')
g.text(252,108,'Every result retains assumptions, sources, revision identity and uncertainty.',9,anchor='middle')
g.line(252,117,252,565,dash=[3,2])
cards=[
('George Irving configurator',['Capture George-reviewed configuration rules.','Generate coordinated aircraft layouts.','Expose editable design choices and constraints.']),
('Expert airframing',['Define spars, frames, ribs and longerons.','Coordinate joints and structural load paths.','Check access and removable skin panels.']),
('Propulsion and installation',['Match engine or propulsor to the mission.','Model cycle, power and installed losses.','Coordinate inlets, exhausts and cooling.']),
('Weights and mass properties',['Maintain component mass and growth ledgers.','Calculate CG, inertia and loading cases.','Track uncertainty and configuration changes.']),
('Stability and control (S&C)',['Estimate derivatives, trim and static margins.','Assess modes and control authority.','Map limits across the flight / CG envelope.']),
('Loads and aeroelasticity',['Build maneuver, gust and ground load cases.','Transfer distributed loads into the structure.','Screen stiffness coupling and flutter risk.']),
('Structural sizing and joints',['Size members, fasteners and connections.','Check stress, buckling, fatigue and damage.','Retain allowables and failure-mode coverage.']),
('Aerodynamics and mission',['Build polars and performance models.','Compare range, endurance and field performance.','Assess model fidelity and sensitivity.']),
('Manufacturing and assembly',['Evaluate forming, machining and printing routes.','Define tolerances, tooling and assembly access.','Estimate process-driven mass, cost and risk.']),
('Verification and trade studies',['Enforce shared constraints across disciplines.','Run benchmarks and uncertainty studies.','Rank candidates with traceable evidence.'])]
for i,(title,lines) in enumerate(cards):
    col=i%2;row=i//2;x=20 if col==0 else 264;y=137+89*row
    g.rect(x,y,220,77,fill=WHITE,stroke=RULE,dash=[3,2])
    g.arrow(252,y+38,240 if col==0 else 264,y+38,dash=[3,2])
    g.text(x+10,y+18,title,10,True,BLUE,limit=200)
    for k,s in enumerate(lines):g.text(x+10,y+35+k*14,s,8.7,limit=200)
g.rect(20,590,464,37,fill=PALE,stroke=None)
g.text(252,606,'Reviewed results update the shared design and can drive new notebook variants.',8.9,True,anchor='middle')
g.text(252,620,'Each future skill needs bounded pilots, independent checks and documented operating limits.',8.6,anchor='middle')
g.text(20,641,'Dashed boxes and links indicate proposals. Detailed inputs, outputs and validation gates accompany the figure.',8.0,color=MUTED)

canvas=Canvas(str(OUT/'ntop-engineering-skills.pdf'),pagesize=(W,H))
canvas.setTitle('nTop engineering experiment skills: current and proposed')
canvas.setAuthor('nTop engineering experiment workflow')
f.save(canvas);g.save(canvas);canvas.save()
(OUT/'figure-layout-check.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Created two vector figures and one two-page PDF, each 7 by 9 inches.')

# Raster companions use the same vector PDF at the selected resolution (450 dpi by default).
import pypdfium2 as pdfium
with pdfium.PdfDocument(str(OUT / 'ntop-engineering-skills.pdf')) as document:
    for index, name in enumerate(('current-engineering-skills', 'proposed-engineering-skills')):
        page = document[index]
        bitmap = page.render(scale=args.dpi / 72)
        bitmap.to_pil().save(OUT / (name + '.png'), dpi=(args.dpi, args.dpi))
        bitmap.close()
        page.close()
