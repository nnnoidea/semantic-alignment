#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from recordlib import (
    append_jsonl,
    atomic_write_json,
    atomic_write_text,
    current_compromises,
    current_semantics,
    empty_audit_state,
    latest_by_id,
    load_audit_state,
    next_prefixed_id,
    read_jsonl,
    record_lock,
    render_alignment_report,
    render_user_semantics,
    save_audit_state,
    SEMANTIC_CATEGORIES,
    SEMANTIC_REASONS,
    utc_now,
)


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
TRIGGER_HEADER = ["ID", "Ledger ID", "Trigger", "Recheck method", "Status", "Last checked", "Notes"]
LEGACY_NAMES = [
    "index.md",
    "user-semantics.md",
    "user-semantic-ledger.md",
    "recheck-triggers.md",
    "realization-semantics.md",
    "artifact-checks.md",
    "audits.md",
    "structured",
]


def split_row(line):
    cells = []
    current = []
    text = line.strip().strip("|")
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text) and text[index + 1] in {"\\", "|"}:
            current.append(text[index + 1])
            index += 2
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
        index += 1
    cells.append("".join(current).strip())
    return cells


def table_rows(path, header, required_header=False):
    if not path.exists():
        if required_header:
            raise ValueError(f"{path.name}: required legacy file was not found")
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("|") or split_row(line) != header:
            continue
        rows = []
        for candidate in lines[index + 2 :]:
            if not candidate.lstrip().startswith("|"):
                break
            cells = split_row(candidate)
            if len(cells) != len(header):
                raise ValueError(
                    f"{path.name}: malformed table row after header; expected {len(header)} cells, got {len(cells)}"
                )
            rows.append(dict(zip(header, cells)))
        return rows
    if required_header:
        raise ValueError(f"{path.name}: expected legacy table header was not found")
    return []


def is_empty(value):
    return value.strip().strip(".").lower() in {"", "none", "n/a", "na", "-"}


def migration_plan(record_dir):
    legacy = [name for name in LEGACY_NAMES if (record_dir / name).exists()]
    rows = table_rows(record_dir / "user-semantic-ledger.md", LEDGER_HEADER, required_header=True)
    current = [
        row
        for row in rows
        if row.get("Current?", "").strip().lower() == "yes"
        and row.get("Operation", "").strip().lower() != "delete"
    ]
    seen = set()
    for row in current:
        semantic_id = row.get("ID", "")
        if not semantic_id:
            raise ValueError("legacy current semantic ID must not be empty")
        if semantic_id in seen:
            raise ValueError(f"duplicate current semantic ID in legacy ledger: {semantic_id}")
        seen.add(semantic_id)
        if row.get("Category") not in SEMANTIC_CATEGORIES:
            raise ValueError(f"invalid category for {semantic_id}: {row.get('Category')!r}")
        if row.get("Reason") not in SEMANTIC_REASONS:
            raise ValueError(f"invalid reason for {semantic_id}: {row.get('Reason')!r}")
        if is_empty(row.get("After", "")):
            raise ValueError(f"current semantic {semantic_id} has no current text")
    triggers = [row for row in current if not is_empty(row.get("Recheck trigger", ""))]
    return legacy, current, triggers


def allocate_semantic_ids(rows, reserved=()):
    used = set(reserved)
    mapping = {}
    for row in rows:
        legacy_id = row["ID"]
        candidate = legacy_id if re.fullmatch(r"U\d+", legacy_id) else None
        if candidate is None or candidate in used:
            candidate = next_prefixed_id(used, "U")
        used.add(candidate)
        mapping[legacy_id] = candidate
    return mapping


def archive_name(record_dir, source_label):
    safe_label = re.sub(r"[^a-z0-9]+", "-", source_label.lower()).strip("-") or "records"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = record_dir / "archive" / f"legacy-v1-{safe_label}-{stamp}"
    candidate = base
    suffix = 2
    while candidate.exists():
        candidate = Path(f"{base}-{suffix}")
        suffix += 1
    return candidate


