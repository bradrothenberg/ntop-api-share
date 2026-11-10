"""Recompute inlet-format directional checks without running nTop or CFD.

Python standard library only. Writes JSON to stdout; does not modify evidence.
Exit codes: 0 comparisons pass, 1 numerical mismatch, 2 invalid evidence.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path


def finite(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label}: expected a number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label}: expected a finite number")
    return result


def vector(value, label, length=None):
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label}: expected a nonempty vector")
    result = [finite(x, label) for x in value]
    if length is not None and len(result) != length:
        raise ValueError(f"{label}: expected {length} components")
    return result


def same_q(actual, expected, label):
    actual = vector(actual, label, len(expected))
    if any(not math.isclose(x, y, rel_tol=0.0, abs_tol=1e-12)
           for x, y in zip(actual, expected)):
        raise ValueError(f"{label}: coefficients differ from the requested sample")


def audit(gate_path, normalization, rtol, atol, relative_floor=1e-12):
    gate_path = Path(gate_path).resolve()
    scales = vector(normalization, "normalization")
    if min(scales) <= 0:
        raise ValueError("normalization must be positive")
    rtol = finite(rtol, "rtol")
    atol = finite(atol, "atol")
    relative_floor = finite(relative_floor, "relative_floor")
    if min(rtol, atol) < 0 or relative_floor <= 0:
        raise ValueError("tolerances must be nonnegative; relative floor must be positive")
    hashes = {}

    def read(path):
        path = Path(path).resolve()
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if str(path) in hashes and hashes[str(path)] != digest:
            raise ValueError(f"Evidence changed during the audit: {path}")
        hashes[str(path)] = digest
        data = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(data, dict):
            raise ValueError(f"Expected a JSON object: {path}")
        return data

    def directory(raw):
        if not isinstance(raw, str) or not raw:
            raise ValueError("Expected an evaluation directory path")
        path = Path(raw)
        return path if path.is_absolute() else gate_path.parent / path

    gate = read(gate_path)
    q = vector(gate["q"], "gate.q")
    comparisons = gate["comparisons"]
    if not isinstance(comparisons, list) or not comparisons:
        raise ValueError("Gate has no comparisons")
    center_dir = directory(gate["center"])
    center = read(center_dir / "values.json")
    names = center["angular_function_names"]
    if (not isinstance(names, list) or len(names) != len(scales)
            or any(not isinstance(n, str) or not n for n in names)
            or len(set(names)) != len(names)):
        raise ValueError("Functional names must be unique and match normalization")

    def values(folder, expected_q):
        value = read(folder / "values.json")
        same_q(value["q"], expected_q, str(folder))
        if value["angular_function_names"] != names:
            raise ValueError(f"Functional order differs: {folder}")
        if value["candidate"] != center["candidate"]:
            raise ValueError(f"Candidate differs: {folder}")
        fp = value["fingerprint"]
        if fp["resolution"] != gate["resolution"]:
            raise ValueError(f"Mesh resolution differs: {folder}")
        for key in ("coefficient_scale", "flow_spec"):
            if fp[key] != center["fingerprint"][key]:
                raise ValueError(f"Study contract differs at {key}: {folder}")
        function = vector(value["angular_function_vector"], "function vector", len(scales))
        return value, function

    jacobians = {}
    for label, folder in (("production", center_dir), ("reference", directory(gate["reference"]))):
        value, _ = values(folder, q)
        gradient = read(folder / "angular_gradient.json")
        same_q(gradient["q"], q, f"{label} gradient")
        if gradient["fingerprint"] != value["fingerprint"]:
            raise ValueError(f"{label}: gradient and functional fingerprints differ")
        if gradient["objectives"] != names:
            raise ValueError(f"{label}: gradient functional order differs")
        matrix = gradient["jacobian_wrt_q"]
        if not isinstance(matrix, list) or len(matrix) != len(scales):
            raise ValueError(f"{label}: Jacobian row count differs")
        jacobians[label] = [vector(row, f"{label} Jacobian", len(q)) for row in matrix]

    rows = []
    for index, comparison in enumerate(comparisons):
        direction = vector(comparison["direction"], "direction", len(q))
        if not any(direction):
            raise ValueError("Direction is zero")
        step = finite(comparison["step"], "step")
        if step <= 0:
            raise ValueError("Step must be positive")
        _, plus = values(directory(comparison["plus"]), [x + step*d for x, d in zip(q, direction)])
        _, minus = values(directory(comparison["minus"]), [x - step*d for x, d in zip(q, direction)])
        fd = [finite((p-m)/(2*step)/s, "finite difference")
              for p, m, s in zip(plus, minus, scales)]
        for label, matrix in jacobians.items():
            ad = [finite(math.fsum(x*d for x, d in zip(row, direction))/s, "adjoint")
                  for row, s in zip(matrix, scales)]
            absolute = [finite(abs(a-f), "absolute error") for a, f in zip(ad, fd)]
            relative = [e/max(abs(a), abs(f), relative_floor) for e, a, f in zip(absolute, ad, fd)]
            passed = [e <= atol or r <= rtol for e, r in zip(absolute, relative)]
            rows.append(dict(comparison=index, kind=label, direction=direction, step=step,
                             adjoint=ad, finite_difference=fd, absolute_error=absolute,
                             relative_error=relative, component_passed=passed, passed=all(passed)))

    return dict(passed=all(row["passed"] for row in rows), gate=str(gate_path),
                scope="Saved directional comparisons only; no primal, provenance, or coverage certification",
                functionals=names, normalization=scales, rtol=rtol, atol=atol,
                relative_floor=relative_floor, checks=rows, input_sha256=hashes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", type=Path)
    parser.add_argument("--normalization", type=float, nargs="+", required=True)
    parser.add_argument("--rtol", type=float, required=True)
    parser.add_argument("--atol", type=float, required=True)
    parser.add_argument("--relative-floor", type=float, default=1e-12)
    args = parser.parse_args()
    try:
        result = audit(args.gate, args.normalization, args.rtol, args.atol, args.relative_floor)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, OverflowError) as exc:
        print(json.dumps(dict(passed=False, error=str(exc))))
        return 2
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
