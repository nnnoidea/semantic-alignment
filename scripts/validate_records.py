#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

from recordlib import (
    COMPROMISE_STATUSES,
    COVERAGE_STATUSES,
    ASSERTION_TYPES,
    DIFFERENCE_IMPACTS,
    DIFFERENCE_STATUSES,
    DIFFERENCE_TYPES,
    IMPLEMENTATION_SOURCES,
    RELATIONS,
    SCHEMA_VERSION,
    SEMANTIC_CATEGORIES,
    SEMANTIC_OPERATIONS,
    SEMANTIC_REASONS,
    read_jsonl,
    record_lock,
    render_alignment_report,
    render_user_semantics,
)


REQUIRED_FILES = [
    "user-semantics.md",
    "semantic-ledger.jsonl",
    "compromises.jsonl",
    "audit-state.json",
    "alignment-report.md",
]


def require_fields(row, fields, label, errors):
    for field in fields:
        if field not in row:
            errors.append(f"{label}: missing field {field!r}")


def validate_revision_events(rows, id_field, prefix, operations, label, terminal_operations=()):
    errors = []
    grouped = {}
    for line_no, row in enumerate(rows, start=1):
        row_label = f"{label}:{line_no}"
        require_fields(row, [id_field, "revision", "operation"], row_label, errors)
        event_id = row.get(id_field)
        if not isinstance(event_id, str) or not re.fullmatch(rf"{prefix}\d+", event_id):
            errors.append(f"{row_label}: invalid {id_field}: {event_id!r}")
            continue
        if row.get("operation") not in operations:
            errors.append(f"{row_label}: invalid operation: {row.get('operation')!r}")
        if not isinstance(row.get("revision"), int) or row["revision"] < 1:
            errors.append(f"{row_label}: revision must be a positive integer")
            continue
        grouped.setdefault(event_id, []).append((line_no, row))

    for event_id, events in grouped.items():
        revisions = [event["revision"] for _line, event in events]
        if revisions != list(range(1, len(revisions) + 1)):
            errors.append(f"{label}: {event_id} revisions must be contiguous and ordered from 1")
        if events[0][1].get("operation") != "add":
            errors.append(f"{label}: {event_id} must start with an add event")
        terminal_seen = False
        for index, (line_no, event) in enumerate(events):
            operation = event.get("operation")
            if index > 0 and operation == "add":
                errors.append(f"{label}:{line_no}: {event_id} cannot contain a second add event")
            if terminal_seen:
                errors.append(f"{label}:{line_no}: {event_id} cannot continue after a terminal event")
            if operation in terminal_operations:
                terminal_seen = True
    return errors


