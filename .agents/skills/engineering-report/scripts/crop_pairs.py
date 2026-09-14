"""Crop report figures to content.

Comparison pairs MUST share one crop box (union of both images' content
bounding boxes) so the cameras stay comparable; singles crop to their own
content. White background assumed.

Import and call, or edit the lists in __main__ and run:
    uv run --with pillow python crop_pairs.py
"""
import os
from PIL import Image, ImageChops

MARGIN = 20


def _bbox(im):
    bg = Image.new("RGB", im.size, (255, 255, 255))
    return ImageChops.difference(im, bg).getbbox()


def _clamp(box, size, margin=MARGIN):
    l, t, r, b = box
    return (max(0, l - margin), max(0, t - margin),
            min(size[0], r + margin), min(size[1], b + margin))


def crop_pair(path_a, path_b, out_a=None, out_b=None):
    """Crop two images with their shared union content box."""
    ims = [Image.open(p).convert("RGB") for p in (path_a, path_b)]
    boxes = [_bbox(im) for im in ims]
    box = (min(b[0] for b in boxes), min(b[1] for b in boxes),
           max(b[2] for b in boxes), max(b[3] for b in boxes))
    box = _clamp(box, ims[0].size)
    outs = [out_a or path_a.replace(".png", "_crop.png"),
            out_b or path_b.replace(".png", "_crop.png")]
    for im, out in zip(ims, outs):
        im.crop(box).save(out)
    return box


def crop_single(path, out=None):
    im = Image.open(path).convert("RGB")
    box = _clamp(_bbox(im), im.size)
    im.crop(box).save(out or path.replace(".png", "_crop.png"))
    return box


if __name__ == "__main__":
    FIGS = r"CHANGE_ME"
    PAIRS = []      # e.g. [("view_linear.png", "view_ho.png"), ...]
    SINGLES = []    # e.g. ["overview.png"]
    for a, b in PAIRS:
        print(a, b, crop_pair(os.path.join(FIGS, a), os.path.join(FIGS, b)))
    for s in SINGLES:
        print(s, crop_single(os.path.join(FIGS, s)))
