#!/usr/bin/env python3
"""Create a compact learning summary from papers plus HFSS simulation files."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PAPER_EXTS = {".pdf"}
CODE_EXTS = {".m", ".vbs", ".py", ".ps1", ".js", ".vb", ".bas"}
RESULT_EXTS = {".csv", ".tab", ".dat", ".s1p", ".s2p", ".s3p", ".s4p", ".snp", ".txt", ".log"}
PROJECT_EXTS = {".aedt", ".aedtresults", ".asol"}
TEXT_EXTS = CODE_EXTS | RESULT_EXTS | {".md", ".rst", ".ini", ".cfg"}
SKIP_DIRS = {".git", "__pycache__", ".hfss_skill_learning"}

INNOVATION_KEYWORDS = [
    "novel", "innovation", "innovative", "propose", "proposed", "contribution",
    "first", "new", "method", "approach", "architecture", "design", "optimized",
    "low-loss", "broadband", "wideband", "compact", "high efficiency", "high gain",
    "measurement", "measured", "simulation", "simulated", "prototype",
    "\u521b\u65b0", "\u63d0\u51fa", "\u672c\u6587", "\u65b9\u6cd5",
    "\u8bbe\u8ba1", "\u4f18\u5316", "\u5bbd\u5e26", "\u4f4e\u635f\u8017",
    "\u4eff\u771f", "\u6d4b\u8bd5",
]

HFSS_PATTERNS = {
    "ports": re.compile(r"hfssAssign(?:Lumped|Wave|Floquet|Circular)Port|Assign(?:Lumped|Wave|Floquet)Port|CreatePort", re.I),
    "materials": re.compile(r"hfssAddMaterial|hfssAssignMaterial|AddMaterial|AssignMaterial|permittivity|dielectric|tanD|conductivity", re.I),
    "mesh": re.compile(r"hfssAssignLengthOp|AssignLengthOp|Mesh|MaximumPasses|MaxDeltaS|MaxRefinement", re.I),
    "sweeps": re.compile(r"hfssInsertSolution|hfssInterpolatingSweep|InsertFrequencySweep|Sweep|Setup|Solve", re.I),
    "reports": re.compile(r"CreateReport|ExportToFile|ExportNetworkData|S\(", re.I),
}

@dataclass
class FileInfo:
    path: Path
    rel: str
    ext: str
    size: int
    kind: str


def human_size(n: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(n)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{n} B"


def classify(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in PAPER_EXTS:
        return "paper"
    if ext in CODE_EXTS:
        return "simulation-code"
    if ext in {".s1p", ".s2p", ".s3p", ".s4p", ".snp"}:
        return "touchstone"
    if ext in {".csv", ".tab", ".dat"}:
        return "result-table"
    if ext in {".aedt", ".asol"}:
        return "hfss-project"
    if ext == ".log":
        return "solver-log"
    if ext in TEXT_EXTS:
        return "text"
    return "other"


def iter_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.endswith(".aedtresults")]
        for name in files:
            yield Path(current) / name


def read_text(path: Path, limit: int = 200_000) -> str:
    data = path.read_bytes()[:limit]
    for enc in ("utf-8", "utf-8-sig", "gbk", "latin-1"):
        try:
            return data.decode(enc, errors="ignore")
        except LookupError:
            continue
    return data.decode("utf-8", errors="ignore")


def try_pdf_with_pypdf(path: Path) -> tuple[str, str] | None:
    for module_name in ("pypdf", "PyPDF2"):
        try:
            module = __import__(module_name)
            reader = module.PdfReader(str(path))
            pages = []
            for page in reader.pages[:80]:
                pages.append(page.extract_text() or "")
            return "\n".join(pages), module_name
        except Exception:
            continue
    return None


def try_pdf_with_fitz(path: Path) -> tuple[str, str] | None:
    try:
        import fitz  # type: ignore
        doc = fitz.open(str(path))
        pages = [doc[i].get_text() for i in range(min(len(doc), 80))]
        return "\n".join(pages), "PyMuPDF"
    except Exception:
        return None


def try_pdf_with_pdftotext(path: Path) -> tuple[str, str] | None:
    exe = shutil.which("pdftotext")
    if not exe:
        return None
    try:
        result = subprocess.run(
            [exe, "-layout", str(path), "-"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=60,
        )
        if result.stdout.strip():
            return result.stdout, "pdftotext"
    except Exception:
        return None
    return None


def extract_pdf_text(path: Path) -> tuple[str, str]:
    for method in (try_pdf_with_pypdf, try_pdf_with_fitz, try_pdf_with_pdftotext):
        result = method(path)
        if result and result[0].strip():
            return result
    return "", "unparsed"


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?。！？])\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 30]


def snippets(text: str, keywords: list[str], limit: int = 10) -> list[str]:
    found = []
    seen = set()
    lowered_keywords = [k.lower() for k in keywords]
    for sentence in split_sentences(text):
        low = sentence.lower()
        if any(k in low for k in lowered_keywords):
            clean = sentence[:420]
            key = clean.lower()
            if key not in seen:
                found.append(clean)
                seen.add(key)
        if len(found) >= limit:
            break
    return found


def summarize_csv(path: Path) -> dict:
    try:
        with path.open(newline="", encoding="utf-8-sig", errors="ignore") as f:
            sample = f.read(4096)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample) if sample.strip() else csv.excel
            reader = csv.DictReader(f, dialect=dialect)
            rows = list(reader)
    except Exception as exc:
        return {"error": str(exc)}
    if not rows:
        return {"rows": 0}
    headers = list(rows[0].keys())
    summary: dict = {"rows": len(rows), "columns": headers[:20]}
    freq_col = next((h for h in headers if h and "freq" in h.lower()), None)
    if freq_col:
        values = []
        for row in rows:
            try:
                values.append(float(row[freq_col]))
            except Exception:
                pass
        if values:
            summary["freq_start"] = min(values)
            summary["freq_stop"] = max(values)
    s_columns = [h for h in headers if h and ("s(" in h.lower() or "s[" in h.lower() or h.lower().startswith("s"))]
    metrics = {}
    for col in s_columns[:8]:
        vals = []
        for row in rows:
            try:
                vals.append(float(row[col]))
            except Exception:
                pass
        if vals:
            metrics[col] = {"min": min(vals), "max": max(vals), "avg": sum(vals) / len(vals)}
    if metrics:
        summary["s_parameter_metrics"] = metrics
    return summary


def summarize_touchstone(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    option = ""
    data = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("!"):
            continue
        if line.startswith("#"):
            option = line
            continue
        parts = line.split()
        try:
            nums = [float(x) for x in parts]
        except Exception:
            continue
        if nums:
            data.append(nums)
    summary: dict = {"points": len(data), "option": option}
    if data:
        freqs = [row[0] for row in data]
        summary["freq_start"] = min(freqs)
        summary["freq_stop"] = max(freqs)
    fmt = option.lower().split()
    data_format = next((x for x in fmt if x in {"ma", "db", "ri"}), "ma")
    if data and len(data[0]) >= 5:
        s21_db = []
        for row in data:
            a, b = row[3], row[4]
            if data_format == "db":
                db = a
            elif data_format == "ri":
                mag = math.hypot(a, b)
                db = 20 * math.log10(mag) if mag > 0 else float("-inf")
            else:
                db = 20 * math.log10(abs(a)) if a != 0 else float("-inf")
            s21_db.append((row[0], db))
        finite = [(f, v) for f, v in s21_db if math.isfinite(v)]
        if finite:
            best = max(finite, key=lambda item: item[1])
            worst = min(finite, key=lambda item: item[1])
            summary["s21_db_best"] = {"freq": best[0], "value": best[1]}
            summary["s21_db_worst"] = {"freq": worst[0], "value": worst[1]}
    return summary


def scan_hfss_text(text: str) -> dict[str, list[str]]:
    result = {}
    lines = text.splitlines()
    for label, pattern in HFSS_PATTERNS.items():
        hits = []
        for line in lines:
            if pattern.search(line):
                clean = line.strip()
                if clean and clean not in hits:
                    hits.append(clean[:240])
            if len(hits) >= 8:
                break
        if hits:
            result[label] = hits
    return result


def markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]
    out = []
    for idx, row in enumerate(rows):
        out.append("| " + " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(row))) + " |")
        if idx == 0:
            out.append("| " + " | ".join("-" * widths[i] for i in range(len(row))) + " |")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="folder containing papers and simulation artifacts")
    parser.add_argument("--output", type=Path, default=None, help="markdown output path")
    parser.add_argument("--work-dir", type=Path, default=None, help="directory for extracted text")
    parser.add_argument("--max-paper-chars", type=int, default=12000)
    parser.add_argument("--json", action="store_true", help="also write a JSON summary next to markdown")
    args = parser.parse_args()

    bundle = args.bundle.resolve()
    if not bundle.exists() or not bundle.is_dir():
        print(f"bundle directory not found: {bundle}", file=sys.stderr)
        return 1

    work_dir = args.work_dir or (bundle / ".hfss_skill_learning")
    work_dir.mkdir(parents=True, exist_ok=True)
    extracted_dir = work_dir / "extracted_text"
    extracted_dir.mkdir(parents=True, exist_ok=True)
    output = args.output or (work_dir / "bundle_learning_summary.md")

    files = []
    for path in iter_files(bundle):
        try:
            stat = path.stat()
        except OSError:
            continue
        rel = str(path.relative_to(bundle))
        files.append(FileInfo(path, rel, path.suffix.lower(), stat.st_size, classify(path)))
    files.sort(key=lambda item: item.rel.lower())

    paper_sections = []
    code_sections = []
    result_sections = []
    limitations = []
    all_innovation_snippets = []

    for info in files:
        if info.kind == "paper":
            text, method = extract_pdf_text(info.path)
            if text:
                safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", info.rel) + ".txt"
                extracted_path = extracted_dir / safe
                extracted_path.write_text(text, encoding="utf-8")
                snips = snippets(text[: args.max_paper_chars], INNOVATION_KEYWORDS, limit=12)
                all_innovation_snippets.extend((info.rel, s) for s in snips[:8])
                paper_sections.append({
                    "file": info.rel,
                    "method": method,
                    "chars": len(text),
                    "extracted_text": str(extracted_path.relative_to(bundle)),
                    "snippets": snips,
                })
            else:
                limitations.append(f"PDF text not extracted: {info.rel}")
        elif info.ext in CODE_EXTS or info.ext in {".aedt", ".log", ".txt", ".md"}:
            text = read_text(info.path)
            hits = scan_hfss_text(text)
            if hits:
                code_sections.append({"file": info.rel, "hits": hits})
        elif info.kind == "result-table":
            result_sections.append({"file": info.rel, "summary": summarize_csv(info.path)})
        elif info.kind == "touchstone":
            result_sections.append({"file": info.rel, "summary": summarize_touchstone(info.path)})

    manifest_rows = [["File", "Kind", "Size"]]
    for info in files[:300]:
        manifest_rows.append([info.rel, info.kind, human_size(info.size)])
    if len(files) > 300:
        manifest_rows.append([f"... {len(files) - 300} more files", "", ""])

    md = []
    md.append("# HFSS Research Bundle Learning Summary")
    md.append("")
    md.append(f"Bundle: `{bundle}`")
    md.append(f"Files scanned: {len(files)}")
    md.append("")
    md.append("## File Manifest")
    md.append("")
    md.append(markdown_table(manifest_rows))
    md.append("")
    md.append("## Paper Extraction")
    md.append("")
    if paper_sections:
        for section in paper_sections:
            md.append(f"### {section['file']}")
            md.append(f"- Extraction method: {section['method']}")
            md.append(f"- Extracted characters: {section['chars']}")
            md.append(f"- Extracted text: `{section['extracted_text']}`")
            if section["snippets"]:
                md.append("- Innovation-related snippets:")
                for snip in section["snippets"][:8]:
                    md.append(f"  - {snip}")
            md.append("")
    else:
        md.append("No parseable PDF text found.")
        md.append("")

    md.append("## HFSS/Simulation Artifact Signals")
    md.append("")
    if code_sections:
        for section in code_sections[:80]:
            md.append(f"### {section['file']}")
            for label, hits in section["hits"].items():
                md.append(f"- {label}:")
                for hit in hits[:6]:
                    md.append(f"  - `{hit}`")
            md.append("")
    else:
        md.append("No HFSS-specific code signals found in text-readable artifacts.")
        md.append("")

    md.append("## Result Summaries")
    md.append("")
    if result_sections:
        for section in result_sections[:80]:
            md.append(f"### {section['file']}")
            md.append("```json")
            md.append(json.dumps(section["summary"], indent=2, ensure_ascii=False))
            md.append("```")
            md.append("")
    else:
        md.append("No CSV/Touchstone result summaries generated.")
        md.append("")

    md.append("## Innovation Map Template For Codex")
    md.append("")
    md.append("Fill this from the paper text and simulation artifacts:")
    md.append("")
    md.append(markdown_table([
        ["Claimed innovation", "Baseline", "Mechanism", "Implementation artifact", "Evidence", "Reusable skill lesson"],
        ["", "", "", "", "", ""],
    ]))
    md.append("")
    md.append("## Skill Improvement Candidate Template")
    md.append("")
    md.append(markdown_table([
        ["Trigger", "Reusable action", "Where to update", "Validation"],
        ["", "", "SKILL.md / references / scripts / templates", "quick_validate.py plus task-specific checks"],
    ]))
    md.append("")
    md.append("## Parsing Limitations")
    md.append("")
    if limitations:
        for item in limitations:
            md.append(f"- {item}")
    else:
        md.append("- None recorded by the analyzer. Semantic interpretation still requires Codex to read the summary and relevant source files.")
    md.append("")

    output.write_text("\n".join(md), encoding="utf-8")

    machine = {
        "bundle": str(bundle),
        "file_count": len(files),
        "papers": paper_sections,
        "code_sections": code_sections,
        "result_sections": result_sections,
        "limitations": limitations,
        "output": str(output),
    }
    if args.json:
        json_path = output.with_suffix(".json")
        json_path.write_text(json.dumps(machine, indent=2, ensure_ascii=False), encoding="utf-8")

    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())