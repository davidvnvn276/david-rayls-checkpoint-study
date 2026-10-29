"""Reproduce the original audit and the separately recorded checkpoint follow-up.

The default workflow is fully offline after installing requirements-lock.txt.
Outputs are new files; the preserved original publication archive is never edited.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parent
BASELINE_ARCHIVE = "original-publication.zip"
BASELINE_SHA256 = "b0e51f0b6cd4bc4ed51bbd336108812b395201fcf08f6586cbf3c5e6ed892bdc"


def integrity():
    manifest = json.loads((ROOT / "MANIFEST_SHA256.json").read_text())
    failures = []
    for relative, expected in manifest["files"].items():
        p = PurePosixPath(relative)
        target = ROOT / relative
        if p.is_absolute() or ".." in p.parts or not target.resolve().is_relative_to(ROOT):
            failures.append({"file": relative, "error": "unsafe path"})
        elif not target.is_file():
            failures.append({"file": relative, "error": "missing"})
        elif hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            failures.append({"file": relative, "error": "SHA-256 mismatch"})
    if failures:
        raise ValueError(json.dumps(failures))
    return {"status": "passed", "files_checked": len(manifest["files"]),
            "limit": "Listed file consistency, not publisher or starting-anchor authentication."}


def extract_baseline(destination):
    data = (ROOT / BASELINE_ARCHIVE).read_bytes()
    if hashlib.sha256(data).hexdigest() != BASELINE_SHA256:
        raise ValueError("Original publication archive identity mismatch")
    with zipfile.ZipFile(ROOT / BASELINE_ARCHIVE) as archive:
        if archive.testzip() is not None:
            raise ValueError("Original archive CRC failure")
        files = [i for i in archive.infolist() if not i.is_dir()]
        if len(files) != 121:
            raise ValueError("Unexpected original publication file count")
        for item in archive.infolist():
            p = PurePosixPath(item.filename)
            if p.is_absolute() or ".." in p.parts or not (destination / item.filename).resolve().is_relative_to(destination):
                raise ValueError("Unsafe original archive path")
        archive.extractall(destination)
    return destination / "DAVID_Week4_Publication"


def main():
    if not __debug__:
        raise SystemExit("Run without -O or -OO; the preserved programs use assertions.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="New directory, separate from packaged input data")
    parser.add_argument("--integrity-only", action="store_true")
    args = parser.parse_args()
    if args.integrity_only:
        print(json.dumps(integrity(), indent=2))
        return
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = Path(args.output).expanduser().resolve() if args.output else ROOT / "runs" / stamp
    if output == ROOT or output.is_relative_to(ROOT / "followup"):
        raise SystemExit("Use a new output directory outside packaged follow-up inputs")
    output.mkdir(parents=True, exist_ok=False)
    logs = output / "logs";logs.mkdir()
    started = time.monotonic();steps = [];error = None

    def run(label, command):
        print(f"Running: {label}", flush=True)
        log = logs / f"{len(steps)+1:02d}-{label}.log"
        start = time.monotonic()
        with log.open("w", encoding="utf-8") as stream:
            result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
        steps.append({"name": label, "command": command, "exit_code": result.returncode,
                      "seconds": round(time.monotonic()-start, 3),
                      "log": str(log.relative_to(output))})
        if result.returncode:
            raise RuntimeError(f"{label} failed: inspect {log}")
        print(f"PASS: {label}", flush=True)

    try:
        before = integrity()
        publication = extract_baseline(output / "extracted-original")
        run("original-ten-step-audit", [sys.executable, "-B", str(publication / "verify_all.py"),
                                       "--output", str(output / "baseline")])
        run("complete-second-library-and-chain-controls", [sys.executable, "-B",
            str(ROOT / "followup/verify_followup.py"), "--publication", str(publication),
            "--output", str(output / "followup")])
        run("all-175-execution-headers", [sys.executable, "-B", str(ROOT / "followup/check_headers.py"),
            "--publication", str(publication), "--capture-dir", str(ROOT / "followup/data/headers-20261029"),
            "--output", str(output / "headers.json")])
        run("article-and-figure-values", [sys.executable, "-B", str(ROOT / "followup/check_publication.py")])
        after = integrity()
        if before != after:
            raise ValueError("Distribution integrity changed during the audit")
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    report = {"status": "failed" if error else "passed", "python": sys.version,
              "started_at_utc": stamp, "seconds": round(time.monotonic()-started, 3),
              "steps": steps, "expected_stages": 4, "stages_completed": len(steps),
              "error": error,
              "scope": "Saved-data reproduction; no live RPC, wallet or transaction submission.",
              "trust_limit": "Initial committee remains observed, not independently authenticated."}
    (output / "review-summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ["status", "stages_completed", "expected_stages", "seconds", "error"]}, indent=2))
    print(f"Report: {output / 'review-summary.json'}", flush=True)
    if error:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
