"""Stable identifiers and source facts. No geometry is evaluated here.

A direct port of the source project's `recipes/catalogue.js`. Values are
millimetres unless stated otherwise. Every row keeps its own source document,
revision and printed page: roles (recess, gauge, driver) are not interchangeable
and a value is never averaged across cited sheets.

Read with no nTop. `python torx_catalogue.py` prints the resolved tables.
"""
import json
from pathlib import Path

TABLES = Path(__file__).resolve().parents[1] / "inputs" / "source_tables"


def _rows(name):
    return json.loads((TABLES / name).read_text(encoding="utf8"))


# ISO 10664:1999 Table 1: size, nominal A, nominal B. Exact declared nominal
# dimensions, not metrology of one physical sample.
_DRIVE_AB = [(6, 1.75, 1.27), (8, 2.4, 1.75), (10, 2.8, 2.05), (15, 3.35, 2.4),
             (20, 3.95, 2.85), (25, 4.5, 3.25), (30, 5.6, 4.05), (40, 6.75, 4.85),
             (45, 7.93, 5.64), (50, 8.95, 6.45), (55, 11.35, 8.05), (60, 13.45, 9.6),
             (70, 15.7, 11.2), (80, 17.75, 12.8), (90, 20.2, 14.4), (100, 22.4, 16.0)]

DRIVES = [{"size": s, "A": a, "B": b,
           "source": "ISO 10664:1999, Table 1; supplied full PDF",
           "role": "nominal recess A and B",
           "contour": "Annex A informative convex radius 0.1 A chosen; "
                      "concave radius solved for tangency"}
          for s, a, b in _DRIVE_AB]

FAMILIES = [
    {"id": 0, "label": "Internal Torx", "implemented": True,
     "source": "ISO 10664:1999, Table 1 and informative Annex A"},
    {"id": 1, "label": "Tamper-resistant Torx", "implemented": True,
     "source": "Camcar TMH-642A, round post D REF; derived custom screw"},
]

SERIES = [
    {"id": 0, "label": "Cylindrical / ISO 14579:2011", "source": "ISO 14579:2011"},
    {"id": 1, "label": "Pan / ISO 14583:2011", "source": "ISO 14583:2011"},
    {"id": 2, "label": "Countersunk / ISO 14581:2013", "source": "ISO 14581:2013, historical"},
]

_CYL_SRC = _rows("ISO14579_rows.json")
_PAN_SRC = _rows("ISO14583_rows.json")
_CSK_SRC = _rows("ISO14581_2013_rows.json")

# Metric size labels. The cylindrical table defines the identifier order; a pan or
# countersunk diameter absent from it is appended, keeping every id stable.
SCREWS = [dict(row, id=i,
               label="M%g x %g%s" % (row["d"], row["P"],
                                     " (non-preferred)" if row.get("nonpreferred") else ""),
               source="%s, printed page %s" % (_CYL_SRC["source"]["title"],
                                               row["source_printed_page"]))
          for i, row in enumerate(_CYL_SRC["rows"])]
for row in _PAN_SRC["rows"]:
    if not any(s["d"] == row["d"] for s in SCREWS):
        SCREWS.append(dict(row, id=len(SCREWS),
                           label="M%g x %g (pan/countersunk)" % (row["d"], row["P"]),
                           source=_PAN_SRC["source"]["title"]))


def _by_d(d):
    return next(s["id"] for s in SCREWS if s["d"] == d)


CYLINDRICAL = [dict(r, id=_by_d(r["d"])) for r in _CYL_SRC["rows"]]
PAN = [dict(r, id=_by_d(r["d"])) for r in _PAN_SRC["rows"]]
COUNTERSUNK = [dict(r, id=_by_d(r["d"])) for r in _CSK_SRC["rows"]]

