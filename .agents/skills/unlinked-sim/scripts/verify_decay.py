"""Compare the included scalar decay pilot with its exact analytical solution."""
import argparse
import json
import math
from pathlib import Path
from unlinked import check_result

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("result")
parser.add_argument("--rate", type=float, required=True)
parser.add_argument("--x0", type=float, required=True)
parser.add_argument("--tolerance", type=float, default=1e-7)
args = parser.parse_args()
if not all(math.isfinite(x) for x in (args.rate, args.x0, args.tolerance)) or args.tolerance <= 0:
    parser.error("Parameters must be finite; tolerance must be positive")
result = json.loads(Path(args.result).read_text(encoding="utf-8"))
report = check_result(result)
trace = result["trace"]
start = result["run"]["request"]["options"]["start"]
expected = [args.x0 * math.exp(-args.rate * (t - start)) for t in trace["time"]]
errors = {key: max(abs(a-b) for a,b in zip(trace["signals"][key], expected)) for key in ("1", "3")}
derivative_error = max(abs(a + args.rate*b) for a,b in zip(trace["signals"]["2"], trace["signals"]["1"]))
report.update({"max_state_error": errors, "max_derivative_residual": derivative_error,
               "tolerance": args.tolerance,
               "analytical_check_passed": max(*errors.values(), derivative_error) <= args.tolerance})
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["analytical_check_passed"] else 1)