def validate_semantics(record_dir):
    rows = read_jsonl(record_dir / "semantic-ledger.jsonl")
    known_ids = {row.get("semantic_id") for row in rows}
    errors = validate_revision_events(
        rows,
        "semantic_id",
        "U",
        SEMANTIC_OPERATIONS,
        "semantic-ledger.jsonl",
        terminal_operations={"delete"},
    )
    required = ["semantic_id", "revision", "date", "operation", "category", "before", "text", "reason", "source", "recorded_at"]
    for line_no, row in enumerate(rows, start=1):
        label = f"semantic-ledger.jsonl:{line_no}"
        require_fields(row, required, label, errors)
        if row.get("category") not in SEMANTIC_CATEGORIES:
            errors.append(f"{label}: invalid category: {row.get('category')!r}")
        if row.get("reason") not in SEMANTIC_REASONS:
            errors.append(f"{label}: invalid reason: {row.get('reason')!r}")
        if row.get("operation") == "delete":
            if row.get("text") is not None:
                errors.append(f"{label}: delete event text must be null")
        elif not isinstance(row.get("text"), str) or not row.get("text", "").strip():
            errors.append(f"{label}: add/update event text must be non-empty")
        related = row.get("related", [])
        if not isinstance(related, list) or any(not isinstance(item, str) for item in related):
            errors.append(f"{label}: related must be a list of semantic IDs")
        else:
            if len(related) != len(set(related)):
                errors.append(f"{label}: related must not contain duplicates")
            if row.get("semantic_id") in related:
                errors.append(f"{label}: a semantic cannot be related to itself")
            if any(not re.fullmatch(r"U\d+", item) for item in related):
                errors.append(f"{label}: related contains an invalid semantic ID")
            elif any(item not in known_ids for item in related):
                errors.append(f"{label}: related contains an unknown semantic ID")
    latest = {}
    for line_no, row in enumerate(rows, start=1):
        previous = latest.get(row.get("semantic_id"))
        if row.get("operation") == "add" and row.get("before") is not None:
            errors.append(f"semantic-ledger.jsonl:{line_no}: add event before must be null")
        if row.get("operation") in {"update", "delete"} and previous and row.get("before") != previous.get("text"):
            errors.append(f"semantic-ledger.jsonl:{line_no}: before does not match the previous revision")
        latest[row.get("semantic_id")] = row

    current = {
        semantic_id: row
        for semantic_id, row in latest.items()
        if row.get("operation") != "delete"
    }
    for semantic_id, row in current.items():
        for related_id in row.get("related", []):
            if related_id not in current:
                errors.append(
                    f"semantic-ledger.jsonl: current semantic {semantic_id} relates to retired semantic {related_id}"
                )
                continue
            if semantic_id not in current[related_id].get("related", []):
                errors.append(
                    f"semantic-ledger.jsonl: current relation {semantic_id}<->{related_id} is not symmetric"
                )
    return errors


def validate_compromises(record_dir):
    rows = read_jsonl(record_dir / "compromises.jsonl")
    known_semantic_ids = {row.get("semantic_id") for row in read_jsonl(record_dir / "semantic-ledger.jsonl")}
    errors = validate_revision_events(
        rows,
        "compromise_id",
        "C",
        {"add", "update", "resolve", "supersede"},
        "compromises.jsonl",
        terminal_operations={"resolve", "supersede"},
    )
    required = [
        "compromise_id",
        "revision",
        "date",
        "operation",
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
        "recorded_at",
    ]
    for line_no, row in enumerate(rows, start=1):
        label = f"compromises.jsonl:{line_no}"
        require_fields(row, required, label, errors)
        if row.get("status") not in COMPROMISE_STATUSES:
            errors.append(f"{label}: invalid status: {row.get('status')!r}")
        expected_status = {"add": "active", "resolve": "resolved", "supersede": "superseded"}.get(row.get("operation"))
        if expected_status and row.get("status") != expected_status:
            errors.append(f"{label}: {row.get('operation')} event must have status {expected_status!r}")
        if row.get("operation") == "update" and row.get("status") != "active":
            errors.append(f"{label}: update event must have status 'active'")
        if not isinstance(row.get("affected_user_semantics"), list):
            errors.append(f"{label}: affected_user_semantics must be a list")
        elif any(semantic_id not in known_semantic_ids for semantic_id in row["affected_user_semantics"]):
            errors.append(f"{label}: affected_user_semantics contains an unknown semantic ID")
        for field in ("original_target", "actual_choice", "gap", "reason", "evidence", "scope", "recheck_condition", "recheck_method"):
            if not isinstance(row.get(field), str) or not row.get(field, "").strip():
                errors.append(f"{label}: {field} must be non-empty")
    return errors


def validate_evidence(items, label, errors):
    if not isinstance(items, list) or not items:
        errors.append(f"{label}: evidence must be a non-empty list")
        return
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"{label}: evidence item {index} must be an object")
            continue
        require_fields(item, ["path", "kind"], f"{label}:evidence:{index}", errors)
        if "version" not in item and "fingerprint" not in item:
            errors.append(f"{label}:evidence:{index}: missing field 'version'")


