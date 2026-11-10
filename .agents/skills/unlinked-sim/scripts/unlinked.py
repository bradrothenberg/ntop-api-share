"""Local Unlinked API helper. Standard library only; no automatic POST retries."""
from __future__ import annotations

import argparse
import hashlib
import http.cookiejar
import json
import math
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def new_directory(path):
    result = Path(path).resolve()
    result.mkdir(parents=True, exist_ok=False)
    return result


class Client:
    def __init__(self, url="http://localhost:3000"):
        parsed = urllib.parse.urlsplit(url)
        if (parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
                or parsed.username or parsed.password or parsed.query or parsed.fragment
                or parsed.path not in {"", "/"}):
            raise ValueError("Use an HTTP loopback origin without a path or credentials")
        self.url = url.rstrip("/")
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(self, method, path, body=None, raw=False):
        if not path.startswith("/api/"):
            raise ValueError("Expected an /api/ route")
        headers = {"Origin": self.url}
        if isinstance(body, bytes):
            data = body
            headers["Content-Type"] = "application/octet-stream"
        elif body is not None:
            data = json.dumps(body, allow_nan=False).encode()
            headers["Content-Type"] = "application/json"
        else:
            data = None
        request = urllib.request.Request(self.url + path, data=data, headers=headers, method=method)
        try:
            with self.opener.open(request, timeout=120) as response:
                content = response.read()
        except urllib.error.HTTPError as error:
            message = error.read(2048).decode(errors="replace")
            raise RuntimeError(f"{method} {path}: HTTP {error.code}: {message}") from error
        except (urllib.error.URLError, TimeoutError) as error:
            suffix = " Inspect server state before retrying this mutation." if method != "GET" else ""
            raise RuntimeError(f"{method} {path}: connection failed or timed out.{suffix}") from error
        return content if raw else (json.loads(content) if content else None)

    def login(self):
        self.request("GET", "/api/auth/dev-login", raw=True)

    def project(self, org_name, project_name):
        def unique(items, name):
            matches = [item for item in items if item["name"] == name]
            if len(matches) > 1:
                raise ValueError(f"More than one match for {name!r}; use IDs directly")
            return matches[0] if matches else None

        org = unique(self.request("GET", "/api/orgs"), org_name)
        if org is None:
            org = self.request("POST", "/api/orgs", {"name": org_name})
        route = f"/api/orgs/{org['id']}/projects"
        project = unique(self.request("GET", route), project_name)
        if project is None:
            project = self.request("POST", route, {"name": project_name,
                "description": "Local simulation with saved inputs and verification."})
        return {"org_id": org["id"], "project_id": project["id"], "name": project["name"]}

    def upload(self, project_id, path, data):
        route = f"/api/projects/{project_id}/files"
        existing = [f for f in self.request("GET", route) if f["path"] == path]
        if len(existing) > 1:
            raise ValueError(f"Ambiguous file path {path}")
        if existing:
            item = existing[0]
            current = self.request("GET", f"{route}/{item['id']}/content", raw=True)
            if current == data:
                return item
        query = urllib.parse.urlencode({"path": path, "message": "Versioned local simulation input"})
        return self.request("POST", f"{route}?{query}", data)

    def archive(self, out):
        index = []
        for project in self.request("GET", "/api/projects"):
            for item in self.request("GET", f"/api/projects/{project['id']}/files"):
                if Path(item["path"]).suffix.lower() not in {".mdl", ".slx"}:
                    continue
                for run in self.request("GET", f"/api/files/{item['id']}/simulations"):
                    result = self.request("GET", f"/api/simulations/{run['id']}")
                    save(out / f"{run['id']}.json", result)
                    index.append({"project_id": project["id"], "file_id": item["id"],
                                  "path": item["path"], "run_id": run["id"], "status": run["status"]})
        save(out / "index.json", index)
        return {"archived_runs": len(index), "directory": str(out)}


def check_result(result):
    run = result["run"]
    if run["status"] != "completed":
        raise ValueError(f"Run {run.get('id')} is {run['status']}: {run.get('error')}")
    trace = result.get("trace") or {}
    times = trace.get("time", [])
    signals = trace.get("signals", {})

    def finite(values):
        return all(isinstance(x, (int, float)) and not isinstance(x, bool)
                   and math.isfinite(x) for x in values)

    if not times or not finite(times) or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("Trace time must be nonempty, finite, and strictly increasing")
    options = run["request"]["options"]
    tolerance = 1e-9 * max(1, abs(options["start"]), abs(options["stop"]))
    if abs(times[0] - options["start"]) > tolerance or abs(times[-1] - options["stop"]) > tolerance:
        raise ValueError("Trace does not cover the requested interval")
    if not signals or any(len(v) != len(times) or not finite(v) for v in signals.values()):
        raise ValueError("Signal arrays must be nonempty, finite, and aligned with time")
    requested = options.get("output_signals")
    if requested and not set(requested).issubset(signals):
        raise ValueError("Requested output signals are missing")
    return {"run_id": run["id"], "status": run["status"], "samples": len(times),
            "signals": len(signals), "start": times[0], "stop": times[-1],
            "structural_checks_passed": True}


