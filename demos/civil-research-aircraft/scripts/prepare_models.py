"""Create separate working copies with checkout-local airfoil inputs."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys

DEMO = Path(__file__).resolve().parents[1]
ROOT = DEMO.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from organize_notebook import read_file, write_file
from prepare import walk

PREFIX = "repo://demos/civil-research-aircraft/inputs/"

def prepare_models(model_names, output_dir=None):
    output = Path(output_dir) if output_dir is not None else DEMO / "output"
    inputs = output / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    for source in (DEMO / "inputs").iterdir():
        target = inputs / source.name
        if target.resolve() == source.resolve():
            raise ValueError("Keep the published inputs unchanged")
        shutil.copyfile(source, target)
    input_prefix = inputs.resolve().as_posix() + "/"
    def replace(value):
        if isinstance(value, dict): return {k: replace(v) for k, v in value.items()}
        if isinstance(value, list): return [replace(v) for v in value]
        if isinstance(value, str):
            value = value.replace(PREFIX, input_prefix)
            if "repo://" in value:
                raise ValueError("Unresolved portable input")
        return value
    receipt = []
    for name in model_names:
        source = (DEMO / name).resolve()
        if source.parent != (DEMO / "models").resolve() or source.suffix != ".ntop":
            raise ValueError("Select a published model filename")
        target = output / "models" / source.name
        if target.resolve() == source:
            raise ValueError("Keep the published notebook unchanged")
        original = source.read_bytes()
        header, chunks = read_file(source)
        for chunk in walk(chunks):
            if chunk.typ.lower() != "json": continue
            data = json.loads(chunk.payload)
            transformed = replace(data)
            if transformed != data:
                if chunk.name != "index":
                    raise ValueError("A runtime path would change a non-literal chunk")
                chunk.payload = json.dumps(transformed, separators=(",", ":")).encode()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(write_file(header, chunks))
        if source.read_bytes() != original:
            raise RuntimeError("Published source changed during preparation")
        receipt.append({"source": name, "source_sha256": hashlib.sha256(original).hexdigest(),
                        "working_file": str(target.resolve()), "new_native_execution": False})
    (output / "preparation.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="Prepare all published snapshots")
    parser.add_argument("--model", help="Filename within models/; defaults to the Revision G assembly")
    args = parser.parse_args()
    if args.all and args.model: parser.error("Choose --all or --model")
    if args.all:
        names = [p.relative_to(DEMO).as_posix() for p in sorted((DEMO / "models").glob("*.ntop"))]
    else:
        names = ["models/" + (args.model or "civil-research-aircraft-rev-g.ntop")]
    print(json.dumps(prepare_models(names), indent=2))

if __name__ == "__main__": main()