def validate_audit_state(record_dir):
    path = record_dir / "audit-state.json"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"audit-state.json: invalid JSON: {exc.msg}"]
    errors = []
    if not isinstance(state, dict):
        return ["audit-state.json: root must be an object"]
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"audit-state.json: schema_version must be {SCHEMA_VERSION}")
    active_audit = state.get("active_audit")
    if active_audit is not None:
        label = "audit-state.json:active_audit"
        if not isinstance(active_audit, dict):
            errors.append(f"{label}: must be an object")
        else:
            require_fields(
                active_audit,
                ["run_id", "mode", "artifact_root", "scopes", "started_at", "user_authorized"],
                label,
                errors,
            )
            if active_audit.get("mode") != "full":
                errors.append(f"{label}: mode must be 'full'")
            if not isinstance(active_audit.get("run_id"), str) or not active_audit.get("run_id", "").strip():
                errors.append(f"{label}: run_id must be non-empty")
            artifact_root = active_audit.get("artifact_root")
            if not isinstance(artifact_root, str) or not Path(artifact_root).is_absolute():
                errors.append(f"{label}: artifact_root must be an absolute path")
            scopes = active_audit.get("scopes")
            if not isinstance(scopes, list) or not scopes or any(not isinstance(scope, str) or not scope for scope in scopes):
                errors.append(f"{label}: scopes must be a non-empty list of strings")
            if active_audit.get("user_authorized") is not True:
                errors.append(f"{label}: user_authorized must be true")
    if not isinstance(state.get("coverage"), dict):
        errors.append("audit-state.json: coverage must be an object")
        coverage = {}
    else:
        coverage = state["coverage"]
    known_ids = {row.get("semantic_id") for row in read_jsonl(record_dir / "semantic-ledger.jsonl")}
    for semantic_id, item in coverage.items():
        label = f"audit-state.json:coverage:{semantic_id}"
        if not re.fullmatch(r"U\d+", semantic_id):
            errors.append(f"{label}: invalid semantic ID")
        if not isinstance(item, dict):
            errors.append(f"{label}: entry must be an object")
            continue
        require_fields(item, ["semantic_revision", "status", "relation", "source", "implementation", "evidence", "notes", "audited_at"], label, errors)
        if item.get("status") not in COVERAGE_STATUSES:
            errors.append(f"{label}: invalid status: {item.get('status')!r}")
        if item.get("relation") not in RELATIONS:
            errors.append(f"{label}: invalid relation: {item.get('relation')!r}")
        assertion_type = item.get("assertion_type")
        if assertion_type is not None and assertion_type not in ASSERTION_TYPES:
            errors.append(f"{label}: invalid assertion_type: {assertion_type!r}")
        counterexample_review = item.get("counterexample_review")
        if counterexample_review is not None and not isinstance(counterexample_review, str):
            errors.append(f"{label}: counterexample_review must be a string")
        if item.get("audit_run_id") is not None and not isinstance(item.get("audit_run_id"), str):
            errors.append(f"{label}: audit_run_id must be a string")
        if assertion_type is not None and item.get("status") == "satisfied":
            if not isinstance(counterexample_review, str) or not counterexample_review.strip():
                errors.append(
                    f"{label}: satisfied coverage requires non-empty counterexample_review"
                )
        if item.get("source") not in IMPLEMENTATION_SOURCES:
            errors.append(f"{label}: invalid source: {item.get('source')!r}")
        related_semantics = item.get("related_semantics", {})
        if not isinstance(related_semantics, dict):
            errors.append(f"{label}: related_semantics must be an object")
        elif any(not re.fullmatch(r"U\d+", related_id) for related_id in related_semantics):
            errors.append(f"{label}: related_semantics contains an invalid semantic ID")
        elif any(related_id not in known_ids for related_id in related_semantics):
            errors.append(f"{label}: related_semantics contains an unknown semantic ID")
        validate_evidence(item.get("evidence"), label, errors)
        if semantic_id not in known_ids:
            errors.append(f"{label}: coverage refers to an unknown user semantic")

    differences = state.get("differences")
    if not isinstance(differences, list):
        errors.append("audit-state.json: differences must be a list")
        differences = []
    seen = set()
    for index, item in enumerate(differences, start=1):
        label = f"audit-state.json:difference:{index}"
        if not isinstance(item, dict):
            errors.append(f"{label}: entry must be an object")
            continue
        require_fields(item, ["id", "type", "source", "relation", "implementation", "user_semantics", "semantic_revisions", "evidence", "impact", "status", "notes", "audited_at"], label, errors)
        difference_id = item.get("id")
        if not isinstance(difference_id, str) or not re.fullmatch(r"D\d+", difference_id):
            errors.append(f"{label}: invalid difference ID: {difference_id!r}")
        elif difference_id in seen:
            errors.append(f"{label}: duplicate difference ID: {difference_id}")
        seen.add(difference_id)
        if item.get("type") not in DIFFERENCE_TYPES:
            errors.append(f"{label}: invalid type: {item.get('type')!r}")
        if item.get("source") not in IMPLEMENTATION_SOURCES:
            errors.append(f"{label}: invalid source: {item.get('source')!r}")
        if item.get("relation") not in RELATIONS:
            errors.append(f"{label}: invalid relation: {item.get('relation')!r}")
        if item.get("impact") not in DIFFERENCE_IMPACTS:
            errors.append(f"{label}: invalid impact: {item.get('impact')!r}")
        if item.get("status") not in DIFFERENCE_STATUSES:
            errors.append(f"{label}: invalid status: {item.get('status')!r}")
        if item.get("audit_run_id") is not None and not isinstance(item.get("audit_run_id"), str):
            errors.append(f"{label}: audit_run_id must be a string")
        if not isinstance(item.get("user_semantics"), list):
            errors.append(f"{label}: user_semantics must be a list")
        elif any(semantic_id not in known_ids for semantic_id in item["user_semantics"]):
            errors.append(f"{label}: user_semantics contains an unknown ID")
        if not isinstance(item.get("semantic_revisions"), dict):
            errors.append(f"{label}: semantic_revisions must be an object")
        else:
            if any(semantic_id not in known_ids for semantic_id in item["semantic_revisions"]):
                errors.append(f"{label}: semantic_revisions contains an unknown semantic ID")
            if any(not isinstance(revision, str) for revision in item["semantic_revisions"].values()):
                errors.append(f"{label}: semantic_revisions values must be strings")
        validate_evidence(item.get("evidence"), label, errors)
    return errors


