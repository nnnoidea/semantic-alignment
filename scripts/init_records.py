#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from recordlib import atomic_write_json, atomic_write_text, empty_audit_state, record_lock


FILES = {
    "semantic-ledger.jsonl": "",
    "compromises.jsonl": "",
    "user-semantics.md": """# User Semantics

This is the complete current user-design baseline. It is generated from `semantic-ledger.jsonl`; edit the ledger through `scripts/record_event.py`.

No user semantics recorded yet.
""",
    "alignment-report.md": """# Alignment Report

This is the generated user-facing view. Full semantics live in `user-semantics.md`; reusable audit evidence lives in `audit-state.json`.

## Current Status

- Overall: not-audited
- Last audit: never
- Validity: no trusted audit has been finalized.
- Coverage: satisfied=0, partial=0, unmet=0, conflict=0, unknown=0

## Implementation Differences

No current implementation differences recorded.

## Relevant Compromises

No active compromises were relevant to the last audit. Active compromises retained internally: 0.
""",
}


def main():
    parser = argparse.ArgumentParser(
        description="Create v2 files in an already resolved project record directory."
    )
    parser.add_argument("record_dir", help="Path to <project-root>/.semantic-alignment/")
    args = parser.parse_args()

    record_dir = Path(args.record_dir)
    record_dir.mkdir(parents=True, exist_ok=True)

    with record_lock(record_dir):
        return initialize(record_dir)


def initialize(record_dir):

    legacy = [
        name
        for name in ("user-semantic-ledger.md", "realization-semantics.md", "artifact-checks.md", "audits.md")
        if (record_dir / name).exists()
    ]
    if legacy:
        print(
            "legacy v1 records found; run scripts/migrate_v1.py <record-dir> --apply before initialization: "
            + ", ".join(legacy),
            file=sys.stderr,
        )
        return 1

    written = []
    skipped = []
    for name, content in FILES.items():
        path = record_dir / name
        if path.exists():
            skipped.append(name)
            continue
        atomic_write_text(path, content)
        written.append(name)

    state_path = record_dir / "audit-state.json"
    if state_path.exists():
        skipped.append(state_path.name)
    else:
        atomic_write_json(state_path, empty_audit_state())
        written.append(state_path.name)

    for name in written:
        print(f"written: {name}")
    for name in skipped:
        print(f"skipped existing: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
