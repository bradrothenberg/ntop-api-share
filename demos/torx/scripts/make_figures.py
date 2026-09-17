"""Turn the native slice archives into report figures, and measure them.

A picture is only evidence once its axes are known. Three facts about the
slicer's mapping, each measured on build 42926 rather than assumed:

  - THE FIRST PLANE SITS AT THE PRINT-VOLUME MINIMUM, not half a layer above
    it. The plane of slice k is BOX0 + (k-1) h. This was pinned by the
    `calibration` stack: five micrometre layers across the recess floor, a
    plane the mirror puts at exactly -1.7300 mm. The recess closes between
    k = 13 and k = 14, which brackets the floor at [-1.7300, -1.7250] under
    this law and at [-1.7275, -1.7225] under the half-layer law. The true value
    sits on the edge of the first bracket and outside the second. A half-layer
    offset is 2.5 micrometres here, which is 25 times the boundary gate, so the
    difference is not a rounding question. Recorded 6.0.3 behaviour was the
    half-layer form; this build is not that, and the archive is read with the
    law measured on the build in hand.
  - the stack does NOT stop at the print-volume ceiling. It continues until the
    body's own bounding box is exhausted, so the archive holds more images than
    layers were asked for, and an index is converted to a coordinate rather than
    divided into the stack.
  - image columns run along the frame's FIRST vector from the box MIN corner,
    and image rows run along the NEGATIVE of the frame's second vector, from the
    box MAX corner.

A plane lying exactly on a boundary surface rasterises as open, not solid.

This script applies that mapping and then checks it against features the mirror
knows independently: the head outer radius, and the recess contour radius at six
angles. If a check fails the mapping is reported as wrong rather than quietly
adjusted.

Run: `uv run --group render python demos/torx/scripts/make_figures.py`. Needs
Pillow; needs no nTop.
"""

import json
import math
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

import torx_spec as spec
from torx_verification import FIGURES

DEMO = Path(__file__).resolve().parents[1]
SOURCE = DEMO / "output" / "report_figures"
ASSETS = DEMO / "reports" / "assets"
MM = 1e-3

# Which plane of each stack to publish, as a target coordinate in mm.
PLANES = {
    "recess": [("mouth", -2.95, "the recess mouth, just inside the head top face"),
               ("wall", -2.35, "mid recess: the six lobes and six valleys"),
               ("web", -1.55, "below the recess floor: solid head metal"),
               ("thread", 5.45, "a thread crest, one turn inside the threaded length")],
    "profile": [("axis", 0.0, "the axial section through the screw axis")],
}


def plane_coordinate(figure, index):
    """The coordinate of slice `index` (1-based), from the MEASURED index law.

    BOX0 + (k-1) h. See the module docstring for how the offset was pinned; the
    half-layer form recorded on an earlier build does not hold here.
    """
    axis = "xyz".index(figure["axis"])
    lo = figure["box_mm"][0][axis]
    return lo + (index - 1) * figure["layer_mm"]


def pixel_axes(figure, size):
    """(column_to_mm, row_to_mm) for one image, from the measured mapping."""
    lo, hi = figure["box_mm"]
    width, height = size
    if figure["axis"] == "z":           # frame first (1,0,0), second (0,1,0)
        col_lo, col_hi, row_lo, row_hi = lo[0], hi[0], lo[1], hi[1]
        col_axis, row_axis = "x", "y"
    else:                               # frame first (0,0,1), second (1,0,0)
        col_lo, col_hi, row_lo, row_hi = lo[2], hi[2], lo[0], hi[0]
        col_axis, row_axis = "z", "x"
    dcol = (col_hi - col_lo) / width
    drow = (row_hi - row_lo) / height
    return {"col_axis": col_axis, "row_axis": row_axis,
            "col": lambda c: col_lo + (c + 0.5) * dcol,
            "row": lambda r: row_hi - (r + 0.5) * drow,
            "dcol": dcol, "drow": drow,
            "col_of": lambda v: (v - col_lo) / dcol - 0.5,
            "row_of": lambda v: (row_hi - v) / drow - 0.5}


