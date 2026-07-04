#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


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

USER_COVERAGE_HEADER = ["User semantic ID", "Coverage", "Evidence", "Notes"]
REALIZATION_COVERAGE_HEADER = ["Realization ID", "Grounding", "User basis", "Conflict", "Notes"]
REALIZATION_REFRESH_HEADER = ["Refresh item", "Status", "Evidence", "Notes"]

USER_COVERAGE_VALUES = {"satisfied", "partial", "unmet", "conflict", "unknown"}
REALIZATION_GROUNDING_VALUES = {"direct", "aligned-addition", "risky-addition", "conflict", "unknown"}
CONFLICT_VALUES = {"yes", "no", "unknown"}
REFRESH_ITEMS = ["inspect-real-project", "update-realization-semantics", "refresh-artifact-checks"]
REFRESH_STATUS_VALUES = {"done", "unchanged"}
EMPTY_EVIDENCE = {"", "none", "n/a", "na", "-", "tbd", "unknown"}


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


def find_table(text, expected_header):
    for table in iter_tables(text):
        if split_row(table[0]) == expected_header:
            return table
    return None


def table_rows(text, expected_header):
    table = find_table(text, expected_header)
    if not table:
        return []
    rows = []
    for line in table[2:]:
        cells = split_row(line)
        if len(cells) == len(expected_header):
            rows.append(dict(zip(expected_header, cells)))
    return rows


def latest_audit_event(text):
    matches = list(re.finditer(r"(?m)^### (\d{4}-\d{2}-\d{2}) - .+$", text))
    if not matches:
        return None
    starts = [match.start() for match in matches] + [len(text)]
    events = []
    for index, match in enumerate(matches):
        events.append((match.group(1), match.start(), text[match.start() : starts[index + 1]]))
    _date, _start, event = max(events, key=lambda item: (item[0], item[1]))
    return event


def normalize_id(value):
    return value.strip().strip("`").strip()


def expected_user_ids(record_dir):
    text = (record_dir / "user-semantic-ledger.md").read_text(encoding="utf-8")
    ids = []
    for row in table_rows(text, LEDGER_HEADER):
        if row["Current?"] == "yes" and row["Operation"] != "delete":
            ids.append(row["ID"])
    return ids


def expected_realization_ids(record_dir):
    text = (record_dir / "realization-semantics.md").read_text(encoding="utf-8")
    ids = []
    for row in table_rows(text, REALIZATION_HEADER):
        if row["Status"] == "active":
            ids.append(row["ID"])
    return ids


def check_coverage_rows(rows, id_column, status_columns, expected_ids):
    errors = []
    seen = {}
    expected_set = set(expected_ids)

    for row in rows:
        row_id = normalize_id(row[id_column])
        if row_id in seen:
            errors.append(f"{id_column}: duplicate coverage row for {row_id}")
        seen[row_id] = row
        if row_id not in expected_set:
            errors.append(f"{id_column}: unexpected ID in coverage table: {row_id}")
        for column, allowed in status_columns.items():
            value = row[column]
            if value not in allowed:
                errors.append(
                    f"{row_id}: invalid {column!r} value {value!r}; expected one of {sorted(allowed)}"
                )

    actual_set = set(seen)
    missing = [record_id for record_id in expected_ids if record_id not in actual_set]
    if missing:
        errors.append(f"{id_column}: missing coverage rows for {', '.join(missing)}")
    return errors


def check_realization_refresh(rows):
    errors = []
    seen = {}
    required = set(REFRESH_ITEMS)
    for row in rows:
        item = normalize_id(row["Refresh item"])
        if item in seen:
            errors.append(f"Realization Refresh: duplicate refresh item {item}")
        seen[item] = row
        if item not in required:
            errors.append(f"Realization Refresh: unexpected refresh item {item}")
        status = row["Status"]
        if status not in REFRESH_STATUS_VALUES:
            errors.append(
                f"Realization Refresh {item}: invalid status {status!r}; expected one of {sorted(REFRESH_STATUS_VALUES)}"
            )
        evidence = row["Evidence"].strip().strip(".").lower()
        if evidence in EMPTY_EVIDENCE:
            errors.append(f"Realization Refresh {item}: evidence must be concrete, not {row['Evidence']!r}")

    missing = [item for item in REFRESH_ITEMS if item not in seen]
    if missing:
        errors.append(f"Realization Refresh: missing rows for {', '.join(missing)}")
    return errors


def check(record_dir):
    record_dir = Path(record_dir)
    audits_path = record_dir / "audits.md"
    if not audits_path.exists():
        return [f"missing file: {audits_path.name}"]

    audits_text = audits_path.read_text(encoding="utf-8")
    event_text = latest_audit_event(audits_text)
    if not event_text:
        return ["audits.md: no dated audit event found"]

    refresh_rows = table_rows(event_text, REALIZATION_REFRESH_HEADER)
    if not refresh_rows:
        return ["latest audit event: missing Realization Refresh table"]

    user_rows = table_rows(event_text, USER_COVERAGE_HEADER)
    if not user_rows:
        return ["latest audit event: missing User Semantic Coverage table"]

    realization_rows = table_rows(event_text, REALIZATION_COVERAGE_HEADER)
    if not realization_rows:
        return ["latest audit event: missing Realization Semantic Coverage table"]

    errors = []
    errors += check_realization_refresh(refresh_rows)
    errors += check_coverage_rows(
        user_rows,
        "User semantic ID",
        {"Coverage": USER_COVERAGE_VALUES},
        expected_user_ids(record_dir),
    )
    errors += check_coverage_rows(
        realization_rows,
        "Realization ID",
        {"Grounding": REALIZATION_GROUNDING_VALUES, "Conflict": CONFLICT_VALUES},
        expected_realization_ids(record_dir),
    )
    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Check that the latest full audit event covers every current user semantic and active realization semantic."
    )
    parser.add_argument("record_dir", help="Path to .semantic-alignment/<project-slug>/ or another record directory")
    args = parser.parse_args()

    errors = check(Path(args.record_dir))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Audit coverage is exhaustive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
