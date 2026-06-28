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

EMPTY_TRIGGERS = {"", "none", "n/a", "na", "-"}
ACTION_TRIGGER_PATTERNS = [
    r"^\s*if\b.*\b(consider|use|run|add|move|revise|repair|handle|tighten|switch|merge|archive)\b",
    r"\b(todo|to do|pending|remains open|is still open|recommendation)\b",
    r"\b(should|need to|needs to)\s+(consider|use|run|add|move|revise|repair|handle|tighten|switch|merge|archive)\b",
]
STOPWORDS = {
    "about",
    "accepted",
    "agent",
    "because",
    "before",
    "current",
    "detail",
    "details",
    "semantic",
    "semantics",
    "should",
    "state",
    "their",
    "there",
    "these",
    "those",
    "user",
    "users",
    "which",
    "with",
}


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
        if split_row(table[0]) == expected_header:
            return table
    return None


def table_rows(path, expected_header):
    table = find_table(path, expected_header)
    if not table:
        return []
    rows = []
    for line in table[2:]:
        cells = split_row(line)
        if len(cells) == len(expected_header):
            rows.append(dict(zip(expected_header, cells)))
    return rows


def is_empty_trigger(value):
    normalized = value.strip().strip(".").strip().lower()
    return normalized in EMPTY_TRIGGERS


def content_tokens(text):
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", text.lower())
    return {token for token in tokens if token not in STOPWORDS}


def lint_triggers(rows):
    warnings = []
    for row in rows:
        trigger = row["Recheck trigger"].strip()
        if row["Current?"] != "yes" or is_empty_trigger(trigger):
            continue
        lowered = trigger.lower()
        for pattern in ACTION_TRIGGER_PATTERNS:
            if re.search(pattern, lowered):
                warnings.append(
                    f"{row['ID']}: recheck trigger looks like an action/task, not an observable condition: {trigger}"
                )
                break
    return warnings


def lint_user_projection(rows, user_text):
    warnings = []
    user_tokens = content_tokens(user_text)
    for row in rows:
        if row["Current?"] != "yes" or row["Operation"] == "delete":
            continue
        if row["Category"] not in {"goal", "principle", "global-design", "local-design", "system", "content", "process", "constraint", "review"}:
            continue
        after_tokens = content_tokens(row["After"])
        if len(after_tokens) < 3:
            continue
        overlap = after_tokens & user_tokens
        if len(overlap) < min(2, len(after_tokens)):
            warnings.append(
                f"{row['ID']}: active ledger entry may be missing from user-semantics.md projection: {row['After']}"
            )
    return warnings


def lint(record_dir):
    record_dir = Path(record_dir)
    ledger_path = record_dir / "user-semantic-ledger.md"
    user_path = record_dir / "user-semantics.md"
    if not ledger_path.exists():
        return [f"missing file: {ledger_path.name}"]
    if not user_path.exists():
        return [f"missing file: {user_path.name}"]
    if not find_table(ledger_path, LEDGER_HEADER):
        return [f"{ledger_path.name}: missing ledger table"]
    rows = table_rows(ledger_path, LEDGER_HEADER)
    user_text = user_path.read_text(encoding="utf-8")
    return lint_triggers(rows) + lint_user_projection(rows, user_text)


def main():
    parser = argparse.ArgumentParser(description="Lint semantic-alignment records for semantic-quality risks.")
    parser.add_argument("record_dir", help="Path to .semantic-alignment/<task-slug>/ or another record directory")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when warnings are found")
    args = parser.parse_args()

    warnings = lint(args.record_dir)
    if warnings:
        for warning in warnings:
            print(f"warning: {warning}")
        return 1 if args.strict else 0
    print("Semantic alignment records passed lint checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