def apply_migration(record_dir):
    if (record_dir / "semantic-ledger.jsonl").exists():
        raise ValueError("v2 semantic-ledger.jsonl already exists; refusing to overwrite")
    legacy, current, trigger_rows = migration_plan(record_dir)
    if "user-semantic-ledger.md" not in legacy:
        raise ValueError("user-semantic-ledger.md not found; this does not look like a v1 record directory")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = record_dir / "archive" / f"legacy-v1-{stamp}"
    with tempfile.TemporaryDirectory(prefix=".semantic-alignment-migration-", dir=record_dir.parent) as temporary:
        staged = Path(temporary)
        atomic_write_text(staged / "semantic-ledger.jsonl", "")
        atomic_write_text(staged / "compromises.jsonl", "")
        atomic_write_json(staged / "audit-state.json", empty_audit_state())

        id_mapping = allocate_semantic_ids(current)
        for row in current:
            append_jsonl(
                staged / "semantic-ledger.jsonl",
                {
                    "semantic_id": id_mapping[row["ID"]],
                    "revision": 1,
                    "date": row["Date"],
                    "operation": "add",
                    "category": row["Category"],
                    "before": None,
                    "text": row["After"],
                    "related": [],
                    "reason": row["Reason"],
                    "source": f"Migrated from legacy {row['ID']}: {row['Source']}",
                    "recorded_at": utc_now(),
                },
            )

        trigger_metadata = {
            row["Trigger"]: row for row in table_rows(record_dir / "recheck-triggers.md", TRIGGER_HEADER)
        }
        for index, row in enumerate(trigger_rows, start=1):
            trigger = row["Recheck trigger"]
            metadata = trigger_metadata.get(trigger, {})
            before = row["Before"]
            append_jsonl(
                staged / "compromises.jsonl",
                {
                    "compromise_id": f"C{index}",
                    "revision": 1,
                    "date": row["Date"],
                    "operation": "add",
                    "original_target": before if not is_empty(before) else f"See archived legacy ledger entry {row['ID']}",
                    "actual_choice": row["After"],
                    "gap": "Legacy records did not isolate the compromise gap; verify it when the recheck condition becomes relevant.",
                    "reason": row["Source"],
                    "evidence": f"archive/{archive.name}/user-semantic-ledger.md ({row['ID']})",
                    "scope": "legacy migration",
                    "affected_user_semantics": [id_mapping[row["ID"]]],
                    "recheck_condition": trigger,
                    "recheck_method": metadata.get("Recheck method", "Inspect current artifacts and constraint evidence."),
                    "status": "active",
                    "last_checked": metadata.get("Last checked", "never"),
                    "recorded_at": utc_now(),
                },
            )

        atomic_write_text(staged / "user-semantics.md", render_user_semantics(staged))
        atomic_write_text(staged / "alignment-report.md", render_alignment_report(staged))

        from validate_records import validate

        errors = validate(staged)
        if errors:
            raise ValueError("staged v2 records are invalid:\n- " + "\n- ".join(errors))

        archive.mkdir(parents=True, exist_ok=False)
        for name in legacy:
            source = record_dir / name
            shutil.move(str(source), str(archive / name))
        for name in ("semantic-ledger.jsonl", "compromises.jsonl", "audit-state.json", "user-semantics.md", "alignment-report.md"):
            shutil.move(str(staged / name), str(record_dir / name))

    return archive, len(current), len(trigger_rows)


def require_v2(record_dir):
    required = [
        "semantic-ledger.jsonl",
        "compromises.jsonl",
        "audit-state.json",
        "user-semantics.md",
        "alignment-report.md",
    ]
    missing = [name for name in required if not (record_dir / name).is_file()]
    if missing:
        raise ValueError("target is not a complete v2 record set: " + ", ".join(missing))


def merge_plan(source_dir, target_dir):
    legacy, current, triggers = migration_plan(source_dir)
    require_v2(target_dir)
    target_current = current_semantics(target_dir)
    existing_by_value = {
        (event.get("category"), event.get("text")): semantic_id
        for semantic_id, event in target_current.items()
    }
    duplicates = [
        row["ID"]
        for row in current
        if (row.get("Category"), row.get("After")) in existing_by_value
    ]
    return legacy, current, triggers, duplicates


