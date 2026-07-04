#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


TABLES = {
    "realization-semantics.md": [
        "ID",
        "Realization semantics",
        "Scope",
        "Relation to user semantics",
        "Linked user semantics",
        "Rationale",
        "Status",
    ],
    "artifact-checks.md": ["ID", "Artifact", "Checked against", "Result", "Concrete note"],
    "recheck-triggers.md": ["ID", "Ledger ID", "Trigger", "Recheck method", "Status", "Last checked", "Notes"],
}


def split_row(line):
    return [cell.strip().replace("\\|", "|") for cell in line.strip().strip("|").split("|")]


def iter_tables(text):
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|"):
            table = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                table.append(lines[i])
                i += 1
            if len(table) >= 2:
                yield table
        else:
            i += 1


def table_rows(path, header):
    text = path.read_text(encoding="utf-8")
    for table in iter_tables(text):
        if split_row(table[0]) == header:
            rows = []
            for line in table[2:]:
                cells = split_row(line)
                if len(cells) == len(header):
                    rows.append(dict(zip(header, cells)))
            return rows
    raise ValueError(f"{path.name}: missing table with expected header")


def export(record_dir):
    output_dir = record_dir / "structured"
    output_dir.mkdir(exist_ok=True)
    written = []
    for filename, header in TABLES.items():
        source = record_dir / filename
        if not source.exists():
            raise FileNotFoundError(source)
        rows = table_rows(source, header)
        target = output_dir / f"{source.stem}.jsonl"
        with target.open("w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        written.append(target)
    return written


def main():
    parser = argparse.ArgumentParser(description="Export selected semantic-alignment records to structured JSONL mirrors.")
    parser.add_argument("record_dir", help="Path to .semantic-alignment/<project-slug>/ or another record directory")
    args = parser.parse_args()

    try:
        for path in export(Path(args.record_dir)):
            print(f"written: {path}")
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
