"""Verify the published snapshot and its recorded native payload identities."""
from pathlib import Path
import hashlib
import json
import sys

DEMO = Path(__file__).resolve().parents[1]
ROOT = DEMO.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from organize_notebook import read_file, write_file
from prepare import walk

def identity(chunks, predicate):
    result = hashlib.sha256()
    for chunk in walk(chunks):
        if predicate(chunk):
            for value in (chunk.typ.encode(), chunk.name.encode(), chunk.payload):
                result.update(len(value).to_bytes(8, "little")); result.update(value)
    return result.hexdigest()

def verify():
    manifest = json.loads((DEMO / "manifest.json").read_text())
    functions = 0
    for row in manifest["models"]:
        path = DEMO / row["file"]
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row["sha256"], row["file"]
        assert len(raw) == row["bytes"], row["file"]
        header, chunks = read_file(path)
        assert write_file(header, chunks) == raw, row["file"]
        assert identity(chunks, lambda c: c.name == "fn") == row["function_payload_sha256"]
        assert identity(chunks, lambda c: c.name not in ("index", "open", "sections")) == row["unchanged_payload_sha256"]
        functions += sum(c.name == "fn" for c in walk(chunks))
    for row in manifest["reports"] + manifest.get("assets", []):
        assert hashlib.sha256((DEMO / row["file"]).read_bytes()).hexdigest() == row["sha256"], row["file"]
    return {"models": len(manifest["models"]), "reports": len(manifest["reports"]),
            "function_chunks": functions, "snapshot_integrity": "PASS", "new_native_execution": False}

if __name__ == "__main__": print(json.dumps(verify(), indent=2))
