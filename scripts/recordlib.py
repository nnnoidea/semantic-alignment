#!/usr/bin/env python3
"""Shared record and low-cost version helpers for semantic-alignment v2."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import threading
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_VERSION = 2

SEMANTIC_CATEGORIES = (
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
)

CATEGORY_HEADINGS = {
    "goal": "Goals",
    "principle": "Principles",
    "context": "Context",
    "global-design": "Global Design Semantics",
    "local-design": "Local Design Semantics",
    "system": "System Semantics",
    "content": "Content Semantics",
    "process": "Process Semantics",
    "constraint": "Constraints",
    "review": "Review Semantics",
}

SEMANTIC_OPERATIONS = {"add", "update", "delete"}
SEMANTIC_REASONS = {
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

COMPROMISE_STATUSES = {"active", "resolved", "superseded"}
COVERAGE_STATUSES = {"satisfied", "partial", "unmet", "conflict", "unknown"}
ASSERTION_TYPES = {"capability", "obligation", "prohibition"}
RELATIONS = {"implements", "extends", "narrows", "substitutes", "conflicts", "none", "unknown"}
IMPLEMENTATION_SOURCES = {"user-explicit", "user-inferred", "agent-added", "constraint-driven", "unknown"}
DIFFERENCE_TYPES = {"added", "enhanced", "omitted", "substituted", "narrowed", "conflict", "artifact-drift"}
DIFFERENCE_IMPACTS = {"low", "medium", "high"}
DIFFERENCE_STATUSES = {"open", "accepted", "resolved"}

DEFAULT_IGNORED_PARTS = {".git", ".semantic-alignment", "__pycache__", ".pytest_cache", ".mypy_cache"}

_RECORD_LOCK_STATE = threading.local()


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@contextmanager
def record_lock(record_dir):
    """Serialize transactions while allowing same-thread reentry for one record set."""
    lock_root = Path(tempfile.gettempdir()) / "semantic-alignment-locks"
    lock_root.mkdir(parents=True, exist_ok=True)
    key = digest_text(str(Path(record_dir).resolve()))
    held = getattr(_RECORD_LOCK_STATE, "held", None)
    if held is None:
        held = {}
        _RECORD_LOCK_STATE.held = held
    if key in held:
        held[key] += 1
        try:
            yield
        finally:
            held[key] -= 1
        return

    lock_path = lock_root / f"{key}.lock"
    handle = lock_path.open("a+b")
    try:
        if os.name == "nt":
            import msvcrt

            if lock_path.stat().st_size == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        held[key] = 1
        yield
    finally:
        held.pop(key, None)
        if os.name == "nt":
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def atomic_write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path, value):
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{line_no}: invalid JSON: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{line_no}: each line must be a JSON object")
        rows.append(value)
    return rows


def append_jsonl(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json(value) + "\n")


def next_prefixed_id(values, prefix):
    highest = 0
    for value in values:
        if isinstance(value, str) and value.startswith(prefix) and value[len(prefix) :].isdigit():
            highest = max(highest, int(value[len(prefix) :]))
    return f"{prefix}{highest + 1}"


def id_sort_key(value):
    if isinstance(value, str) and len(value) > 1 and value[1:].isdigit():
        return value[0], int(value[1:])
    return str(value), 0


def latest_by_id(events, id_field):
    latest = {}
    for event in events:
        event_id = event.get(id_field)
        revision = event.get("revision")
        if not isinstance(event_id, str) or not isinstance(revision, int):
            continue
        previous = latest.get(event_id)
        if previous is None or revision > previous["revision"]:
            latest[event_id] = event
    return latest


def current_semantics(record_dir):
    latest = latest_by_id(read_jsonl(Path(record_dir) / "semantic-ledger.jsonl"), "semantic_id")
    return {
        semantic_id: event
        for semantic_id, event in latest.items()
        if event.get("operation") != "delete"
    }


def semantic_neighbors(record_dir):
    """Return direct, untyped, undirected related-semantic links."""
    semantics = current_semantics(record_dir)
    neighbors = {semantic_id: set() for semantic_id in semantics}
    for semantic_id, event in semantics.items():
        for related_id in event.get("related", []):
            if related_id in semantics and related_id != semantic_id:
                neighbors[semantic_id].add(related_id)
                neighbors[related_id].add(semantic_id)
    return {semantic_id: sorted(values, key=id_sort_key) for semantic_id, values in neighbors.items()}


def current_compromises(record_dir):
    latest = latest_by_id(read_jsonl(Path(record_dir) / "compromises.jsonl"), "compromise_id")
    return {
        compromise_id: event
        for compromise_id, event in latest.items()
        if event.get("status") not in {"resolved", "superseded"}
    }


def semantic_revision(event):
    return f"r{event.get('revision')}"


def related_semantic_revisions(record_dir, semantic_id):
    semantics = current_semantics(record_dir)
    neighbors = semantic_neighbors(record_dir)
    return {
        related_id: semantic_revision(semantics[related_id])
        for related_id in neighbors.get(semantic_id, [])
    }


def render_user_semantics(record_dir):
    grouped = defaultdict(list)
    semantics = current_semantics(record_dir)
    neighbors = semantic_neighbors(record_dir)
    for event in semantics.values():
        grouped[event["category"]].append(event)

    lines = [
        "# User Semantics",
        "",
        "This is the complete current user-design baseline. It is generated from `semantic-ledger.jsonl`; edit the ledger through `scripts/record_event.py`.",
        "",
    ]
    for category in SEMANTIC_CATEGORIES:
        rows = sorted(
            grouped.get(category, []),
            key=lambda row: id_sort_key(row["semantic_id"]),
        )
        if not rows:
            continue
        lines.extend([f"## {CATEGORY_HEADINGS[category]}", ""])
        for row in rows:
            related = neighbors.get(row["semantic_id"], [])
            suffix = f" _(related: {', '.join(related)})_" if related else ""
            lines.append(f"- `{row['semantic_id']}` {row['text']}{suffix}")
        lines.append("")
    if not any(grouped.values()):
        lines.append("No user semantics recorded yet.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def empty_audit_state():
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_snapshot": None,
        "coverage": {},
        "differences": [],
        "last_audit": None,
    }


def load_audit_state(record_dir):
    path = Path(record_dir) / "audit-state.json"
    if not path.exists():
        return empty_audit_state()
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("audit-state.json: root must be an object")
    return value


def save_audit_state(record_dir, state):
    atomic_write_json(Path(record_dir) / "audit-state.json", state)


def _ignored(relative):
    parts = Path(relative).parts
    return any(part in DEFAULT_IGNORED_PARTS for part in parts) or relative.endswith(".pyc")


def _normalize_scope(scope):
    text = str(scope).replace("\\", "/").strip()
    if text in {"", ".", "./"}:
        return "."
    normalized = Path(text)
    if normalized.is_absolute() or ".." in normalized.parts:
        raise ValueError(f"scope must stay inside the artifact root: {scope}")
    return normalized.as_posix().rstrip("/")


def _git_files(root, scopes):
    command = ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--"]
    command.extend(scopes)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    if result.returncode != 0:
        return None
    return [item.decode("utf-8", errors="surrogateescape") for item in result.stdout.split(b"\0") if item]


def _git_default_paths(root):
    candidates = _git_files(root, [])
    if candidates is None:
        return None
    paths = set()
    for raw_relative in candidates:
        relative = Path(raw_relative).as_posix()
        if _ignored(relative):
            continue
        path = root / relative
        if path.is_file() or path.is_symlink():
            paths.add(relative)
            continue
        if not path.is_dir():
            continue
        paths.add(relative)
        nested = _git_default_paths(path.resolve())
        if nested is None:
            nested = _walk_scopes(path.resolve(), ["."])
        for child in nested:
            paths.add((Path(relative) / child).as_posix())
    return sorted(paths)


def list_artifact_files(root, scopes=None):
    root = Path(root).resolve()
    normalized_scopes = [_normalize_scope(scope) for scope in (scopes or ["."])]
    candidates = _git_default_paths(root) if normalized_scopes == ["."] else None
    if candidates is None:
        candidates = _walk_scopes(root, normalized_scopes)

    files = []
    for relative in sorted(set(candidates)):
        relative = Path(relative).as_posix()
        if _ignored(relative):
            continue
        path = root / relative
        if path.is_file() or path.is_symlink() or path.is_dir():
            files.append(relative)
    return normalized_scopes, files


def _walk_scopes(root, scopes):
    candidates = []
    for scope in scopes:
        target = root if scope == "." else root / scope
        if target.is_file() or target.is_symlink():
            candidates.append(target.relative_to(root).as_posix())
        elif target.is_dir():
            for path in target.rglob("*"):
                if path.is_file() or path.is_symlink():
                    candidates.append(path.relative_to(root).as_posix())
    return sorted(set(path for path in candidates if not _ignored(path)))


def path_version(path):
    path = Path(path)
    if not (path.exists() or path.is_symlink()):
        return None
    stat = path.lstat()
    mode = oct(stat.st_mode & 0o777)
    if path.is_symlink():
        return f"symlink:{mode}:{stat.st_size}:{stat.st_mtime_ns}:{os.readlink(path)}"
    kind = "directory" if path.is_dir() else "file"
    return f"stat:{kind}:{mode}:{stat.st_size}:{stat.st_mtime_ns}"


def build_snapshot(root, scopes=None):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError(f"artifact root is not a directory: {root}")
    normalized_scopes = [_normalize_scope(scope) for scope in (scopes or ["."])]
    for scope in normalized_scopes:
        target = root if scope == "." else root / scope
        if not (target.exists() or target.is_symlink()):
            raise ValueError(f"artifact scope does not exist: {scope}")
    _normalized, files = list_artifact_files(root, normalized_scopes)
    return {
        "scopes": normalized_scopes,
        "files": {relative: path_version(root / relative) for relative in files},
    }


def snapshot_changes(previous, current):
    old_files = (previous or {}).get("files", {})
    new_files = current.get("files", {})
    old_paths = set(old_files)
    new_paths = set(new_files)
    return {
        "added": sorted(new_paths - old_paths),
        "modified": sorted(path for path in old_paths & new_paths if old_files[path] != new_files[path]),
        "deleted": sorted(old_paths - new_paths),
    }


def version_evidence(root, evidence_paths):
    root = Path(root).resolve()
    evidence = []
    for raw in evidence_paths:
        relative = _normalize_scope(raw)
        target = root if relative == "." else root / relative
        if target.is_file() or target.is_symlink():
            evidence.append({"path": relative, "kind": "file", "version": path_version(target)})
            continue
        if target.is_dir():
            members = {}
            for path in target.rglob("*"):
                if not (path.is_file() or path.is_symlink()):
                    continue
                member = path.relative_to(root).as_posix()
                if _ignored(member):
                    continue
                members[member] = path_version(path)
            evidence.append(
                {
                    "path": relative,
                    "kind": "directory",
                    "version": members,
                    "members": len(members),
                }
            )
            continue
        evidence.append({"path": relative, "kind": "missing", "version": None})
    return evidence


def stale_evidence(root, evidence):
    expected = {item["path"]: item for item in evidence}
    current = {item["path"]: item for item in version_evidence(root, expected)}
    return sorted(
        path
        for path, item in expected.items()
        if current.get(path, {}).get("kind") != item.get("kind")
        or "version" not in item
        or current.get(path, {}).get("version") != item.get("version")
    )


def evidence_label(evidence):
    return ", ".join(item.get("path", "?") for item in evidence) or "none"


def render_alignment_report(record_dir):
    record_dir = Path(record_dir)
    state = load_audit_state(record_dir)
    current_ids = set(current_semantics(record_dir))
    coverage = {
        semantic_id: item
        for semantic_id, item in state.get("coverage", {}).items()
        if semantic_id in current_ids
    }
    differences = [item for item in state.get("differences", []) if item.get("status") != "resolved"]
    compromises = current_compromises(record_dir)
    relevant_compromise_ids = set((state.get("last_audit") or {}).get("relevant_compromises", []))
    relevant_compromises = {
        compromise_id: item
        for compromise_id, item in compromises.items()
        if compromise_id in relevant_compromise_ids
    }
    counts = defaultdict(int)
    for item in coverage.values():
        counts[item.get("status", "unknown")] += 1

    audit_current = bool(state.get("last_audit") and state["last_audit"].get("current", True))
    if state.get("last_audit") and not audit_current:
        overall = "stale"
    elif any(item.get("type") == "conflict" for item in differences) or counts["conflict"]:
        overall = "conflict"
    elif differences or counts["partial"] or counts["unmet"] or counts["unknown"]:
        overall = "differences-present"
    elif state.get("last_audit"):
        overall = "aligned"
    else:
        overall = "not-audited"

    if state.get("last_audit") and not audit_current:
        validity = "working audit results are recorded, but the audit is not finalized; do not claim current alignment"
    elif state.get("last_audit"):
        validity = "the recorded semantic revisions, evidence, and artifact snapshot were finalized together"
    else:
        validity = "no trusted audit has been finalized"

    lines = [
        "# Alignment Report",
        "",
        "This is the generated user-facing view. Full semantics live in `user-semantics.md`; reusable audit evidence lives in `audit-state.json`.",
        "",
        "## Current Status",
        "",
        f"- Overall: {overall}",
        f"- Last audit: {(state.get('last_audit') or {}).get('completed_at', 'never')}",
        f"- Validity: {validity}.",
        f"- Coverage: satisfied={counts['satisfied']}, partial={counts['partial']}, unmet={counts['unmet']}, conflict={counts['conflict']}, unknown={counts['unknown']}",
        "",
        "## Implementation Differences",
        "",
    ]
    if differences:
        lines.extend(
            [
                "| ID | Type | Source | Implementation semantics | User basis | Impact | Evidence | Status |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for item in differences:
            basis = ",".join(item.get("user_semantics", [])) or "none"
            values = [
                item.get("id", "?"),
                item.get("type", "unknown"),
                item.get("source", "unknown"),
                item.get("implementation", ""),
                basis,
                item.get("impact", "unknown"),
                evidence_label(item.get("evidence", [])),
                item.get("status", "open"),
            ]
            lines.append("| " + " | ".join(_table_cell(value) for value in values) + " |")
    else:
        lines.append("No current implementation differences recorded.")

    lines.extend(["", "## Relevant Compromises", ""])
    if relevant_compromises:
        lines.extend(
            [
                "| ID | Gap | Actual choice | Recheck condition | Scope |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for compromise_id, item in sorted(relevant_compromises.items()):
            values = [
                compromise_id,
                item.get("gap", ""),
                item.get("actual_choice", ""),
                item.get("recheck_condition", ""),
                item.get("scope", ""),
            ]
            lines.append("| " + " | ".join(_table_cell(value) for value in values) + " |")
    else:
        lines.append(
            f"No active compromises were relevant to the last audit. Active compromises retained internally: {len(compromises)}."
        )

    return "\n".join(lines).rstrip() + "\n"


def _table_cell(value):
    return str(value).replace("|", "\\|").replace("\r\n", "<br>").replace("\n", "<br>").replace("\r", "<br>")
