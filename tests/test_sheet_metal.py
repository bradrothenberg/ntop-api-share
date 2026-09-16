"""Offline graph and output-location checks; no native forming evaluation."""
import json
import os
import subprocess
import sys

import pytest

from project import ROOT
from verify_recipe import verify

SCRIPTS = ROOT / ".agents/skills/ntop-sheet-metal/scripts"


def build(script, working_dir, case="all"):
    subprocess.run(
        [sys.executable, str(SCRIPTS / script), "--case", case],
        cwd=working_dir,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1"),
        capture_output=True, text=True, check=True, timeout=300,
    )


def check_graphs(folder, count):
    paths = sorted((folder / "models").glob("*.recipe.json"))
    assert len(paths) == count
    for path in paths:
        result = verify(json.loads(path.read_text(encoding="utf-8")))
        assert result["references_resolve"] and result["variables"] > 0


@pytest.mark.parametrize("script,subfolder,count", [
    ("build_sheet_metal.py", "", 10),
    ("build_advanced_sheet_metal.py", "advanced", 10),
    ("build_complex_sheet_metal.py", "complex", 12),
    ("build_drafted_sheet_metal.py", "drafted", 12),
])
def test_default_outputs_are_local_and_complete(script, subfolder, count, tmp_path):
    build(script, tmp_path)
    check_graphs(tmp_path / ".local/sheet-metal-study" / subfolder, count)


def test_family_builder_consumes_sibling_drafted_datums(tmp_path):
    build("build_drafted_sheet_metal.py", tmp_path, case="annular_cover")
    build("build_assembly_families.py", tmp_path)
    check_graphs(tmp_path / ".local/sheet-metal-study/assemblies/families", 12)