# Tamper-resistant posts. Each post belongs to its source drive size, never to a
# gauge-hole diameter, and keeps the units its own sheet printed.
POSTS = [{"size": s, "diameter": d, "source": "Camcar TMH-642A, PDF page 102, D REF",
          "role": "reference round post diameter",
          "heightPolicy": "Top approximately at head top; CAD choice flush",
          "adaptation": "Original sheet is button head; reused as an explicit custom "
                        "cylindrical-head derivative"}
         for s, d in [(8, .584), (10, .762), (15, 1.016), (25, 1.778),
                      (40, 2.642), (45, 3.175), (55, 4.572)]]
for size, inch in [(20, .055), (50, .140), (60, .211)]:
    POSTS.append({"size": size, "diameter": inch * 25.4,
                  "source": "Camcar TXH-203B, PDF page 18, D REF", "sourceInches": inch,
                  "role": "reference round post diameter",
                  "heightPolicy": "Top approximately at head top; CAD choice flush",
                  "adaptation": "Original sheet is button head; custom cylindrical-head derivative"})
POSTS.append({"size": 30, "diameter": 2.29,
              "source": "Camcar TMH-603B, PDF page 86, C DIA REF",
              "role": "reference round post diameter",
              "heightPolicy": "Top approximately at head top; CAD choice flush",
              "adaptation": "Source post reused in a custom cylindrical-head derivative"})
POSTS.sort(key=lambda r: r["size"])

SCHEMA_VERSION = 1

# The source-row table the size selector reads, in the column order the graph uses:
#   0 key, 1 d, 2 P, 3 dk, 4 k, 5 v, 6 r, 7 2P/a, 8 t, 9 drive, 10 b, 11 short limit,
#   12 web, 13 crown.
# Columns 5 to 7 and 13 carry a different declared meaning per series; that is why
# the key is series * 100 + size id and never a shared index.
SOURCE_ROWS = (
    [[r["id"], r["d"], r["P"], r["dk_max_plain"], r["k_max"], r["v_max"], r["r_min"],
      2 * r["P"], r["t_max"], r["drive"], r["b_ref"],
      r["full_thread_preferred_length_max"], r["w_min"], r["dk_max_plain"]]
     for r in CYLINDRICAL]
    + [[100 + r["id"], r["d"], r["P"], r["dk_max"], r["k_max"], r["r_min"], r["r_min"],
        r["a_max"], r["t_max"], r["drive"], 0, 0, 0, r["rf_approx"]]
       for r in PAN]
    + [[200 + r["id"], r["d"], r["P"], r["dk_actual_max"], r["k_max"], .1 * r["k_max"],
        .05 * r["P"], r["a_max"], r["t_max"], r["drive"], 0, 0, 0, r["dk_actual_max"]]
       for r in COUNTERSUNK])

DRIVE_ROWS = [[r["size"], r["A"], r["B"]] for r in DRIVES]
POST_ROWS = [[r["size"], r["diameter"]] for r in POSTS]

SOURCES = {
    "recess": _DRIVE_AB and "ISO 10664:1999, Table 1 and informative Annex A "
                            "(supplied complete PDF, not redistributed)",
    "cylindrical": _CYL_SRC["source"],
    "pan": _PAN_SRC["source"],
    "countersunk": _CSK_SRC["source"],
    "posts": "Camcar TMH-642A, TXH-203B and TMH-603B reference sheets",
    "thread": "ISO 68-1 basic profile; root, runout and tip simplified",
}


def summary():
    return {
        "schemaVersion": SCHEMA_VERSION,
        "families": len(FAMILIES), "series": len(SERIES),
        "metric_labels": len(SCREWS), "drive_sizes": len(DRIVES),
        "tamper_posts": len(POSTS),
        "series_size_rows": len(SOURCE_ROWS),
        "cylindrical": len(CYLINDRICAL), "pan": len(PAN), "countersunk": len(COUNTERSUNK),
    }


if __name__ == "__main__":
    print(json.dumps({"summary": summary(),
                      "labels": [s["label"] for s in SCREWS],
                      "drives": ["T%d" % r["size"] for r in DRIVES],
                      "posts": ["T%d" % r["size"] for r in POSTS]}, indent=2))
