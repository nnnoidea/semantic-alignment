#!/usr/bin/env python3
import argparse
import json
import re
import sys
import uuid
from pathlib import Path

from recordlib import (
    COVERAGE_STATUSES,
    ASSERTION_TYPES,
    DIFFERENCE_IMPACTS,
    DIFFERENCE_STATUSES,
    DIFFERENCE_TYPES,
    IMPLEMENTATION_SOURCES,
    RELATIONS,
    atomic_write_text,
    build_snapshot,
    current_compromises,
    current_semantics,
    version_evidence,
    id_sort_key,
    load_audit_state,
    next_prefixed_id,
    record_lock,
    related_semantic_revisions,
    render_alignment_report,
    save_audit_state,
    semantic_neighbors,
    semantic_revision,
    snapshot_changes,
    stale_evidence,
    utc_now,
)


def require_records(record_dir):
    required = ["semantic-ledger.jsonl", "compromises.jsonl", "audit-state.json"]
    missing = [name for name in required if not (record_dir / name).exists()]
    if missing:
        raise ValueError("missing v2 record files: " + ", ".join(missing))


def split_ids(value):
    if not value or value.lower() == "none":
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def mark_audit_stale(state, reason):
    if not state.get("last_audit"):
        return
    state["last_audit"]["current"] = False
    invalidated = set(state["last_audit"].get("invalidated_by", []))
    invalidated.add(reason)
    state["last_audit"]["invalidated_by"] = sorted(invalidated)


def save_working_state(record_dir, state, reason):
    mark_audit_stale(state, reason)
    save_audit_state(record_dir, state)
    atomic_write_text(record_dir / "alignment-report.md", render_alignment_report(record_dir))


def artifact_root_identity(artifact_root):
    return str(Path(artifact_root).resolve())


def active_audit_for_write(state, artifact_root):
    active = state.get("active_audit")
    if active is None:
        return None
    if not isinstance(active, dict):
        raise ValueError("audit-state.json: active_audit must be an object")
    if active.get("mode") != "full":
        raise ValueError(f"unsupported active audit mode: {active.get('mode')!r}")
    if active.get("artifact_root") != artifact_root_identity(artifact_root):
        raise ValueError("active audit artifact root does not match --artifact-root")
    return active


def begin_full(args, record_dir, artifact_root):
    if not args.confirm_user_authorized:
        raise ValueError("begin-full requires --confirm-user-authorized")
    state = load_audit_state(record_dir)
    if state.get("active_audit") is not None:
        active = state["active_audit"]
        run_id = active.get("run_id", "?") if isinstance(active, dict) else "?"
        raise ValueError(f"active audit already exists: {run_id}")
    snapshot = build_snapshot(artifact_root, args.scope)
    started_at = utc_now()
    run_id = "full-" + uuid.uuid4().hex
    state["active_audit"] = {
        "run_id": run_id,
        "mode": "full",
        "artifact_root": artifact_root_identity(artifact_root),
        "scopes": snapshot["scopes"],
        "started_at": started_at,
        "user_authorized": True,
    }
    save_audit_state(record_dir, state)
    print(f"began full audit {run_id}")


