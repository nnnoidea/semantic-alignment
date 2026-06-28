#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


TABLES = {
    "ledger": {
        "file": "user-semantic-ledger.md",
        "header": [
            "ID",
            "Date",
            "Operation",
            "Category",
            "Before",
            "After",
            "Reason",
            "Source",
            "Current?",
            "Recheck trigger",
        ],
        "prefix": "U",
    },
    "realization": {
        "file": "realization-semantics.md",
        "header": [
            "ID",
            "Realization semantics",
            "Scope",
            "Relation to user semantics",
            "Linked user semantics",
            "Rationale",
            "Status",
        ],
        "prefix": "R",
        "jsonl": "structured/realization-semantics.jsonl",
    },
    "check": {
        "file": "artifact-checks.md",
        "header": ["ID", "Artifact", "Checked against", "Result", "Concrete note"],
        "prefix": "K",
        "jsonl": "structured/artifact-checks.jsonl",
    },
}

ALLOWED = {
    "operation": {"add", "update", "delete"},
    "category": {
        "goal",
        "principle",
        "context",
        "global-design",
        "local-design",
        "system",
        "content",
        "process",
        "constraint",
        "review",
    },
    "reason": {
        "clarification",
        "correction",
        "optimization",
        "constraint",
        "implementation-discovery",
        "agent-inference",
        "scope-control",
        "preference-change",
        "deletion",
        "unknown",
    },
    "current": {"yes", "no"},
    "relation": {"grounded", "added", "risky", "divergent"},
    "status": {"active", "rejected", "revised"},
    "result": {"pass", "partial", "fail"},
}


def split_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def iter_tables(lines):
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("|"):
            start = i
            table = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                table.append(lines[i])
                i += 1
            if len(table) >= 2:
                yield start, i, table
        else:
            i += 1


def find_table(lines, expected_header):
    for start, end, table in iter_tables(lines):
        if split_row(table[0]) == expected_header:
            return start, end, table
    return None


def markdown_cell(value):
    text = str(value).replace("\r\n", " ").replace("\n", " ").strip()
    return text.replace("|", "\\|")


def existing_ids(table, header):
    ids = []
    for line in table[2:]:
        cells = split_row(line)
        if len(cells) == len(header):
            ids.append(cells[0])
    return ids


def next_id(ids, prefix):
    numbers = []
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
    for value in ids:
        match = pattern.match(value)
        if match:
            numbers.append(int(match.group(1)))
    return f"{prefix}{max(numbers, default=0) + 1}"


def infer_realization_prefix(ids):
    has_a = any(re.match(r"^A\d+$", value) for value in ids)
    has_r = any(re.match(r"^R\d+$", value) for value in ids)
    if has_a and not has_r:
        return "A"
    return "R"


def validate_choice(name, value):
    allowed = ALLOWED[name]
    if value not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(f"invalid {name}: {value!r}; expected one of: {choices}")


def append_row(record_dir, kind, values, record_id=None, prefix=None, mirror_jsonl=True):
    config = TABLES[kind]
    path = record_dir / config["file"]
    if not path.exists():
        raise FileNotFoundError(path)

    lines = path.read_text(encoding="utf-8").splitlines()
    found = find_table(lines, config["header"])
    if not found:
        raise ValueError(f"{path.name}: missing table with expected header")
    _start, end, table = found

    ids = existing_ids(table, config["header"])
    chosen_prefix = prefix or config["prefix"]
    if kind == "realization" and prefix is None:
        chosen_prefix = infer_realization_prefix(ids)
    row_id = record_id or next_id(ids, chosen_prefix)
    if row_id in ids:
        raise ValueError(f"{path.name}: duplicate ID would be created: {row_id}")

    row = {"ID": row_id, **values}
    markdown_row = "| " + " | ".join(markdown_cell(row[column]) for column in config["header"]) + " |"
    lines.insert(end, markdown_row)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    if mirror_jsonl and "jsonl" in config:
        write_jsonl(record_dir / config["jsonl"], row)

    print(f"appended {row_id} to {path.name}")
    return row_id


def write_jsonl(path, row):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def add_ledger_parser(subparsers):
    parser = subparsers.add_parser("ledger", help="Append a user semantic ledger row")
    parser.add_argument("--id")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--operation", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--current", default="yes")
    parser.add_argument("--recheck-trigger", default="None.")


def add_realization_parser(subparsers):
    parser = subparsers.add_parser("realization", help="Append a realization semantics row")
    parser.add_argument("--id")
    parser.add_argument("--prefix")
    parser.add_argument("--semantics", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--relation", required=True)
    parser.add_argument("--linked-user-semantics", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--status", default="active")
    parser.add_argument("--no-jsonl", action="store_true")


def add_check_parser(subparsers):
    parser = subparsers.add_parser("check", help="Append an artifact check row")
    parser.add_argument("--id")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--checked-against", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("--note", required=True)
    parser.add_argument("--no-jsonl", action="store_true")


def main():
    parser = argparse.ArgumentParser(description="Append fixed-format semantic-alignment record rows.")
    parser.add_argument("record_dir", help="Path to .semantic-alignment/<task-slug>/ or another record directory")
    subparsers = parser.add_subparsers(dest="kind", required=True)
    add_ledger_parser(subparsers)
    add_realization_parser(subparsers)
    add_check_parser(subparsers)
    args = parser.parse_args()

    record_dir = Path(args.record_dir)
    try:
        if args.kind == "ledger":
            validate_choice("operation", args.operation)
            validate_choice("category", args.category)
            validate_choice("reason", args.reason)
            validate_choice("current", args.current)
            append_row(
                record_dir,
                "ledger",
                {
                    "Date": args.date,
                    "Operation": args.operation,
                    "Category": args.category,
                    "Before": args.before,
                    "After": args.after,
                    "Reason": args.reason,
                    "Source": args.source,
                    "Current?": args.current,
                    "Recheck trigger": args.recheck_trigger,
                },
                record_id=args.id,
            )
        elif args.kind == "realization":
            validate_choice("relation", args.relation)
            validate_choice("status", args.status)
            append_row(
                record_dir,
                "realization",
                {
                    "Realization semantics": args.semantics,
                    "Scope": args.scope,
                    "Relation to user semantics": args.relation,
                    "Linked user semantics": args.linked_user_semantics,
                    "Rationale": args.rationale,
                    "Status": args.status,
                },
                record_id=args.id,
                prefix=args.prefix,
                mirror_jsonl=not args.no_jsonl,
            )
        elif args.kind == "check":
            validate_choice("result", args.result)
            append_row(
                record_dir,
                "check",
                {
                    "Artifact": args.artifact,
                    "Checked against": args.checked_against,
                    "Result": args.result,
                    "Concrete note": args.note,
                },
                record_id=args.id,
                mirror_jsonl=not args.no_jsonl,
            )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
