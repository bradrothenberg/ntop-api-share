import hashlib,json
import pytest
from project import ROOT
from organize_notebook import read_file
from prepare import walk
from verify_saved_graph import compare

@pytest.mark.parametrize("demo,model",[("f16","F16_Parametric.ntop"),("a12","A12_R33.ntop"),("fcat","F-Cat_Parametric.ntop")])
def test_saved_graph_matches_native_construction(demo,model):
    result=compare(demo,model)
    assert not result["mismatched_names"]
    assert not result["extra_native_names"]

def test_fury_current_model_has_finite_edges_and_paused_mesh_operations():
    _,chunks=read_file(ROOT/"demos/fury/models/Fury_RC_TE_0p5in.ntop")
    leaves=list(walk(chunks))
    fn=json.loads(next(c.payload for c in leaves if c.name=="fn"))
    values={int(x["id"]):x for x in json.loads(next(c.payload for c in leaves if c.name=="index"))}
    controls=[x for x in fn["code"] if x["name"] in {"Wing trailing-edge thickness","HStab trailing-edge thickness","VStab trailing-edge thickness"}]
    assert len(controls)==3
    for block in controls:
        literal=values[block["inputs"][0]["instanceId"]]["value"]
        assert literal["val"]==0.0127
        assert literal["units"]=={"length":1}
    operations=[x for x in fn["code"] if x["func"].startswith(("mesh_by_adaptive_tets<","sharpen_mesh<","export_mesh<"))]
    assert operations
    assert all(x["paust"]==1 for x in operations)

def test_report_assets_and_pages_match_release_manifest():
    manifest=json.loads((ROOT/"reports/manifest.json").read_text())
    assert len(manifest["reports"])==27
    for item in manifest["reports"]+manifest["assets"]:
        raw=(ROOT/"reports"/item["file"]).read_bytes()
        assert len(raw)==item["bytes"]
        # Content-addressed assets retain their complete digest as a filename.
        expected=item.get("sha256") or (ROOT/item["file"]).stem
        assert hashlib.sha256(raw).hexdigest()==expected