def make_plan(record_dir, artifact_root, scopes):
    state = load_audit_state(record_dir)
    semantics = current_semantics(record_dir)
    snapshot = build_snapshot(artifact_root, scopes)
    neighbors = semantic_neighbors(record_dir)
    related_revisions = {
        semantic_id: {
            related_id: semantic_revision(semantics[related_id])
            for related_id in neighbors.get(semantic_id, [])
        }
        for semantic_id in semantics
    }
    previous = state.get("artifact_snapshot")
    changes = snapshot_changes(previous, snapshot)

    missing = []
    stale = {}
    valid = []
    for semantic_id, event in sorted(semantics.items(), key=lambda item: id_sort_key(item[0])):
        coverage = state.get("coverage", {}).get(semantic_id)
        if coverage is None:
            missing.append(semantic_id)
            continue
        reasons = []
        if coverage.get("semantic_revision") != semantic_revision(event):
            reasons.append("user-semantic-changed")
        if coverage.get("related_semantics", {}) != related_revisions[semantic_id]:
            reasons.append("related-semantics-changed")
        assertion_type = coverage.get("assertion_type")
        if (
            coverage.get("status") == "satisfied"
            and assertion_type in ASSERTION_TYPES
            and not str(coverage.get("counterexample_review", "")).strip()
        ):
            reasons.append("missing-counterexample-review")
        changed_evidence = stale_evidence(artifact_root, coverage.get("evidence", []))
        if changed_evidence:
            reasons.append("evidence-changed:" + ",".join(changed_evidence))
        if reasons:
            stale[semantic_id] = reasons
        else:
            valid.append(semantic_id)

    stale_differences = {}
    for item in state.get("differences", []):
        if item.get("status") == "resolved":
            continue
        difference_reasons = []
        changed_evidence = stale_evidence(artifact_root, item.get("evidence", []))
        if changed_evidence:
            difference_reasons.append("evidence-changed:" + ",".join(changed_evidence))
        expected_revisions = item.get("semantic_revisions", {})
        for semantic_id, expected_revision in expected_revisions.items():
            event = semantics.get(semantic_id)
            if event is None:
                difference_reasons.append(f"semantic-retired:{semantic_id}")
            elif expected_revision != semantic_revision(event):
                difference_reasons.append(f"semantic-changed:{semantic_id}")
        if difference_reasons:
            stale_differences[item.get("id", "?")] = difference_reasons

    current_ids = set(semantics)
    retired = sorted(set(state.get("coverage", {})) - current_ids)
    reasons = []
    full_required = False
    if previous is None:
        recommended_mode = "full"
        full_required = True
        reasons.append("no trusted artifact baseline exists")
    else:
        recommended_mode = "incremental"
        if previous.get("scopes") != snapshot.get("scopes"):
            recommended_mode = "full"
            full_required = True
            reasons.append("artifact scope changed")
    target_ids = missing + list(stale)
    semantic_targets = [
        {
            "semantic_id": semantic_id,
            "status": "missing" if semantic_id in missing else "stale",
            "related": neighbors.get(semantic_id, []),
            "reasons": stale.get(semantic_id, ["missing-coverage"]),
        }
        for semantic_id in sorted(target_ids, key=id_sort_key)
    ]

    return {
        "recommended_mode": recommended_mode,
        "full_required": full_required,
        "reasons": reasons,
        "changed_paths": changes,
        "coverage": {"valid": valid, "missing": missing, "stale": stale, "retired": retired},
        "semantic_targets": semantic_targets,
        "stale_differences": stale_differences,
        "snapshot": snapshot,
    }


def print_plan(plan, as_json):
    if as_json:
        print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
        return
    print(f"recommended audit mode: {plan['recommended_mode']}")
    print(f"full audit required: {'yes' if plan['full_required'] else 'no'}")
    for reason in plan["reasons"]:
        print(f"reason: {reason}")
    changes = plan["changed_paths"]
    print(
        "artifact changes: "
        f"added={len(changes['added'])}, modified={len(changes['modified'])}, deleted={len(changes['deleted'])}"
    )
    for kind in ("added", "modified", "deleted"):
        for path in changes[kind]:
            print(f"  {kind}: {path}")
    coverage = plan["coverage"]
    print(
        "semantic coverage: "
        f"valid={len(coverage['valid'])}, missing={len(coverage['missing'])}, "
        f"stale={len(coverage['stale'])}, retired={len(coverage['retired'])}"
    )
    for semantic_id in coverage["missing"]:
        print(f"  missing: {semantic_id}")
    for semantic_id, reasons in coverage["stale"].items():
        print(f"  stale: {semantic_id}: {'; '.join(reasons)}")
    for target in plan["semantic_targets"]:
        related = ", ".join(target["related"]) or "none"
        print(f"  audit target: {target['semantic_id']} (directly related: {related})")
    for difference_id, paths in plan["stale_differences"].items():
        print(f"  stale difference: {difference_id}: {'; '.join(paths)}")


