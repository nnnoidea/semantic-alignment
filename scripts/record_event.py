#!/usr/bin/env python3
import argparse
import re
import sys
from datetime import date
from pathlib import Path

from recordlib import (
    COMPROMISE_STATUSES,
    SEMANTIC_CATEGORIES,
    SEMANTIC_OPERATIONS,
    SEMANTIC_REASONS,
    append_jsonl,
    atomic_write_text,
    current_compromises,
    current_semantics,
    id_sort_key,
    latest_by_id,
    load_audit_state,
    next_prefixed_id,
    read_jsonl,
    record_lock,
    render_alignment_report,
    render_user_semantics,
    save_audit_state,
    utc_now,
)


def require_v2(record_dir):
    required = ["semantic-ledger.jsonl", "compromises.jsonl", "audit-state.json"]
    missing = [name for name in required if not (record_dir / name).exists()]
    if missing:
        raise ValueError("missing v2 record files: " + ", ".join(missing))


def record_semantic(args, record_dir):
    events = read_jsonl(record_dir / "semantic-ledger.jsonl")
    latest = latest_by_id(events, "semantic_id")
    current = {
        semantic_id: event
        for semantic_id, event in latest.items()
        if event.get("operation") != "delete"
    }

    semantic_id = args.id
    previous_related = set()
    if args.operation == "add":
        semantic_id = semantic_id or next_prefixed_id(latest, "U")
        if not re.fullmatch(r"U\d+", semantic_id):
            raise ValueError(f"invalid semantic ID: {semantic_id!r}")
        if semantic_id in latest:
            raise ValueError(f"semantic already exists: {semantic_id}")
        if not args.text:
            raise ValueError("--text is required for add")
        if not args.category:
            raise ValueError("--category is required for add")
        revision = 1
        before = None
        text = args.text
        related = split_ids(args.related)
    else:
        if not semantic_id or semantic_id not in latest:
            raise ValueError("update/delete requires an existing --id")
        previous = latest[semantic_id]
        previous_related = {
            item for item in previous.get("related", []) if item in current and item != semantic_id
        }
        if previous.get("operation") == "delete":
            raise ValueError(f"semantic is already deleted: {semantic_id}")
        revision = previous["revision"] + 1
        before = previous.get("text")
        if args.category is None:
            args.category = previous.get("category")
        if args.operation == "update":
            text = previous.get("text") if args.text is None else args.text
            if not text:
                raise ValueError("updated semantic text must be non-empty")
            related = (
                [item for item in previous.get("related", []) if item in current]
                if args.related is None
                else split_ids(args.related)
            )
            if (
                text == previous.get("text")
                and args.category == previous.get("category")
                and related == previous.get("related", [])
            ):
                raise ValueError("update does not change text, category, or related semantics")
        else:
            text = None
            related = [item for item in previous.get("related", []) if item in current]

    unknown_related = [item for item in related if item not in current]
    if semantic_id in related:
        raise ValueError("a semantic cannot be related to itself")
    if unknown_related:
        raise ValueError("unknown current related semantics: " + ", ".join(unknown_related))
    related = sorted(set(related), key=id_sort_key)

    event = {
        "semantic_id": semantic_id,
        "revision": revision,
        "date": args.date,
        "operation": args.operation,
        "category": args.category,
        "before": before,
        "text": text,
        "related": related,
        "reason": args.reason,
        "source": args.source,
        "recorded_at": utc_now(),
    }
    append_jsonl(record_dir / "semantic-ledger.jsonl", event)
    effective_related = set() if args.operation == "delete" else set(related)
    synchronized_ids = []
    for related_id in sorted(previous_related ^ effective_related, key=id_sort_key):
        previous = latest[related_id]
        original_values = set(previous.get("related", []))
        related_values = set(original_values)
        if related_id in effective_related:
            related_values.add(semantic_id)
        else:
            related_values.discard(semantic_id)
        if related_values == original_values:
            continue
        synchronized = {
            "semantic_id": related_id,
            "revision": previous["revision"] + 1,
            "date": args.date,
            "operation": "update",
            "category": previous.get("category"),
            "before": previous.get("text"),
            "text": previous.get("text"),
            "related": sorted(related_values, key=id_sort_key),
            "reason": args.reason,
            "source": f"{args.source} [related sync from {semantic_id}]",
            "recorded_at": utc_now(),
        }
        append_jsonl(record_dir / "semantic-ledger.jsonl", synchronized)
        synchronized_ids.append(related_id)
    atomic_write_text(record_dir / "user-semantics.md", render_user_semantics(record_dir))

    state = load_audit_state(record_dir)
    if state.get("last_audit"):
        state["last_audit"]["current"] = False
        invalidated = set(state["last_audit"].get("invalidated_by", []))
        invalidated.add(f"semantic:{semantic_id}")
        invalidated.update(f"semantic:{item}" for item in synchronized_ids)
        state["last_audit"]["invalidated_by"] = sorted(invalidated)
        save_audit_state(record_dir, state)
    atomic_write_text(record_dir / "alignment-report.md", render_alignment_report(record_dir))
    print(f"recorded {semantic_id} revision {revision}")
    if synchronized_ids:
        print("synchronized related semantics: " + ", ".join(synchronized_ids))


def split_ids(value):
    if not value or value.strip().lower() == "none":
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def validate_compromise_value(value):
    required = (
        "original_target",
        "actual_choice",
        "gap",
        "reason",
        "evidence",
        "scope",
        "recheck_condition",
        "recheck_method",
    )
    missing = [
        name.replace("_", "-")
        for name in required
        if not isinstance(value.get(name), str) or not value.get(name, "").strip()
    ]
    if missing:
        raise ValueError("missing required compromise fields: " + ", ".join(missing))