def expressions(path):
    if path is None:
        return {}
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str)
                                            for k, v in value.items()):
        raise ValueError("Overrides must be a JSON object with string expression values")
    return value


def run_model(client, args):
    if not all(math.isfinite(v) for v in [args.start, args.stop, args.step]):
        raise ValueError("Times and step must be finite")
    if args.step <= 0 or args.stop <= args.start:
        raise ValueError("Require start < stop and a positive step")
    if math.ceil((args.stop - args.start) / args.step) + 1 > 25001:
        raise ValueError("Requested grid exceeds the reference server's 25,001-sample cap")
    model_path = Path(args.model)
    if model_path.suffix.lower() not in {".mdl", ".slx"}:
        raise ValueError("Model must be .mdl or .slx")
    model_bytes = model_path.read_bytes()
    if len(model_bytes) > 16 * 1024 * 1024:
        raise ValueError("Model exceeds 16 MiB")
    init_path = Path(args.init) if args.init else None
    init_bytes = init_path.read_bytes() if init_path else None
    if init_path and (init_path.suffix.lower() != ".m" or len(init_bytes) > 65536):
        raise ValueError("Init must be a .m file no larger than 64 KiB")
    workspace, inputs = expressions(args.workspace), expressions(args.inputs)
    out = new_directory(args.out)
    source = out / "inputs"
    source.mkdir()
    files = {}
    for path, data in [(model_path, model_bytes), (init_path, init_bytes)]:
        if path:
            (source / path.name).write_bytes(data)
            files[path.name] = {"sha256": hashlib.sha256(data).hexdigest()}
    # Save local input provenance before any upload.
    save(out / "source.json", {"url": client.url, "project_id": args.project_id, "files": files})
    model = client.upload(args.project_id, model_path.name, model_bytes)
    request = {"version": model["latest"]["version"], "workspace": workspace, "inputs": inputs,
               "options": {"start": args.start, "stop": args.stop, "step": args.step,
                           "solver": args.solver, "max_samples": 25001}}
    if args.signal:
        request["options"]["output_signals"] = args.signal
    if init_path:
        init = client.upload(args.project_id, init_path.name, init_bytes)
        request["init_script"] = {"file_id": init["id"], "version": init["latest"]["version"]}
    receipt = {"project_id": args.project_id, "file_id": model["id"], "request": request,
               "model_url": f"{client.url}/projects/{args.project_id}/files/{model['id']}"}
    save(out / "pending.json", receipt)
    result = client.request("POST", f"/api/files/{model['id']}/simulations", request)
    save(out / "result.json", result)  # Preserve failed results too.
    report = check_result(result)
    if result["run"]["file_version"] != request["version"]:
        raise ValueError("Returned model version differs from requested version")
    if result["run"]["request"].get("init_script") != request.get("init_script"):
        raise ValueError("Returned init-script version differs from requested version")
    report.update({"directory": str(out), "model_url": receipt["model_url"]})
    save(out / "verification.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:3000")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("health")
    project = commands.add_parser("project")
    project.add_argument("--org", required=True)
    project.add_argument("--name", required=True)
    archive = commands.add_parser("archive-history")
    archive.add_argument("--out", required=True)
    check = commands.add_parser("check")
    check.add_argument("result")
    fetch = commands.add_parser("fetch")
    fetch.add_argument("--run-id", required=True)
    fetch.add_argument("--out", required=True)
    run = commands.add_parser("run")
    run.add_argument("--project-id", required=True)
    run.add_argument("--model", required=True)
    run.add_argument("--init")
    run.add_argument("--workspace")
    run.add_argument("--inputs")
    run.add_argument("--signal", action="append")
    run.add_argument("--start", type=float, default=0)
    run.add_argument("--stop", type=float, required=True)
    run.add_argument("--step", type=float, required=True)
    run.add_argument("--solver", choices=["euler", "rk4", "rk45"], default="rk4")
    run.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.command == "check":
        return check_result(json.loads(Path(args.result).read_text(encoding="utf-8")))
    client = Client(args.url)
    if args.command == "health":
        return client.request("GET", "/api/health")
    client.login()
    if args.command == "project":
        return client.project(args.org, args.name)
    if args.command == "archive-history":
        return client.archive(new_directory(args.out))
    if args.command == "fetch":
        out = new_directory(args.out)
        result = client.request("GET", f"/api/simulations/{args.run_id}")
        save(out / "result.json", result)
        return {"directory": str(out), "status": result["run"]["status"]}
    return run_model(client, args)


if __name__ == "__main__":
    try:
        print(json.dumps(main(), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as error:
        print(f"Unlinked: {error}", file=sys.stderr)
        sys.exit(1)