def record_coverage(args, record_dir, artifact_root):
    semantics = current_semantics(record_dir)
    if args.semantic_id not in semantics:
        raise ValueError(f"unknown current user semantic: {args.semantic_id}")
    state = load_audit_state(record_dir)
    active = active_audit_for_write(state, artifact_root)
    evidence = version_evidence(artifact_root, args.evidence)
    if any(item["kind"] == "missing" for item in evidence):
        missing = [item["path"] for item in evidence if item["kind"] == "missing"]
        raise ValueError("evidence path does not exist: " + ", ".join(missing))
    event = semantics[args.semantic_id]
    if args.status == "satisfied" and not args.counterexample_review.strip():
        raise ValueError("satisfied coverage requires --counterexample-review")
    coverage = {
        "semantic_revision": semantic_revision(event),
        "related_semantics": related_semantic_revisions(record_dir, args.semantic_id),
        "status": args.status,
        "relation": args.relation,
        "source": args.source,
        "implementation": args.implementation,
        "assertion_type": args.assertion_type,
        "counterexample_review": args.counterexample_review,
        "evidence": evidence,
        "notes": args.notes,
        "audited_at": utc_now(),
    }
    if active:
        coverage["audit_run_id"] = active["run_id"]
    state.setdefault("coverage", {})[args.semantic_id] = coverage
    save_working_state(record_dir, state, f"coverage:{args.semantic_id}")
    print(f"recorded coverage for {args.semantic_id}")


def record_difference(args, record_dir, artifact_root):
    semantics = current_semantics(record_dir)
    user_ids = split_ids(args.user_semantics)
    unknown = [semantic_id for semantic_id in user_ids if semantic_id not in semantics]
    if unknown:
        raise ValueError("unknown current user semantics: " + ", ".join(unknown))
    evidence = version_evidence(artifact_root, args.evidence)
    if any(item["kind"] == "missing" for item in evidence):
        missing = [item["path"] for item in evidence if item["kind"] == "missing"]
        raise ValueError("evidence path does not exist: " + ", ".join(missing))

    state = load_audit_state(record_dir)
    active = active_audit_for_write(state, artifact_root)
    differences = state.setdefault("differences", [])
    difference_id = args.id or next_prefixed_id((item.get("id") for item in differences), "D")
    if not re.fullmatch(r"D\d+", difference_id):
        raise ValueError(f"invalid difference ID: {difference_id!r}")
    neighbors = semantic_neighbors(record_dir)
    context_ids = set(user_ids)
    for semantic_id in user_ids:
        context_ids.update(neighbors.get(semantic_id, []))
    replacement = {
        "id": difference_id,
        "type": args.type,
        "source": args.source,
        "relation": args.relation,
        "implementation": args.implementation,
        "user_semantics": user_ids,
        "semantic_revisions": {
            semantic_id: semantic_revision(semantics[semantic_id])
            for semantic_id in sorted(context_ids, key=id_sort_key)
        },
        "evidence": evidence,
        "impact": args.impact,
        "status": args.status,
        "notes": args.notes,
        "audited_at": utc_now(),
    }
    if active:
        replacement["audit_run_id"] = active["run_id"]
    for index, item in enumerate(differences):
        if item.get("id") == difference_id:
            differences[index] = replacement
            break
    else:
        differences.append(replacement)
    save_working_state(record_dir, state, f"difference:{difference_id}")
    print(f"recorded difference {difference_id}")


def resolve_difference(args, record_dir):
    state = load_audit_state(record_dir)
    for item in state.get("differences", []):
        if item.get("id") == args.id:
            if item.get("status") == "resolved":
                raise ValueError(f"difference is already resolved: {args.id}")
            item["status"] = args.status
            item["notes"] = args.notes or item.get("notes", "")
            item["audited_at"] = utc_now()
            save_working_state(record_dir, state, f"difference:{args.id}")
            print(f"updated difference {args.id} to {args.status}")
            return
    raise ValueError(f"unknown difference: {args.id}")