def record_compromise(args, record_dir):
    events = read_jsonl(record_dir / "compromises.jsonl")
    latest = latest_by_id(events, "compromise_id")
    current = current_compromises(record_dir)

    compromise_id = args.id
    if args.operation == "add":
        compromise_id = compromise_id or next_prefixed_id(latest, "C")
        if not re.fullmatch(r"C\d+", compromise_id):
            raise ValueError(f"invalid compromise ID: {compromise_id!r}")
        if compromise_id in latest:
            raise ValueError(f"compromise already exists: {compromise_id}")
        value = {
            "original_target": args.original_target,
            "actual_choice": args.actual_choice,
            "gap": args.gap,
            "reason": args.reason,
            "evidence": args.evidence,
            "scope": args.scope,
            "recheck_condition": args.recheck_condition,
            "recheck_method": args.recheck_method,
        }
        value["affected_user_semantics"] = split_ids(args.affected_user_semantics)
        value["status"] = "active"
        value["last_checked"] = args.last_checked or "never"
        revision = 1
    else:
        if not compromise_id or compromise_id not in latest:
            raise ValueError("update/resolve/supersede requires an existing --id")
        previous = latest[compromise_id]
        if compromise_id not in current:
            raise ValueError(f"compromise is not active: {compromise_id}")
        value = {
            key: previous.get(key)
            for key in (
                "original_target",
                "actual_choice",
                "gap",
                "reason",
                "evidence",
                "scope",
                "affected_user_semantics",
                "recheck_condition",
                "recheck_method",
                "status",
                "last_checked",
            )
        }
        for key in (
            "original_target",
            "actual_choice",
            "gap",
            "reason",
            "evidence",
            "scope",
            "recheck_condition",
            "recheck_method",
            "last_checked",
        ):
            incoming = getattr(args, key)
            if incoming is not None:
                value[key] = incoming
        if args.affected_user_semantics is not None:
            value["affected_user_semantics"] = split_ids(args.affected_user_semantics)
        if args.operation == "resolve":
            value["status"] = "resolved"
        elif args.operation == "supersede":
            value["status"] = "superseded"
        elif args.status and args.status != "active":
            raise ValueError("use --operation resolve or supersede for terminal compromise states")
        else:
            value["status"] = "active"
        revision = previous["revision"] + 1

    if value.get("status") not in COMPROMISE_STATUSES:
        raise ValueError(f"invalid compromise status: {value.get('status')}")
    validate_compromise_value(value)
    active_semantics = current_semantics(record_dir)
    unknown_semantics = [item for item in value.get("affected_user_semantics", []) if item not in active_semantics]
    if unknown_semantics:
        raise ValueError("unknown current affected user semantics: " + ", ".join(unknown_semantics))
    event = {
        "compromise_id": compromise_id,
        "revision": revision,
        "date": args.date,
        "operation": args.operation,
        **value,
        "recorded_at": utc_now(),
    }
    append_jsonl(record_dir / "compromises.jsonl", event)
    state = load_audit_state(record_dir)
    if state.get("last_audit"):
        state["last_audit"]["current"] = False
        invalidated = set(state["last_audit"].get("invalidated_by", []))
        invalidated.add(f"compromise:{compromise_id}")
        state["last_audit"]["invalidated_by"] = sorted(invalidated)
        save_audit_state(record_dir, state)
    atomic_write_text(record_dir / "alignment-report.md", render_alignment_report(record_dir))
    print(f"recorded {compromise_id} revision {revision}")


def add_semantic_parser(subparsers):
    parser = subparsers.add_parser("semantic", help="Add, update, or delete a stable user semantic")
    parser.add_argument("--id")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--operation", choices=sorted(SEMANTIC_OPERATIONS), required=True)
    parser.add_argument("--category", choices=SEMANTIC_CATEGORIES)
    parser.add_argument("--text")
    parser.add_argument("--related", help="Comma-separated current semantic IDs; use 'none' to clear")
    parser.add_argument("--reason", choices=sorted(SEMANTIC_REASONS), required=True)
    parser.add_argument("--source", required=True)


def add_compromise_parser(subparsers):
    parser = subparsers.add_parser("compromise", help="Add or revise a constraint-driven compromise")
    parser.add_argument("--id")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--operation", choices=("add", "update", "resolve", "supersede"), required=True)
    parser.add_argument("--original-target")
    parser.add_argument("--actual-choice")
    parser.add_argument("--gap")
    parser.add_argument("--reason")
    parser.add_argument("--evidence")
    parser.add_argument("--scope")
    parser.add_argument("--affected-user-semantics")
    parser.add_argument("--recheck-condition")
    parser.add_argument("--recheck-method")
    parser.add_argument("--status", choices=sorted(COMPROMISE_STATUSES))
    parser.add_argument("--last-checked")


def main():
    parser = argparse.ArgumentParser(description="Record semantic changes and compromises with stable IDs.")
    parser.add_argument("record_dir", help="Path to <project-root>/.semantic-alignment/")
    subparsers = parser.add_subparsers(dest="kind", required=True)
    add_semantic_parser(subparsers)
    add_compromise_parser(subparsers)
    args = parser.parse_args()

    record_dir = Path(args.record_dir)
    try:
        require_v2(record_dir)
        with record_lock(record_dir):
            if args.kind == "semantic":
                record_semantic(args, record_dir)
            else:
                record_compromise(args, record_dir)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
