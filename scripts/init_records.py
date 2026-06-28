#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path


FILES = {
    "index.md": """# {title}

## Current Semantic Frame

### Goal

TBD

### Global Semantics

- TBD

### Local Semantics

- TBD

### Known Unknowns

- TBD
""",
    "user-semantics.md": """# User Semantics

This is the current user-semantic baseline. Keep it readable for the user. Do not put history or agent rationale here.

## Goal

TBD

## Principles

- TBD

## Context

- TBD

## Global Design Semantics

- TBD

## Local Semantics

- TBD

## Constraints

- TBD

## Review Semantics

- TBD

## User Review Focus

- TBD
""",
    "user-semantic-ledger.md": """# User Semantic Ledger

This file records user semantic changes, not every user input. Use `add`, `update`, or `delete`; include the reason.

## Ledger

| ID | Date | Operation | Category | Before | After | Reason | Source | Current? | Recheck trigger |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
""",
    "recheck-triggers.md": """# Recheck Triggers

This file is generated from current rows in `user-semantic-ledger.md`. Do not add or remove trigger rows by hand; edit trigger presence/text in the ledger and run `scripts/sync_triggers.py`. You may edit `Recheck method`, `Status`, `Last checked`, and `Notes`; the sync script preserves those fields for matching triggers.

| ID | Ledger ID | Trigger | Recheck method | Status | Last checked | Notes |
| --- | --- | --- | --- | --- | --- | --- |
""",
    "realization-semantics.md": """# Realization Semantics

Realization semantics are intended artifact semantics: what the agent believes the produced artifact should mean after interpreting user semantics and filling implementation/design gaps.

| ID | Realization semantics | Scope | Relation to user semantics | Linked user semantics | Rationale | Status |
| --- | --- | --- | --- | --- | --- | --- |
""",
    "artifact-checks.md": """# Artifact Checks

This is a mechanical check log comparing real artifacts with `realization-semantics.md`. Put synthesis in `audits.md`.

| ID | Artifact | Checked against | Result | Concrete note |
| --- | --- | --- | --- | --- |
""",
    "audits.md": """# Audits

## Current Audit Summary

- Overall status: TBD
- Open drift: TBD
- Open contradictions: TBD
- Reopen triggers: TBD
- Current recommendations: TBD

## Audit Events

No audit events recorded yet.
""",
}


def main():
    parser = argparse.ArgumentParser(description="Create semantic-alignment record files with fixed headers.")
    parser.add_argument("record_dir", help="Path to .semantic-alignment/<task-slug>/ or another writable record directory")
    parser.add_argument("--title", default="Semantic Alignment Records", help="Title for index.md")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    record_dir = Path(args.record_dir)
    record_dir.mkdir(parents=True, exist_ok=True)

    written = []
    skipped = []
    for name, template in FILES.items():
        path = record_dir / name
        if path.exists() and not args.force:
            skipped.append(name)
            continue
        path.write_text(template.format(title=args.title), encoding="utf-8", newline="\n")
        written.append(name)

    for name in written:
        print(f"written: {name}")
    for name in skipped:
        print(f"skipped existing: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