def finalize(args, record_dir, artifact_root):
    plan = make_plan(record_dir, artifact_root, args.scope)
    problems = []
    state = load_audit_state(record_dir)
    semantics = current_semantics(record_dir)
    current_coverage = {
        semantic_id: item
        for semantic_id, item in state.get("coverage", {}).items()
        if semantic_id in semantics
    }
    open_differences = [item for item in state.get("differences", []) if item.get("status") != "resolved"]
    if plan["coverage"]["missing"]:
        problems.append("missing coverage: " + ", ".join(plan["coverage"]["missing"]))
    if plan["coverage"]["stale"]:
        problems.append("stale coverage: " + ", ".join(plan["coverage"]["stale"]))
    if plan["stale_differences"]:
        problems.append("stale differences: " + ", ".join(plan["stale_differences"]))
    for semantic_id, coverage in current_coverage.items():
        if coverage.get("status") == "satisfied":
            continue
        if not any(semantic_id in item.get("user_semantics", []) for item in open_differences):
            problems.append(f"non-satisfied coverage for {semantic_id} has no reported difference")
    changed = sum(plan["changed_paths"].values(), [])
    if args.mode == "incremental" and changed and not args.confirm_all_changes_reviewed:
        problems.append("artifact changes exist; pass --confirm-all-changes-reviewed only after reviewing every listed path")
    if args.mode == "incremental" and plan["full_required"]:
        problems.append("the current audit plan requires --mode full")
    completed_run_id = None
    if args.mode == "full":
        active = state.get("active_audit")
        if not isinstance(active, dict) or active.get("mode") != "full":
            problems.append("full audit requires an active full audit session; run begin-full first")
        else:
            completed_run_id = active.get("run_id")
            if active.get("artifact_root") != artifact_root_identity(artifact_root):
                problems.append("active full audit artifact root does not match --artifact-root")
            if active.get("scopes") != plan["snapshot"].get("scopes"):
                problems.append("active full audit scope does not match finalize scope")
            if not isinstance(completed_run_id, str) or not completed_run_id.strip():
                problems.append("active full audit is missing run_id")
            else:
                not_refreshed = [
                    semantic_id
                    for semantic_id in sorted(semantics, key=id_sort_key)
                    if current_coverage.get(semantic_id, {}).get("audit_run_id") != completed_run_id
                ]
                if not_refreshed:
                    problems.append(
                        "full audit coverage not refreshed in active run: " + ", ".join(not_refreshed)
                    )
                unreviewed_differences = [
                    item.get("id", "?")
                    for item in open_differences
                    if item.get("audit_run_id") != completed_run_id
                ]
                if unreviewed_differences:
                    problems.append(
                        "open differences not reviewed in active full audit: "
                        + ", ".join(sorted(unreviewed_differences, key=id_sort_key))
                    )
        if not args.confirm_full_scope_reviewed:
            problems.append(
                "full artifact scope was not confirmed; pass --confirm-full-scope-reviewed only after reviewing every scoped artifact path"
            )
    active_compromises = current_compromises(record_dir)
    unknown_compromises = [item for item in args.relevant_compromise if item not in active_compromises]
    if unknown_compromises:
        problems.append("unknown or inactive relevant compromises: " + ", ".join(unknown_compromises))
    if problems:
        raise ValueError("cannot finalize audit:\n- " + "\n- ".join(problems))

    state["coverage"] = current_coverage
    completed_at = utc_now()
    state["artifact_snapshot"] = {**plan["snapshot"], "completed_at": completed_at}
    state["last_audit"] = {
        "mode": args.mode,
        "completed_at": completed_at,
        "current": True,
        "relevant_compromises": sorted(set(args.relevant_compromise)),
        "reviewed_changes": plan["changed_paths"],
        "semantic_count": len(semantics),
        "file_count": len(plan["snapshot"].get("files", {})),
    }
    if completed_run_id:
        state["last_audit"]["audit_run_id"] = completed_run_id
        state.pop("active_audit", None)
    save_audit_state(record_dir, state)
    atomic_write_text(record_dir / "alignment-report.md", render_alignment_report(record_dir))
    print(f"finalized {args.mode} audit at {completed_at}")


def render_report(record_dir):
    atomic_write_text(record_dir / "alignment-report.md", render_alignment_report(record_dir))
    print(f"rendered: {record_dir / 'alignment-report.md'}")


def add_common_root(parser):
    parser.add_argument("--artifact-root", required=True)


