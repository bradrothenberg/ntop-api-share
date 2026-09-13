"""Organise a saved .ntop notebook into sections, hide intermediates, colour parts.

`import_recipe` puts every imported block into the first section and the
build-42594 Notebook API had no block movement or visibility setters.
Build 42926 adds move_block; this saved-file helper also controls visibility. The saved file does carry both, as data:

  MAGIC%$1 container
    table at byte 24: 16-byte chunk name + 8-byte END offset relative to
    the first chunk (byte 344), one entry per top-level chunk
    chunks: 'MAGIC@@9' + type(16) + name(16) + size(8) + pad to 128 + payload
      main (ntopfn)  -> fn (json): {"code":[blocks...]}; block 100 is the root
                        group whose `inputs` order is the tree order
                     -> leaves (obj_container): 8-byte count + chunks
      sections (json) {"decorations":[{name,...}], "poles":[0, n1, ..., N]}
                        consecutive index ranges over the root order
      open (json)     per tree node UI state, paths "100_<i>_..." by index
      view (json)     per body display state: visible, colour, ...

This tool reorders the root group's inputs by section, writes the poles,
remaps the `open` paths, hides every body except the final parts, and
colours those. The sections and colours come from _agent/engine_layout.json,
written by engine.make_recipe().

    uv run python scripts/organize_notebook.py I6_Engine.ntop -o I6_Engine_organized.ntop --layout demos/i6/output/_agent/engine_layout.json
    uv run python scripts/organize_notebook.py I6_Engine.ntop --roundtrip      # prove the writer is byte exact
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

MAGIC = b"MAGIC@@9"
HEADER = 128
FIRST_CHUNK = 344
TABLE_AT = 24


class Chunk:
    def __init__(self, typ, name, payload, children=None, prefix=b""):
        self.typ, self.name, self.payload, self.children, self.prefix = typ, name, payload, children, prefix

    def serialize(self) -> bytes:
        if self.children is not None:
            body = self.prefix + b"".join(c.serialize() for c in self.children)
        else:
            body = self.payload
        head = MAGIC + self.typ.encode().ljust(16, b"\0") + self.name.encode().ljust(16, b"\0") + struct.pack("<Q", len(body))
        return head.ljust(HEADER, b"\0") + body

    def find(self, name, typ=None):
        if self.name == name and (typ is None or self.typ == typ):
            return self
        for c in self.children or []:
            r = c.find(name, typ)
            if r is not None:
                return r
        return None


def parse_chunks(buf: bytes, start: int, end: int) -> list[Chunk]:
    out = []
    pos = start
    while pos < end:
        assert buf[pos:pos + 8] == MAGIC, "no chunk marker at %d" % pos
        typ = buf[pos + 8:pos + 24].rstrip(b"\0").decode()
        name = buf[pos + 24:pos + 40].rstrip(b"\0").decode()
        size = struct.unpack("<Q", buf[pos + 40:pos + 48])[0]
        p0, p1 = pos + HEADER, pos + HEADER + size
        if typ == "ntopfn":
            out.append(Chunk(typ, name, None, parse_chunks(buf, p0, p1)))
        elif typ == "obj_container":
            prefix = buf[p0:p0 + 8]
            out.append(Chunk(typ, name, None, parse_chunks(buf, p0 + 8, p1), prefix))
        else:
            out.append(Chunk(typ, name, buf[p0:p1]))
        pos = p1
    return out


def read_file(path: Path):
    raw = path.read_bytes()
    assert raw[:9] == b"MAGIC%$1\n", "not an nTop container"
    header = bytearray(raw[:FIRST_CHUNK])
    chunks = parse_chunks(raw, FIRST_CHUNK, len(raw))
    return header, chunks


def write_file(header: bytearray, chunks: list[Chunk]) -> bytes:
    body = b""
    ends = {}
    for c in chunks:
        body += c.serialize()
        ends[c.name] = len(body)
    pos = TABLE_AT
    while True:
        name = bytes(header[pos:pos + 16]).rstrip(b"\0").decode()
        if not name:
            break
        header[pos + 16:pos + 24] = struct.pack("<Q", ends[name])
        pos += 24
    return bytes(header) + body


def organize(chunks: list[Chunk], layout: dict, hide: bool, report: dict, translucent: dict | None = None):
    fn = next(c for c in chunks if c.name == "main").find("fn", "json")
    code = json.loads(fn.payload.decode("utf-8"))
    blocks = code["code"]
    byid = {b["id"]: b for b in blocks}
    root = byid[100]
    order = [inp["instanceId"] for inp in root["inputs"]]
    names = {i: byid[i]["name"] for i in order}

    sections = list(layout["sections"])
    assign = layout["variables"]
    final = layout["final_bodies"]

    def section_of(name):
        if name in assign:
            return assign[name]
        if name.startswith("CHECK "):
            return "CHECKS"
        return "OTHER"

    groups = {s: [] for s in sections}
    groups["OTHER"] = []
    for i in order:
        groups[section_of(names[i])].append(i)
    if groups["OTHER"]:
        sections.append("OTHER")
        report["unassigned"] = [names[i] for i in groups["OTHER"]][:20]
    sections = [s for s in sections if groups[s]]
    new_order = [i for s in sections for i in groups[s]]
    assert sorted(new_order) == sorted(order)
    old_index = {i: k for k, i in enumerate(order)}
    new_index = {i: k for k, i in enumerate(new_order)}
    remap = {old_index[i]: new_index[i] for i in order}
    root["inputs"] = [root["inputs"][old_index[i]] for i in new_order]
    fn.payload = json.dumps(code, separators=(",", ":")).encode("utf-8")

    poles, n = [0], 0
    for s in sections:
        n += len(groups[s])
        poles.append(n)
    sec = next(c for c in chunks if c.name == "sections")
    sec.payload = json.dumps({"decorations": [{"collapse": False, "description": "", "name": s} for s in sections],
                              "poles": poles}, separators=(",", ":")).encode()
    report["sections"] = {s: len(groups[s]) for s in sections}

    op = next(c for c in chunks if c.name == "open")
    entries = json.loads(op.payload.decode("utf-8"))
    for e in entries:
        parts = e["relativePath"].split("_")
        if len(parts) >= 2 and parts[0] == "100" and parts[1].isdigit():
            parts[1] = str(remap[int(parts[1])])
            e["relativePath"] = "_".join(parts)
    op.payload = json.dumps(entries, separators=(",", ":")).encode()

    view = next(c for c in chunks if c.name == "view")
    ventries = json.loads(view.payload.decode("utf-8"))
    top_ids = set(order)
    shown, coloured, missing = [], [], []
    have_view = {v["id"] for v in ventries}
    for v in ventries:
        name = names.get(v["id"])
        is_final = name in final
        if hide:
            v["visible"] = bool(is_final)
        if is_final:
            shown.append(name)
            for a in v["attributes"]:
                if a["name"] == "color":
                    a["value"] = list(final[name])
                    coloured.append(name)
            if translucent and name in translucent:
                # `transparent` + `opacity` are the top-level fields the viewer
                # reads; the attribute pair mirrors them in the properties panel.
                v["transparent"] = True
                v["opacity"] = float(translucent[name])
                for a in v["attributes"]:
                    if a["name"] == "transparency":
                        a["value"] = 1
                    if a["name"] == "opacity":
                        a["value"] = int(round(translucent[name] * 100))
    for name in final:
        fid = next((i for i in order if names[i] == name), None)
        if fid is None:
            missing.append(name + " (no block)")
        elif fid not in have_view:
            missing.append(name + " (no view entry)")
    view.payload = json.dumps(ventries, separators=(",", ":")).encode()
    report["view_entries"] = len(ventries)
    report["view_entries_on_top_level"] = sum(1 for v in ventries if v["id"] in top_ids)
    report["final_shown"] = len(shown)
    report["final_coloured"] = len(coloured)
    report["final_missing"] = missing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("notebook", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    ap.add_argument("--layout", type=Path, default=Path(__file__).resolve().parents[1] / "_agent" / "engine_layout.json")
    ap.add_argument("--roundtrip", action="store_true", help="re-serialise unchanged and compare bytes")
    ap.add_argument("--keep-visibility", action="store_true", help="do not hide intermediate bodies")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--translucent", type=float, default=None,
                    help="opacity (0-1) for the static parts: block, head, bedplate, pan")
    args = ap.parse_args()

    header, chunks = read_file(args.notebook)
    if args.roundtrip:
        out = write_file(bytearray(header), chunks)
        raw = args.notebook.read_bytes()
        same = out == raw
        print("roundtrip identical:", same, "| in", len(raw), "out", len(out))
        if not same:
            k = next(i for i in range(min(len(raw), len(out))) if raw[i] != out[i])
            print("first difference at", k, raw[k:k + 40], out[k:k + 40])
        return 0 if same else 1

    layout = json.loads(args.layout.read_text(encoding="utf-8"))
    report = {}
    trans = None
    if args.translucent is not None:
        trans = {n: args.translucent for n in ("Cylinder Block", "Cylinder Head", "Bedplate", "Oil Pan")}
    organize(chunks, layout, hide=not args.keep_visibility, report=report, translucent=trans)
    print(json.dumps(report, indent=1))
    if args.dry_run:
        return 0
    out = args.out or args.notebook
    data = write_file(header, chunks)
    if out.resolve() == args.notebook.resolve():
        backup = args.notebook.with_suffix(".bak.ntop")
        backup.write_bytes(args.notebook.read_bytes())
        print("backup:", backup)
    out.write_bytes(data)
    print("wrote", out, len(data), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
