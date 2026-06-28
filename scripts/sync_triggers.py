#!/usr/bin/env python3
import argparse
import difflib
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

TRIGGERS_HEADER = ["ID", "Ledger ID", "Trigger", "Recheck method", "Status", "Last checked", "Notes"]

EMPTY_TRIGGERS = {"", "none", "n/a", "na", "-", "None", "N/A", "NA"}
DEFAULT_METHOD = "Review linked ledger entry and verify whether the trigger condition is true."
DEFAULT_LAST_CHECKED = "never"
DEFAULT_NOTES = "Generated from user-semantic-ledger.md."


def split_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def table_separator(column_count):
    return "| " + " | ".join(["---"] * column_count) + " |"


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
        if split_row(table[0]) == expected_header:
            return table
    return None


def rows_from_table(table, header):
    rows = []
    if not table:
        return rows
    for line in table[2:]:
        cells = split_row(line)
        if len(cells) == len(header):
            rows.append(dict(zip(header, cells)))
    return rows


def load_ledger_rows(record_dir):
    path = record_dir / "user-semantic-ledger.md"
    if not path.exists():
        raise FileNotFoundError(path)
    table = find_table(path, LEDGER_HEADER)
    if not table:
        raise ValueError(f"{path.name}: missing ledger table")
    return rows_from_table(table, LEDGER_HEADER)


def load_existing_trigger_rows(record_dir):
    path = record_dir / "recheck-triggers.md"
    if not path.exists():
        return []
    table = find_table(path, TRIGGERS_HEADER)
    return rows_from_table(table, TRIGGERS_HEADER)


def active_ledger_triggers(ledger_rows):
    triggers_by_text = {}
    for row in ledger_rows:
        trigger = row["Recheck trigger"].strip()
        if row["Current?"] == "yes" and not is_empty_trigger(trigger):
            triggers_by_text.setdefault(trigger, []).append(row["ID"])
    return [(ledger_ids, trigger) for trigger, ledger_ids in triggers_by_text.items()]


def is_empty_trigger(value):
    normalized = value.strip().strip(".").strip().lower()
    return normalized in {"", "none", "n/a", "na", "-"}


def build_trigger_rows(ledger_rows, existing_rows):
    existing_by_key = {(row["Ledger ID"], row["Trigger"]): row for row in existing_rows}
    existing_by_trigger = {row["Trigger"]: row for row in existing_rows}
    generated = []
    for index, (ledger_ids, trigger) in enumerate(active_ledger_triggers(ledger_rows), start=1):
        ledger_id_text = ",".join(ledger_ids)
        previous = existing_by_key.get((ledger_id_text, trigger), existing_by_trigger.get(trigger, {}))
        generated.append(
            {
                "ID": f"T{index}",
                "Ledger ID": ledger_id_text,
                "Trigger": trigger,
                "Recheck method": previous.get("Recheck method", DEFAULT_METHOD),
                "Status": previous.get("Status", "active"),
                "Last checked": previous.get("Last checked", DEFAULT_LAST_CHECKED),
                "Notes": previous.get("Notes", DEFAULT_NOTES),
            }
        )
    return generated


def render(rows):
    lines = [
        "# Recheck Triggers",
        "",
        "This file is generated from current rows in `user-semantic-ledger.md`. Do not add or remove trigger rows by hand; edit trigger presence/text in the ledger and run `scripts/sync_triggers.py`. You may edit `Recheck method`, `Status`, `Last checked`, and `Notes`; the sync script preserves those fields for matching triggers.",
        "",
        "| " + " | ".join(TRIGGERS_HEADER) + " |",
        table_separator(len(TRIGGERS_HEADER)),
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[column] for column in TRIGGERS_HEADER) + " |")
    return "\n".join(lines) + "\n"


def sync(record_dir, check=False):
    ledger_rows = load_ledger_rows(record_dir)
    existing_rows = load_existing_trigger_rows(record_dir)
    generated = render(build_trigger_rows(ledger_rows, existing_rows))
    target = record_dir / "recheck-triggers.md"
    current = target.read_text(encoding="utf-8") if target.exists() else ""

    if check:
        if current != generated:
            diff = difflib.unified_diff(
                current.splitlines(),
                generated.splitlines(),
                fromfile=str(target),
                tofile=f"{target} (generated)",
                lineterm="",
            )
            for line in diff:
                print(line)
            return 1
        print("Recheck triggers are in sync.")
        return 0

    target.write_text(generated, encoding="utf-8", newline="\n")
    print(f"synced: {target}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Generate recheck-triggers.md from user-semantic-ledger.md.")
    parser.add_argument("record_dir", help="Path to .semantic-alignment/<task-slug>/ or another record directory")
    parser.add_argument("--check", action="store_true", help="Only check whether recheck-triggers.md is already in sync")
    args = parser.parse_args()

    try:
        return sync(Path(args.record_dir), check=args.check)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
