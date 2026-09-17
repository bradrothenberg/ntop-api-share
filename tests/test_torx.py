"""Offline checks for the Torx demo. No nTop, no network."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demos" / "torx"
SCRIPTS = DEMO / "scripts"

sys.path.insert(0, str(SCRIPTS))


def run(script):
    return subprocess.run([sys.executable, str(SCRIPTS / script)], cwd=SCRIPTS,
                          capture_output=True, text=True, encoding="utf8",
                          errors="replace", timeout=180)


def test_catalogue_matches_the_published_coverage():
    import torx_catalogue as cat
    summary = cat.summary()
    assert summary == {"schemaVersion": 1, "families": 2, "series": 3,
                       "metric_labels": 14, "drive_sizes": 16, "tamper_posts": 11,
                       "series_size_rows": 31, "cylindrical": 13, "pan": 9,
                       "countersunk": 9}


def test_every_source_row_cites_its_document():
    import torx_catalogue as cat
    assert all(row.get("source") for row in cat.SCREWS)
    assert all(row["source"] and row["role"] for row in cat.DRIVES)
    assert all(row["source"] and row["role"] for row in cat.POSTS)


def test_mirror_checks_itself():
    result = run("check_spec.py")
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["failed"] == 0
    assert report["checks"] > 600
    assert report["worst_delta"] < 1e-12


def test_offline_recipe_equals_ntops_own():
    build = run("build_torx.py")
    assert build.returncode == 0, build.stdout + build.stderr
    check = run("check_recipe.py")
    assert check.returncode == 0, check.stdout + check.stderr
    report = json.loads(check.stdout)
    assert report["identical"] is True
    assert report["blocks_identical"] == report["blocks_total"] == 8
    assert report["same_import_order"] and report["same_root_cbRefs"]


def test_recipe_carries_its_import_closure_in_dependency_order():
    import torx
    from torx_backend import validate
    recipe, _ctx, _blocks = torx.graph()
    assert validate(recipe) == []
    names = [d["name"] for d in recipe["imports"]]
    assert len(names) == len(set(names)) == 7
    for position, definition in enumerate(recipe["imports"]):
        for reference in definition.get("cbRefs", []):
            assert reference < position, "an import may only reference earlier ones"
    assert recipe["cbRefs"] == list(range(7))


def test_no_call_carries_a_revision_suffix():
    """Rule P4: a definition may carry a revision, a call to it may not."""
    import torx
    recipe, _ctx, _blocks = torx.graph()

    calls = []

    def walk(node):
        if isinstance(node, dict):
            func = node.get("func")
            if isinstance(func, str) and func.startswith("user_func_"):
                calls.append(func)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(recipe)
    assert calls, "the recipe should call its imports"
    assert not [c for c in calls if "[" in c]


def test_every_configuration_the_band_builds_is_valid():
    import torx_spec as spec
    entries = spec.configurations()
    assert len(entries) == 8
    assert all(entry["resolved"]["valid"] for entry in entries)
    for entry in spec.rejections():
        assert entry["valid"] is False
        assert entry["expected_failing_check"] in entry["failing_checks"]


def test_predictions_are_paired_and_frozen():
    import torx_spec as spec
    predictions = spec.predictions()
    ids = {row["id"] for row in predictions["samples"]}
    assert len(ids) == len(predictions["samples"])
    boundary = [r for r in predictions["samples"] if r["kind"] == "boundary"]
    assert len(boundary) == predictions["counts"]["boundary"]
    for row in boundary:
        assert row["id"] + "-in" in ids and row["id"] + "-out" in ids
        assert row["tolerance_m"] == spec.GATE_M


def test_v2_example_recipe_is_a_complete_closure():
    """Fifteen definitions in dependency order, two of them named Torx."""
    import json as _json
    from torx_backend import count_nodes, validate
    recipe = _json.loads(
        (DEMO / "inputs" / "recorded" / "torx_example_recipe.json").read_text(encoding="utf8"))
    assert validate(recipe) == []
    assert len(recipe["imports"]) == 15
    assert recipe["inputs"] == []
    names = [d["displayname"] for d in recipe["imports"]]
    assert names.count("Torx") == 2, "the example calls two different Torx blocks"
    uuids = [d["name"] for d in recipe["imports"]]
    assert len(set(uuids)) == 15, "two blocks may share a name, never a uuid"
    for position, definition in enumerate(recipe["imports"]):
        for reference in definition.get("cbRefs", []):
            assert reference < position
    assert count_nodes(recipe) == 1249
    assert [e["name"] for e in recipe["body"]] == [
        "Main body", "Torx result pair", "Detailed screws", "Outer moulds",
        "Detailed subtraction comparison", "Main body minus outer moulds"]


def test_the_imported_example_matches_its_recipe():
    """The readback of the imported notebook equals the source root graph."""
    report = DEMO / "output" / "check_example.json"
    if not report.exists():
        pytest.skip("no example receipt in this checkout; run check_example.py")
    import json as _json
    data = _json.loads(report.read_text(encoding="utf8"))
    assert data["graph"]["identical"] is True
    assert data["graph"]["same_variable_order"] is True
    assert data["import"]["custom_blocks_count"] == 15
    assert data["import"]["both_torx_blocks_kept"] is True
    assert data["import"]["variables_ok"] == 6


@pytest.mark.parametrize("name", ["README.md", "AGENTS.md", "reports/index.html"])
def test_demo_documents_exist(name):
    assert (DEMO / name).exists()


def test_report_assets_are_local_and_present():
    page = (DEMO / "reports" / "index.html").read_text(encoding="utf8")
    import re
    for src in re.findall(r'<img src="([^"]+)"', page):
        assert not src.startswith(("http://", "https://", "//", "data:"))
        assert (DEMO / "reports" / src).exists(), src


def test_no_private_paths_in_published_text():
    """Internal source paths must not travel with the public demo."""
    import re
    pattern = re.compile(r"Sagouin|C:\\\\Users|C:/Users", re.IGNORECASE)
    for path in list(DEMO.rglob("*.md")) + list(DEMO.rglob("*.py")) \
            + list((DEMO / "reports").rglob("*.html")):
        if "output" in path.parts:
            continue
        assert not pattern.search(path.read_text(encoding="utf8", errors="replace")), path