def validate_generated_files(record_dir):
    errors = []
    expected_semantics = render_user_semantics(record_dir)
    actual_semantics = (record_dir / "user-semantics.md").read_text(encoding="utf-8")
    if actual_semantics != expected_semantics:
        errors.append("user-semantics.md is out of sync; record semantics through scripts/record_event.py")
    expected_report = render_alignment_report(record_dir)
    actual_report = (record_dir / "alignment-report.md").read_text(encoding="utf-8")
    if actual_report != expected_report:
        errors.append("alignment-report.md is out of sync; run scripts/audit.py <record-dir> render")
    return errors


def validate(record_dir):
    record_dir = Path(record_dir)
    if not record_dir.is_dir():
        return [f"record directory not found: {record_dir}"]
    errors = [f"missing required file: {name}" for name in REQUIRED_FILES if not (record_dir / name).exists()]
    if errors:
        if (record_dir / "user-semantic-ledger.md").exists():
            errors.append("legacy v1 records detected; run scripts/migrate_v1.py <record-dir> --apply")
        return errors
    try:
        errors += validate_semantics(record_dir)
        errors += validate_compromises(record_dir)
        errors += validate_audit_state(record_dir)
        errors += validate_generated_files(record_dir)
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate semantic-alignment v2 records and generated projections.")
    parser.add_argument("record_dir", help="Path to <project-root>/.semantic-alignment/")
    args = parser.parse_args()
    with record_lock(args.record_dir):
        errors = validate(args.record_dir)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Semantic alignment records are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