def main():
    parser = argparse.ArgumentParser(description="Plan and persist incremental semantic audits.")
    parser.add_argument("record_dir", help="Path to <project-root>/.semantic-alignment/")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Show changed artifacts and invalidated audit entries")
    add_common_root(plan_parser)
    plan_parser.add_argument("--scope", action="append", default=[])
    plan_parser.add_argument("--json", action="store_true")

    begin_full_parser = subparsers.add_parser("begin-full", help="Start a user-authorized full audit run")
    add_common_root(begin_full_parser)
    begin_full_parser.add_argument("--scope", action="append", default=[])
    begin_full_parser.add_argument("--confirm-user-authorized", action="store_true")

    coverage_parser = subparsers.add_parser("record-coverage", help="Record code-derived implementation evidence for one user semantic")
    add_common_root(coverage_parser)
    coverage_parser.add_argument("--semantic-id", required=True)
    coverage_parser.add_argument("--status", choices=sorted(COVERAGE_STATUSES), required=True)
    coverage_parser.add_argument("--relation", choices=sorted(RELATIONS), required=True)
    coverage_parser.add_argument("--source", choices=sorted(IMPLEMENTATION_SOURCES), required=True)
    coverage_parser.add_argument("--implementation", required=True)
    coverage_parser.add_argument(
        "--assertion-type", choices=sorted(ASSERTION_TYPES), required=True
    )
    coverage_parser.add_argument("--counterexample-review", default="")
    coverage_parser.add_argument("--evidence", action="append", required=True)
    coverage_parser.add_argument("--notes", default="")

    difference_parser = subparsers.add_parser("record-difference", help="Record an implementation difference found by artifact audit")
    add_common_root(difference_parser)
    difference_parser.add_argument("--id")
    difference_parser.add_argument("--type", choices=sorted(DIFFERENCE_TYPES), required=True)
    difference_parser.add_argument("--source", choices=sorted(IMPLEMENTATION_SOURCES), required=True)
    difference_parser.add_argument("--relation", choices=sorted(RELATIONS), required=True)
    difference_parser.add_argument("--implementation", required=True)
    difference_parser.add_argument("--user-semantics", default="none")
    difference_parser.add_argument("--evidence", action="append", required=True)
    difference_parser.add_argument("--impact", choices=sorted(DIFFERENCE_IMPACTS), required=True)
    difference_parser.add_argument("--status", choices=sorted(DIFFERENCE_STATUSES), default="open")
    difference_parser.add_argument("--notes", default="")

    resolve_parser = subparsers.add_parser("resolve-difference", help="Accept or resolve a previously recorded difference")
    resolve_parser.add_argument("--id", required=True)
    resolve_parser.add_argument("--status", choices=("accepted", "resolved"), required=True)
    resolve_parser.add_argument("--notes")

    finalize_parser = subparsers.add_parser("finalize", help="Commit a trusted artifact snapshot after audit")
    add_common_root(finalize_parser)
    finalize_parser.add_argument("--scope", action="append", default=[])
    finalize_parser.add_argument("--mode", choices=("full", "incremental"), required=True)
    finalize_parser.add_argument("--confirm-all-changes-reviewed", action="store_true")
    finalize_parser.add_argument("--confirm-full-scope-reviewed", action="store_true")
    finalize_parser.add_argument("--relevant-compromise", action="append", default=[])

    subparsers.add_parser("render", help="Regenerate alignment-report.md from current records")

    args = parser.parse_args()
    record_dir = Path(args.record_dir)
    try:
        require_records(record_dir)
        with record_lock(record_dir):
            if args.command == "plan":
                print_plan(make_plan(record_dir, args.artifact_root, args.scope), args.json)
            elif args.command == "begin-full":
                begin_full(args, record_dir, args.artifact_root)
            elif args.command == "record-coverage":
                record_coverage(args, record_dir, args.artifact_root)
            elif args.command == "record-difference":
                record_difference(args, record_dir, args.artifact_root)
            elif args.command == "resolve-difference":
                resolve_difference(args, record_dir)
            elif args.command == "finalize":
                finalize(args, record_dir, args.artifact_root)
            else:
                render_report(record_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
