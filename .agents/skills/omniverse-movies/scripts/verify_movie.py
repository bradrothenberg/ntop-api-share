"""Decode a movie and check its expected frame contract. Uses FFmpeg and stdlib.

Run with uv run. Use --help for required inputs. This does not validate visual
quality, source geometry, simulation results, or audio.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def decode(path,stem,args):
    md5=stem.parent/(stem.name+'.frames.md5')
    log=stem.parent/(stem.name+'.decode.log')
    before=digest(path)
    cmd=[str(args.ffmpeg),'-y','-nostdin','-hide_banner','-xerror',
         '-threads','2','-i',str(path),'-map','0:v:0','-vsync','0',
         '-f','framemd5',str(md5)]
    with log.open('w',encoding='utf-8') as err:
        subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=err,
                       check=True,timeout=args.timeout)
    if digest(path)!=before:
        raise ValueError('The source movie changed during verification')
    tb=None;dimensions=None;frames=[]
    for line in md5.read_text(encoding='utf-8').splitlines():
        if line.startswith('#tb 0:'):
            tb=Fraction(line.split(':',1)[1].strip())
        elif line.startswith('#dimensions 0:'):
            dimensions=tuple(map(int,re.findall(r'\d+',line.split(':',1)[1])))
        elif line and not line.startswith('#'):
            fields=[s.strip() for s in line.split(',')]
            if int(fields[0])!=0:
                raise ValueError('Unexpected extra video stream')
            frames.append((int(fields[2]),fields[-1]))
    if len(frames)!=args.frames:
        raise ValueError(f'Expected {args.frames} frames, decoded {len(frames)}')
    if dimensions!=(args.width,args.height):
        raise ValueError(f'Unexpected dimensions: {dimensions}')
    if tb is None:
        raise ValueError('FFmpeg did not report the decoded time base')
    for i,(pts,_) in enumerate(frames):
        if pts*tb!=Fraction(i,1)/args.fps:
            raise ValueError(f'Unexpected presentation timestamp at frame {i}')
    return dict(sha256=before,bytes=path.stat().st_size,
                hashes=[h for _,h in frames],framemd5=str(md5),log=str(log))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('movie',type=Path)
    p.add_argument('--ffmpeg',type=Path,required=True)
    p.add_argument('--fps',type=Fraction,required=True,help='For example 60 or 30000/1001')
    p.add_argument('--frames',type=int,required=True)
    p.add_argument('--width',type=int,required=True)
    p.add_argument('--height',type=int,required=True)
    p.add_argument('--report',type=Path,required=True,help='Output JSON audit path')
    p.add_argument('--reference',type=Path)
    p.add_argument('--unchanged-from-frame',type=int)
    p.add_argument('--timeout',type=int,default=600,help='Maximum seconds per full decode')
    args=p.parse_args()
    if min(args.fps,args.frames,args.width,args.height,args.timeout)<=0:
        p.error('FPS, dimensions, frame count, and timeout must be positive')
    if bool(args.reference)!=(args.unchanged_from_frame is not None):
        p.error('--reference and --unchanged-from-frame must be provided together')
    if args.reference and not 0<=args.unchanged_from_frame<args.frames:
        p.error('The unchanged interval must begin inside the movie')
    args.movie=args.movie.resolve();args.ffmpeg=args.ffmpeg.resolve()
    args.report=args.report.resolve()
    if args.reference:args.reference=args.reference.resolve()
    if args.report.suffix.lower()!='.json':p.error('--report must be a JSON path')
    inputs=[args.movie,args.ffmpeg]+([args.reference] if args.reference else [])
    if not all(path.is_file() for path in inputs):p.error('An input file does not exist')
    destinations=[args.report]+[args.report.with_name(args.report.stem+suffix+ext)
                               for suffix in ['-movie','-reference']
                               for ext in ['.frames.md5','.decode.log']]
    if any(path in inputs for path in destinations):p.error('An audit path would overwrite an input')
    args.report.parent.mkdir(parents=True,exist_ok=True)
    report=dict(passed=False,file=str(args.movie),fps=str(args.fps),
                frames=args.frames,resolution=[args.width,args.height],
                duration_seconds=float(Fraction(args.frames,1)/args.fps),
                scope='Decode, frame clock, file hash, and optional unchanged-tail comparison only.')
    try:
        actual=decode(args.movie,args.report.with_name(args.report.stem+'-movie'),args)
        report.update({k:v for k,v in actual.items() if k!='hashes'})
        if args.reference:
            reference=decode(args.reference,args.report.with_name(args.report.stem+'-reference'),args)
            first=args.unchanged_from_frame
            if actual['hashes'][first:]!=reference['hashes'][first:]:
                mismatch=next(i for i in range(first,args.frames)
                              if actual['hashes'][i]!=reference['hashes'][i])
                raise ValueError(f'Unchanged section differs at frame {mismatch}')
            report['unchanged_tail']=dict(reference=str(args.reference),
                reference_sha256=reference['sha256'],from_frame=first,
                compared_frames=args.frames-first,pixel_identical=True)
        report['passed']=True
    except (ValueError,OSError,subprocess.SubprocessError) as error:
        report['error']=str(error)
    args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    sys.exit(main())
