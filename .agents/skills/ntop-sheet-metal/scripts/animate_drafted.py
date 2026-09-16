"""Draft revision: native final meshes, conservative translucent release envelopes."""
import argparse
from pathlib import Path
from PIL import ImageDraw
import animate_with_tools as tools
import animate_advanced as anim
from release_tools import tool_shells
from build_drafted_sheet_metal import KEYS
original_decorate=anim.decorate
def decorate(render,key,p,phase,tooling=False):
    im=original_decorate(render,key,p,phase,tooling=True);d=ImageDraw.Draw(im)
    d.rectangle((38,90,930,115),fill=anim.BG)
    label='30-degree corrugation walls' if key=='corrugated_shield' else '3-degree drafted walls'
    d.text((39,94),label+' / release envelopes with >= 0.5 mm separation',font=anim.font(15),fill='#506579')
    d.rectangle((38,666,955,714),fill=anim.BG)
    d.text((38,667),'Illustrative forming / translucent release envelopes / no material solver',font=anim.font(16),fill='#425c73')
    d.text((38,691),'Final-state release clearance checked; forming contact and tool access not qualified.',font=anim.font(13),fill='#425c73')
    if phase in ['retract','hold']:
        d.rectangle((40,586,650,614),fill='white')
        d.text((55,588),'NATIVE PART / TOOLS RELEASING',font=anim.font(17,True),fill=anim.INK)
    return im
anim.decorate=decorate
tools.tool_shells=tool_shells
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path.cwd()/'.local'/'sheet-metal-study'/'drafted');p.add_argument('--case',default='all');p.add_argument('--preview',action='store_true');args=p.parse_args()
    for key in KEYS if args.case=='all' else args.case.split(','):tools.make(args.root.resolve(),key,args.preview)