def merge_migration(source_dir, target_dir, source_label, archive_only=False):
    source_dir = source_dir.resolve()
    target_dir = target_dir.resolve()
    if source_dir == target_dir:
        raise ValueError("--into target must differ from the legacy source directory")
    if source_dir in target_dir.parents:
        raise ValueError("--into target must not be inside the legacy source directory")
    legacy, current, trigger_rows, duplicates = merge_plan(source_dir, target_dir)
    if "user-semantic-ledger.md" not in legacy:
        raise ValueError("user-semantic-ledger.md not found; this does not look like a v1 record directory")

    destination_archive = archive_name(target_dir, source_label)
    with tempfile.TemporaryDirectory(prefix=".semantic-alignment-merge-", dir=target_dir.parent) as temporary:
        staged = Path(temporary)
        for name in (
            "semantic-ledger.jsonl",
            "compromises.jsonl",
            "audit-state.json",
            "user-semantics.md",
            "alignment-report.md",
        ):
            shutil.copy2(target_dir / name, staged / name)

        imported = 0
        compromise_count = 0
        if not archive_only:
            events = read_jsonl(staged / "semantic-ledger.jsonl")
            latest = latest_by_id(events, "semantic_id")
            active = current_semantics(staged)
            existing_by_value = {
                (event.get("category"), event.get("text")): semantic_id
                for semantic_id, event in active.items()
            }
            id_mapping = {}
            used_ids = set(latest)
            for row in current:
                key = (row["Category"], row["After"])
                if key in existing_by_value:
                    id_mapping[row["ID"]] = existing_by_value[key]
                    continue
                semantic_id = next_prefixed_id(used_ids, "U")
                used_ids.add(semantic_id)
                id_mapping[row["ID"]] = semantic_id
                append_jsonl(
                    staged / "semantic-ledger.jsonl",
                    {
                        "semantic_id": semantic_id,
                        "revision": 1,
                        "date": row["Date"],
                        "operation": "add",
                        "category": row["Category"],
                        "before": None,
                        "text": row["After"],
                        "related": [],
                        "reason": row["Reason"],
                        "source": f"Migrated from legacy {source_label} {row['ID']}: {row['Source']}",
                        "recorded_at": utc_now(),
                    },
                )
                existing_by_value[key] = semantic_id
                imported += 1

            trigger_metadata = {
                row["Trigger"]: row
                for row in table_rows(source_dir / "recheck-triggers.md", TRIGGER_HEADER)
            }
            compromise_events = read_jsonl(staged / "compromises.jsonl")
            used_compromise_ids = {
                item.get("compromise_id") for item in compromise_events if item.get("compromise_id")
            }
            active_compromise_keys = {
                (
                    item.get("recheck_condition"),
                    item.get("actual_choice"),
                    tuple(item.get("affected_user_semantics", [])),
                )
                for item in current_compromises(staged).values()
            }
            for row in trigger_rows:
                trigger = row["Recheck trigger"]
                metadata = trigger_metadata.get(trigger, {})
                affected = [id_mapping[row["ID"]]]
                key = (trigger, row["After"], tuple(affected))
                if key in active_compromise_keys:
                    continue
                compromise_id = next_prefixed_id(used_compromise_ids, "C")
                used_compromise_ids.add(compromise_id)
                append_jsonl(
                    staged / "compromises.jsonl",
                    {
                        "compromise_id": compromise_id,
                        "revision": 1,
                        "date": row["Date"],
                        "operation": "add",
                        "original_target": row["Before"]
                        if not is_empty(row["Before"])
                        else f"See archived legacy ledger entry {row['ID']}",
                        "actual_choice": row["After"],
                        "gap": "Legacy records did not isolate the compromise gap; verify it when the recheck condition becomes relevant.",
                        "reason": row["Source"],
                        "evidence": f"archive/{destination_archive.name}/user-semantic-ledger.md ({row['ID']})",
                        "scope": f"legacy migration: {source_label}",
                        "affected_user_semantics": affected,
                        "recheck_condition": trigger,
                        "recheck_method": metadata.get(
                            "Recheck method", "Inspect current artifacts and constraint evidence."
                        ),
                        "status": "active",
                        "last_checked": metadata.get("Last checked", "never"),
                        "recorded_at": utc_now(),
                    },
                )
                active_compromise_keys.add(key)
                compromise_count += 1

            atomic_write_text(staged / "user-semantics.md", render_user_semantics(staged))
            state = load_audit_state(staged)
            if state.get("last_audit"):
                state["last_audit"]["current"] = False
                invalidated = set(state["last_audit"].get("invalidated_by", []))
                invalidated.add(f"legacy-merge:{source_label}")
                state["last_audit"]["invalidated_by"] = sorted(invalidated)
                save_audit_state(staged, state)
            atomic_write_text(staged / "alignment-report.md", render_alignment_report(staged))

            from validate_records import validate

            errors = validate(staged)
            if errors:
                raise ValueError("staged merged v2 records are invalid:\n- " + "\n- ".join(errors))

        destination_archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source_dir, destination_archive)
        if not archive_only:
            for name in (
                "semantic-ledger.jsonl",
                "compromises.jsonl",
                "audit-state.json",
                "user-semantics.md",
                "alignment-report.md",
            ):
                atomic_write_text(target_dir / name, (staged / name).read_text(encoding="utf-8"))
        shutil.rmtree(source_dir)

    return destination_archive, imported, len(duplicates), compromise_count


