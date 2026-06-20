#!/usr/bin/env python3
"""Lightweight checks for MATLAB scripts that generate HFSS VBS files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_PATTERNS = [
    ("adds API root", r"\baddpath\s*\("),
    ("includes API paths", r"\bhfssIncludePaths\s*\("),
    ("defines HFSS executable", r"\bhfssExePath\s*="),
    ("opens VBS file", r"\bfopen\s*\("),
    ("creates or opens project", r"\bhfss(NewProject|OpenProject)\s*\("),
    ("sets active design", r"\bhfss(InsertDesign|SetDesign)\s*\("),
    ("saves project", r"\bhfssSaveProject\s*\("),
    ("closes VBS file", r"\bfclose\s*\("),
]


def find_assignment(text: str, name: str) -> str | None:
    pattern = rf"{re.escape(name)}\s*=\s*'([^']+)'"
    match = re.search(pattern, text)
    return match.group(1) if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path, help="MATLAB script to validate")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat path and run-order warnings as failures",
    )
    args = parser.parse_args()

    if not args.script.exists():
        print(f"FAIL: script not found: {args.script}")
        return 1

    text = args.script.read_text(encoding="utf-8", errors="ignore")
    failures: list[str] = []
    warnings: list[str] = []

    for label, pattern in REQUIRED_PATTERNS:
        if not re.search(pattern, text):
            failures.append(f"missing required step: {label}")

    api_root = find_assignment(text, "apiRoot")
    hfss_exe = find_assignment(text, "hfssExePath")

    if api_root and "hfss-api-master" not in api_root:
        warnings.append(f"apiRoot does not look like the bundled API root: {api_root}")
    if "F:\\2026fall\\HFSS_SKILL design\\hfss-api-master" in text:
        warnings.append("script still references the old external hfss-api-master path")
    if hfss_exe and not hfss_exe.lower().endswith("ansysedt.exe"):
        warnings.append(f"hfssExePath does not end with ansysedt.exe: {hfss_exe}")
    if hfss_exe and "F:\\AnsysEM\\v221\\Win64\\ansysedt.exe" not in hfss_exe:
        warnings.append(f"hfssExePath differs from configured default: {hfss_exe}")

    execute_pos = text.find("hfssExecuteScript")
    close_pos = text.find("fclose")
    if execute_pos >= 0 and close_pos >= 0 and execute_pos < close_pos:
        warnings.append("hfssExecuteScript appears before fclose; close the VBS first")

    if "hfssRemovePaths" not in text:
        warnings.append("hfssRemovePaths is not called; MATLAB path cleanup may be incomplete")

    if warnings and args.strict:
        failures.extend(warnings)
        warnings = []

    for warning in warnings:
        print(f"WARN: {warning}")
    for failure in failures:
        print(f"FAIL: {failure}")

    if failures:
        return 1

    print(f"OK: {args.script}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
