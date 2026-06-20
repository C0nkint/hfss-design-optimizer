#!/usr/bin/env python3
"""Parse a numeric HFSS report CSV and summarize a selected trace."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path


def parse_float(value: str) -> float | None:
    value = value.strip().strip('"')
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        match = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", value)
        return float(match.group(0)) if match else None


def unit_factor_to_ghz(header: str) -> float:
    lower = header.lower()
    if "ghz" in lower:
        return 1.0
    if "mhz" in lower:
        return 1e-3
    if "khz" in lower:
        return 1e-6
    if re.search(r"(^|[^gmk])hz", lower):
        return 1e-9
    return 1.0


def choose_column(headers: list[str], requested: str | None, fallback_index: int) -> int:
    if requested:
        needle = requested.lower()
        for i, header in enumerate(headers):
            if needle in header.lower():
                return i
        raise ValueError(f"no column contains: {requested}")
    if fallback_index < len(headers):
        return fallback_index
    raise ValueError("not enough columns")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--x-column", help="substring used to select the x/frequency column")
    parser.add_argument("--y-column", help="substring used to select the trace column")
    parser.add_argument("--target-ghz", type=float, help="target frequency in GHz")
    parser.add_argument("--json", action="store_true", help="emit JSON only")
    args = parser.parse_args()

    if not args.csv_file.exists():
        print(f"file not found: {args.csv_file}", file=sys.stderr)
        return 1

    with args.csv_file.open(newline="", encoding="utf-8-sig", errors="ignore") as handle:
        rows = list(csv.reader(handle))

    header_index = None
    for i, row in enumerate(rows):
        numeric_count = sum(parse_float(cell) is not None for cell in row)
        if len(row) >= 2 and numeric_count < len(row):
            next_rows = rows[i + 1 : i + 4]
            if any(sum(parse_float(cell) is not None for cell in r) >= 2 for r in next_rows):
                header_index = i
                break

    if header_index is None:
        print("could not locate a CSV header followed by numeric data", file=sys.stderr)
        return 1

    headers = [cell.strip() for cell in rows[header_index]]
    x_index = choose_column(headers, args.x_column or "freq", 0)
    y_index = choose_column(headers, args.y_column, 1)

    data = []
    for row in rows[header_index + 1 :]:
        if len(row) <= max(x_index, y_index):
            continue
        x = parse_float(row[x_index])
        y = parse_float(row[y_index])
        if x is None or y is None or not (math.isfinite(x) and math.isfinite(y)):
            continue
        data.append((x, y))

    if not data:
        print("no numeric data rows found", file=sys.stderr)
        return 1

    factor = unit_factor_to_ghz(headers[x_index])
    min_x, min_y = min(data, key=lambda pair: pair[1])
    result: dict[str, object] = {
        "file": str(args.csv_file),
        "rows": len(data),
        "x_column": headers[x_index],
        "y_column": headers[y_index],
        "min_y": min_y,
        "min_y_x": min_x,
        "min_y_x_ghz": min_x * factor,
    }

    if args.target_ghz is not None:
        nearest_x, nearest_y = min(data, key=lambda pair: abs(pair[0] * factor - args.target_ghz))
        result.update(
            {
                "target_ghz": args.target_ghz,
                "nearest_x": nearest_x,
                "nearest_x_ghz": nearest_x * factor,
                "nearest_y": nearest_y,
            }
        )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