def main():
    parser = argparse.ArgumentParser(description="Migrate semantic-alignment v1 Markdown records to v2.")
    parser.add_argument("record_dir")
    parser.add_argument("--apply", action="store_true", help="Apply the migration; default is a dry run")
    parser.add_argument("--into", help="Merge the legacy record into an existing v2 record directory")
    parser.add_argument("--source-label", help="Stable label used in provenance and archive naming")
    parser.add_argument(
        "--archive-only",
        action="store_true",
        help="With --into, archive a superseded legacy mirror without importing its current rows",
    )
    args = parser.parse_args()
    record_dir = Path(args.record_dir)
    try:
        if args.archive_only and not args.into:
            raise ValueError("--archive-only requires --into")
        if args.into:
            target_dir = Path(args.into)
            source_label = args.source_label or record_dir.name
            first, second = sorted((record_dir.resolve(), target_dir.resolve()), key=str)
            with record_lock(first):
                with record_lock(second):
                    legacy, current, triggers, duplicates = merge_plan(record_dir, target_dir)
                    if not args.apply:
                        print("dry run")
                        print("legacy entries to archive: " + (", ".join(legacy) or "none"))
                        print(f"current user semantics found: {len(current)}")
                        print(f"exact current semantics already present: {len(duplicates)}")
                        print(
                            "legacy recheck conditions to preserve as unverified compromises: "
                            + str(len(triggers))
                        )
                        print(f"archive only: {'yes' if args.archive_only else 'no'}")
                        return 0
                    archive, imported, duplicate_count, compromise_count = merge_migration(
                        record_dir,
                        target_dir,
                        source_label,
                        archive_only=args.archive_only,
                    )
            print(f"archived legacy source: {archive}")
            print(f"imported current user semantics: {imported}")
            print(f"skipped exact duplicate semantics: {duplicate_count}")
            print(f"migrated active compromise candidates: {compromise_count}")
            if not args.archive_only:
                print("legacy audit conclusions were not trusted as v2 cache entries; run a baseline full audit")
        else:
            with record_lock(record_dir):
                legacy, current, triggers = migration_plan(record_dir)
                if not args.apply:
                    print("dry run")
                    print("legacy entries to archive: " + (", ".join(legacy) or "none"))
                    print(f"current user semantics to migrate: {len(current)}")
                    print(f"legacy recheck conditions to preserve as unverified compromises: {len(triggers)}")
                    return 0
                archive, semantic_count, compromise_count = apply_migration(record_dir)
            print(f"archived v1 records: {archive}")
            print(f"migrated current user semantics: {semantic_count}")
            print(f"migrated active compromise candidates: {compromise_count}")
            print("legacy audit conclusions were not trusted as v2 cache entries; run a baseline full audit")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
