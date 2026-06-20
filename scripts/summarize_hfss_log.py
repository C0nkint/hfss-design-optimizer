#!/usr/bin/env python3
"""Summarize the latest Ansys Electronics Desktop batch log segment."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SEGMENT_MARKER = "Ansys Electronics Desktop Version"


def latest_segment(text: str) -> str:
    parts = text.split(SEGMENT_MARKER)
    if len(parts) <= 1:
        return text
    return SEGMENT_MARKER + parts[-1]


def collect_lines(segment: str, token: str) -> list[str]:
    return [line.strip() for line in segment.splitlines() if token.lower() in line.lower()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log_file", type=Path)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    if not args.log_file.exists():
        print(f"log not found: {args.log_file}", file=sys.stderr)
        return 1

    text = args.log_file.read_text(encoding="utf-8", errors="ignore")
    segment = latest_segment(text)

    errors = collect_lines(segment, "[error]")
    warnings = collect_lines(segment, "[warning]")
    infos = collect_lines(segment, "[info]")
    started = bool(re.search(r"Starting Batch Run", segment, re.IGNORECASE))
    stopped = bool(re.search(r"Stopping Batch Run", segment, re.IGNORECASE))
    normal = bool(re.search(r"Normal completion of simulation", segment, re.IGNORECASE))
    converged = bool(re.search(r"frequency sweep complete\. Converged", segment, re.IGNORECASE))
    nonconverged_sweep = bool(
        re.search(r"interpolating frequency sweep (did not|did NOT|didn't) converge", segment, re.IGNORECASE)
        or re.search(r"did not converge to the desired tolerance", segment, re.IGNORECASE)
    )

    if errors:
        status = "failed"
    elif normal and nonconverged_sweep:
        status = "solved_nonconverged_sweep"
    elif normal or converged:
        status = "solved"
    elif started and stopped:
        status = "completed"
    elif started:
        status = "running_or_incomplete"
    else:
        status = "unknown"

    result = {
        "file": str(args.log_file),
        "status": status,
        "started": started,
        "stopped": stopped,
        "normal_completion": normal,
        "sweep_converged": converged,
        "nonconverged_sweep": nonconverged_sweep,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "info_count": len(infos),
        "errors": errors,
        "warnings": warnings,
        "infos": infos,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"status: {status}")
        print(f"started: {started}")
        print(f"stopped: {stopped}")
        print(f"normal_completion: {normal}")
        print(f"sweep_converged: {converged}")
        print(f"nonconverged_sweep: {nonconverged_sweep}")
        print(f"errors: {len(errors)}")
        for line in errors:
            print(f"  {line}")
        print(f"warnings: {len(warnings)}")
        for line in warnings:
            print(f"  {line}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())



