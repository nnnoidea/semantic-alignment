#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path


REQUIRED_FILES = [
    "index.md",
    "user-semantics.md",
    "user-semantic-ledger.md",
    "recheck-triggers.md",
    "realization-semantics.md",
    "artifact-checks.md",
    "audits.md",
]

LEDGER_HEADER = [
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
]

REALIZATION_HEADER = [
    "ID",
    "Realization semantics",
    "Scope",
    "Relation to user semantics",
    "Linked user semantics",
    "Rationale",
    "Status",
]

TRIGGERS_HEADER = ["ID", "Ledger ID", "Trigger", "Recheck method", "Status", "Last checked", "Notes"]
CHECKS_HEADER = ["ID", "Artifact", "Checked against", "Result", "Concrete note"]

OPERATIONS = {"add", "update", "delete"}
CATEGORIES = {
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
}
REASONS = {
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
}
CURRENT_VALUES = {"yes", "no"}
TRIGGER_STATUS = {"active", "unverified", "resolved", "superseded"}
RELATIONS = {"grounded", "added", "risky", "divergent"}
AGENT_STATUS = {"active", "rejected", "revised"}
CHECK_RESULTS = {"pass", "partial", "fail"}


def is_empty_trigger(value):
    normalized = value.strip().strip(".").strip().lower()
    return normalized in {"", "none", "n/a", "na", "-"}


def split_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


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


def find_table(path, expected_header):
    text = path.read_text(encoding="utf-8")
    for table in iter_tables(text):
        header = split_row(table[0])
        if header == expected_header:
            return table
    return None


def validate_table(path, expected_header, validators):
    errors = []
    table = find_table(path, expected_header)
    if not table:
        return [f"{path.name}: missing table with header {expected_header}"]

    seen_ids = {}
    for line_no, row in enumerate(table[2:], start=3):
        cells = split_row(row)
        if len(cells) != len(expected_header):
            errors.append(f"{path.name}:{line_no}: expected {len(expected_header)} cells, got {len(cells)}")
            continue
        record = dict(zip(expected_header, cells))
        record_id = record.get("ID")
        if record_id:
            if record_id in seen_ids:
                errors.append(f"{path.name}:{line_no}: duplicate ID {record_id!r}; first seen on line {seen_ids[record_id]}")
            else:
                seen_ids[record_id] = line_no
        for column, allowed in validators.items():
            value = record[column]
            if value not in allowed:
                errors.append(
                    f"{path.name}:{line_no}: invalid {column!r} value {value!r}; expected one of {sorted(allowed)}"
                )
    return errors


def table_rows(path, expected_header):
    table = find_table(path, expected_header)
    if not table:
        return []
    rows = []
    for row in table[2:]:
        cells = split_row(row)
        if len(cells) == len(expected_header):
            rows.append(dict(zip(expected_header, cells)))
    return rows


def validate_trigger_projection(record_dir):
    ledger_rows = table_rows(record_dir / "user-semantic-ledger.md", LEDGER_HEADER)
    trigger_rows = table_rows(record_dir / "recheck-triggers.md", TRIGGERS_HEADER)
    grouped = {}
    for row in ledger_rows:
        trigger = row["Recheck trigger"].strip()
        if row["Current?"] == "yes" and not is_empty_trigger(trigger):
            grouped.setdefault(trigger, []).append(row["ID"])
    expected = [(",".join(ids), trigger) for trigger, ids in grouped.items()]
    actual = [(row["Ledger ID"], row["Trigger"].strip()) for row in trigger_rows]
    if actual != expected:
        return [
            "recheck-triggers.md: projection is out of sync with current ledger triggers; "
            "run scripts/sync_triggers.py <record-dir>"
        ]
    return []


def validate_record_dir(record_dir):
    record_dir = Path(record_dir)
    errors = []
    if not record_dir.exists():
        return [f"record directory not found: {record_dir}"]
    if not record_dir.is_dir():
        return [f"not a directory: {record_dir}"]

    for name in REQUIRED_FILES:
        if not (record_dir / name).exists():
            errors.append(f"missing required file: {name}")

    if errors:
        return errors

    errors += validate_table(
        record_dir / "user-semantic-ledger.md",
        LEDGER_HEADER,
        {
            "Operation": OPERATIONS,
            "Category": CATEGORIES,
            "Reason": REASONS,
            "Current?": CURRENT_VALUES,
        },
    )
    errors += validate_table(
        record_dir / "recheck-triggers.md",
        TRIGGERS_HEADER,
        {
            "Status": TRIGGER_STATUS,
        },
    )
    errors += validate_trigger_projection(record_dir)
    errors += validate_table(
        record_dir / "realization-semantics.md",
        REALIZATION_HEADER,
        {
            "Relation to user semantics": RELATIONS,
            "Status": AGENT_STATUS,
        },
    )
    errors += validate_table(
        record_dir / "artifact-checks.md",
        CHECKS_HEADER,
        {
            "Result": CHECK_RESULTS,
        },
    )
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate semantic-alignment record files.")
    parser.add_argument("record_dir", help="Path to .semantic-alignment/<task-slug>/ or another writable record directory")
    args = parser.parse_args()

    errors = validate_record_dir(args.record_dir)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Semantic alignment records are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