def load_stack(figure):
    path = SOURCE / ("torx_%s.zip" % figure["name"])
    with zipfile.ZipFile(path) as archive:
        names = sorted(archive.namelist(),
                       key=lambda n: int("".join(ch for ch in n if ch.isdigit()) or 0))
        images = {}
        for name in names:
            index = int("".join(ch for ch in name if ch.isdigit()))
            with archive.open(name) as fh:
                images[index] = Image.open(fh).convert("L").copy()
    return images, path


def solid_mask(image):
    """Solid is white in a black-and-white slice image."""
    return image.point(lambda v: 255 if v > 127 else 0)


def measure_recess(image, axes, cfg):
    """Radius of the recess boundary at six angles, read off the raster.

    The recess is the black region around the axis. Walking outwards from the
    centre along one angle, the first solid pixel marks the wall.
    """
    out = []
    transition = spec.contour_transition_angle(cfg.recess_radius * 2,
                                               cfg.recess_inner * 2, cfg.lobe_radius)
    pixels = solid_mask(image).load()
    width, height = image.size
    step = min(abs(axes["dcol"]), abs(axes["drow"])) / 4.0
    for name, theta in (("lobe", 0.0), ("junction", transition),
                        ("valley", math.pi / 6), ("lobe 60", math.pi / 3),
                        ("valley 90", math.pi / 2), ("lobe 120", 2 * math.pi / 3)):
        r = 0.0
        found = None
        while r < cfg.head_radius:
            x, y = r * math.cos(theta), r * math.sin(theta)
            c, rw = axes["col_of"](x), axes["row_of"](y)
            ci, ri = int(round(c)), int(round(rw))
            if 0 <= ci < width and 0 <= ri < height and pixels[ci, ri] > 127:
                found = r
                break
            r += step
        expected = cfg.contour(theta)
        out.append({"angle_deg": theta * 180 / math.pi, "feature": name,
                    "measured_mm": found, "expected_mm": expected,
                    "delta_mm": None if found is None else found - expected,
                    "pixel_mm": min(abs(axes["dcol"]), abs(axes["drow"]))})
    return out


def measure_head_radius(image, axes, cfg):
    """Outer radius of the head, read along +X and -X."""
    pixels = solid_mask(image).load()
    width, height = image.size
    step = min(abs(axes["dcol"]), abs(axes["drow"])) / 4.0
    out = []
    for name, sign in (("+X", 1.0), ("-X", -1.0)):
        r, last = 0.0, None
        while r < cfg.head_radius * 1.2:
            c, rw = axes["col_of"](sign * r), axes["row_of"](0.0)
            ci, ri = int(round(c)), int(round(rw))
            if 0 <= ci < width and 0 <= ri < height and pixels[ci, ri] > 127:
                last = r
            r += step
        out.append({"direction": name, "measured_mm": last,
                    "expected_mm": cfg.head_radius,
                    "delta_mm": None if last is None else last - cfg.head_radius,
                    "note": "the print volume is clipped 1 micrometre inside the head "
                            "radius, so the measured value is bounded by 2.749 mm"})
    return out


def publish(image, name, scale=1):
    ASSETS.mkdir(parents=True, exist_ok=True)
    out = image
    if scale != 1:
        out = image.resize((image.width * scale, image.height * scale), Image.NEAREST)
    path = ASSETS / ("%s.png" % name)
    out.save(path, optimize=True)
    return {"asset": "assets/%s.png" % name, "bytes": path.stat().st_size,
            "px": [out.width, out.height]}


def calibrate(figure, cfg):
    """Pin the slicer's first-plane offset against a plane the mirror knows.

    Returns the bracket each candidate law puts the known plane in, and which
    law survives. This is the measurement, not an assumption carried over.
    """
    images, _ = load_stack(figure)
    known = figure["known_plane_mm"]
    h = figure["layer_mm"]
    lo = figure["box_mm"][0]["xyz".index(figure["axis"])]
    solid = {}
    for index, image in images.items():
        pixels = solid_mask(image).load()
        width, height = image.size
        solid[index] = pixels[width // 2, height // 2] > 127
    keys = sorted(solid)
    closes = next((k for k in keys[1:] if solid[k] and not solid[k - 1]), None)
    laws = {}
    for name, offset in (("BOX0 + (k-1)h", 0.0), ("BOX0 + h/2 + (k-1)h", h / 2)):
        if closes is None:
            laws[name] = None
            continue
        low = lo + offset + (closes - 2) * h
        high = lo + offset + (closes - 1) * h
        laws[name] = {"bracket_mm": [round(low, 6), round(high, 6)],
                      "contains_known_plane": low - 1e-9 <= known <= high + 1e-9}
    return {"stack": figure["name"], "images": len(images),
            "layer_mm": h, "known_plane_mm": known,
            "closes_between": [closes - 1, closes] if closes else None,
            "laws": laws,
            "law_used": "BOX0 + (k-1)h",
            "note": "a plane lying exactly on a boundary surface rasterises as open"}


def main():
    cfg = spec.Configuration()
    report = {"planes": [], "measurements": {}}
    for figure in FIGURES:
        if figure.get("known_plane_mm") is not None:
            report["calibration"] = calibrate(figure, cfg)
        if figure.get("publish") is False:
            continue
        images, archive = load_stack(figure)
        report.setdefault("stacks", []).append(
            {"name": figure["name"], "axis": figure["axis"],
             "archive": archive.name, "images": len(images),
             "layers_requested": round((figure["box_mm"][1]["xyz".index(figure["axis"])]
                                        - figure["box_mm"][0]["xyz".index(figure["axis"])])
                                       / figure["layer_mm"]),
             "note": "the stack continues past the print-volume ceiling until the "
                     "body's own bounds are exhausted",
             "first_plane_mm": plane_coordinate(figure, 1),
             "last_plane_mm": plane_coordinate(figure, max(images))})
        size = next(iter(images.values())).size
        axes = pixel_axes(figure, size)
        for label, target, caption in PLANES[figure["name"]]:
            index = min(images, key=lambda k: abs(plane_coordinate(figure, k) - target))
            coordinate = plane_coordinate(figure, index)
            image = images[index]
            asset = publish(image, "torx_%s_%s" % (figure["name"], label))
            entry = {"stack": figure["name"], "label": label, "caption": caption,
                     "target_mm": target, "plane_mm": round(coordinate, 6),
                     "slice_index": index, "axis": figure["axis"],
                     "pixel_mm": [abs(axes["dcol"]), abs(axes["drow"])],
                     "col_axis": axes["col_axis"], "row_axis": axes["row_axis"]}
            entry.update(asset)
            report["planes"].append(entry)
            if figure["name"] == "recess" and label == "wall":
                report["measurements"]["recess_contour"] = measure_recess(image, axes, cfg)
                report["measurements"]["head_radius"] = measure_head_radius(image, axes, cfg)

    contour = report["measurements"].get("recess_contour", [])
    read = [r for r in contour if r["measured_mm"] is not None]
    worst = max((abs(r["delta_mm"]) for r in read), default=None)
    pixel = read[0]["pixel_mm"] if read else None
    report["verdict"] = {
        "contour_points_read": len(read), "of": len(contour),
        "worst_delta_mm": worst, "pixel_mm": pixel,
        "within_one_pixel": None if worst is None or pixel is None else worst <= pixel,
        "scope": "the raster confirms the mapping and the gross shape at pixel "
                 "resolution. The field samples, not the raster, carry the "
                 "sub-micrometre verdict.",
    }
    out = DEMO / "output" / "figures_measured.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf8")
    print(json.dumps({"calibration": report.get("calibration"),
                      "planes": [{k: p[k] for k in ("label", "plane_mm", "slice_index",
                                                    "asset", "px", "bytes")}
                                 for p in report["planes"]],
                      "contour": report["measurements"].get("recess_contour"),
                      "verdict": report["verdict"]}, indent=2))


if __name__ == "__main__":
    main()
