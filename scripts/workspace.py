#!/usr/bin/env python3
"""Manage project-local semantic records from a workspace index."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from init_records import initialize
from recordlib import atomic_write_json, record_lock


WORKSPACE_SCHEMA_VERSION = 1
PROJECT_SCHEMA_VERSION = 1
INDEX_RELATIVE_PATH = Path(".semantic-alignment/projects.json")
PROJECT_RECORD_DIR = Path(".semantic-alignment")
PROJECT_MANIFEST = "project.json"
REQUIRED_RECORD_FILES = {
    "semantic-ledger.jsonl",
    "compromises.jsonl",
    "audit-state.json",
    "user-semantics.md",
    "alignment-report.md",
}
SCAN_IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}


def normalize_project_id(value):
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not normalized:
        raise ValueError("project ID must contain at least one letter or digit")
    return normalized


def relative_path(path, root, label):
    path = Path(path).resolve()
    root = Path(root).resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label} must stay inside the workspace: {path}") from exc
    return "." if relative == Path(".") else relative.as_posix()


def path_from_workspace(workspace_root, relative, label):
    relative_path_value = Path(relative)
    if relative_path_value.is_absolute() or ".." in relative_path_value.parts:
        raise ValueError(f"{label} must be a workspace-relative path: {relative!r}")
    resolved = (workspace_root / relative_path_value).resolve()
    relative_path(resolved, workspace_root, label)
    return resolved


def empty_index():
    return {"schema_version": WORKSPACE_SCHEMA_VERSION, "projects": []}


def load_index(workspace_root, required=False):
    index_path = workspace_root / INDEX_RELATIVE_PATH
    if not index_path.exists():
        if required:
            raise ValueError(f"workspace index does not exist: {index_path}")
        return empty_index()
    try:
        value = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{index_path}: invalid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError("workspace index root must be an object")
    if value.get("schema_version") != WORKSPACE_SCHEMA_VERSION:
        raise ValueError(
            f"workspace index schema_version must be {WORKSPACE_SCHEMA_VERSION}"
        )
    if not isinstance(value.get("projects"), list):
        raise ValueError("workspace index projects must be an array")
    return value


def save_index(workspace_root, entries):
    ordered = sorted(entries, key=lambda item: item["project_id"])
    atomic_write_json(
        workspace_root / INDEX_RELATIVE_PATH,
        {"schema_version": WORKSPACE_SCHEMA_VERSION, "projects": ordered},
    )


def project_entry(workspace_root, project_root, project_id):
    root = relative_path(project_root, workspace_root, "project root")
    record_dir = PROJECT_RECORD_DIR if root == "." else Path(root) / PROJECT_RECORD_DIR
    return {
        "project_id": normalize_project_id(project_id),
        "root": root,
        "record_dir": record_dir.as_posix(),
    }


def project_manifest(project_id):
    return {
        "schema_version": PROJECT_SCHEMA_VERSION,
        "project_id": normalize_project_id(project_id),
        "artifact_root": ".",
        "record_dir": PROJECT_RECORD_DIR.as_posix(),
    }


def load_manifest(record_dir):
    path = Path(record_dir) / PROJECT_MANIFEST
    if not path.exists():
        raise ValueError(f"missing project manifest: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be an object")
    if value.get("schema_version") != PROJECT_SCHEMA_VERSION:
        raise ValueError(f"{path}: unsupported schema_version")
    project_id = value.get("project_id")
    if not isinstance(project_id, str) or normalize_project_id(project_id) != project_id:
        raise ValueError(f"{path}: invalid project_id")
    if value.get("artifact_root") != "." or value.get("record_dir") != ".semantic-alignment":
        raise ValueError(f"{path}: artifact_root and record_dir must describe the project-local layout")
    return value


def validate_entries(workspace_root, entries, require_files=True, require_paths=True):
    errors = []
    normalized = []
    seen_ids = {}
    seen_roots = {}

    for position, entry in enumerate(entries):
        prefix = f"projects[{position}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: entry must be an object")
            continue
        project_id = entry.get("project_id")
        root_value = entry.get("root")
        record_value = entry.get("record_dir")
        try:
            if not isinstance(project_id, str) or normalize_project_id(project_id) != project_id:
                raise ValueError("invalid project_id")
            if not isinstance(root_value, str) or not isinstance(record_value, str):
                raise ValueError("root and record_dir must be strings")
            project_root = path_from_workspace(workspace_root, root_value, f"{prefix}.root")
            record_dir = path_from_workspace(workspace_root, record_value, f"{prefix}.record_dir")
            if record_dir != project_root / PROJECT_RECORD_DIR:
                raise ValueError("record_dir must be <project-root>/.semantic-alignment")
        except ValueError as exc:
            errors.append(f"{prefix}: {exc}")
            continue

        if project_id in seen_ids:
            errors.append(
                f"duplicate project_id {project_id!r}: {seen_ids[project_id]} and {root_value}"
            )
        else:
            seen_ids[project_id] = root_value
        if project_root in seen_roots:
            errors.append(
                f"duplicate project root {root_value!r}: {seen_roots[project_root]} and {project_id}"
            )
        else:
            seen_roots[project_root] = project_id

        normalized.append((project_id, project_root, record_dir, entry))

        if not require_paths:
            continue
        if not project_root.is_dir():
            errors.append(f"stale project path for {project_id}: {project_root}")
            continue
        if not record_dir.is_dir():
            errors.append(f"missing record directory for {project_id}: {record_dir}")
            continue
        try:
            manifest = load_manifest(record_dir)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if manifest["project_id"] != project_id:
            errors.append(
                f"project ID mismatch for {project_root}: index={project_id}, manifest={manifest['project_id']}"
            )
        if require_files:
            missing = sorted(name for name in REQUIRED_RECORD_FILES if not (record_dir / name).exists())
            if missing:
                errors.append(f"incomplete record set for {project_id}: {', '.join(missing)}")

    for index, (left_id, left_root, _left_records, _left_entry) in enumerate(normalized):
        for right_id, right_root, _right_records, _right_entry in normalized[index + 1 :]:
            if left_root in right_root.parents or right_root in left_root.parents:
                errors.append(
                    f"overlapping active project roots: {left_id}={left_root} and {right_id}={right_root}"
                )
    return errors


def discover_projects(workspace_root):
    entries = []
    for current, directories, _files in os.walk(workspace_root):
        directories[:] = [name for name in directories if name not in SCAN_IGNORED_DIRS]
        if PROJECT_RECORD_DIR.name not in directories:
            continue
        project_root = Path(current).resolve()
        record_dir = project_root / PROJECT_RECORD_DIR
        manifest_path = record_dir / PROJECT_MANIFEST
        directories.remove(PROJECT_RECORD_DIR.name)
        if not manifest_path.exists():
            continue
        manifest = load_manifest(record_dir)
        entries.append(project_entry(workspace_root, project_root, manifest["project_id"]))
    return entries


def report_entries(entries, as_json=False):
    if as_json:
        print(json.dumps(entries, ensure_ascii=False, indent=2, sort_keys=True))
        return
    for entry in entries:
        print(f"{entry['project_id']}\t{entry['root']}\t{entry['record_dir']}")


def command_init(args):
    workspace_root = Path(args.workspace_root).resolve()
    project_root = Path(args.project_root).resolve()
    if not workspace_root.is_dir():
        raise ValueError(f"workspace root is not a directory: {workspace_root}")
    if not project_root.is_dir():
        raise ValueError(f"project root is not a directory: {project_root}")
    project_id = normalize_project_id(args.project_id or project_root.name)
    entry = project_entry(workspace_root, project_root, project_id)
    index_lock_dir = workspace_root / INDEX_RELATIVE_PATH.parent

    with record_lock(index_lock_dir):
        index = load_index(workspace_root)
        errors = validate_entries(workspace_root, index["projects"], require_files=True)
        candidate_entries = []
        for existing in index["projects"]:
            same_id = existing.get("project_id") == project_id
            same_root = existing.get("root") == entry["root"]
            if same_id and not same_root:
                errors.append(
                    f"project_id {project_id!r} is already registered at {existing.get('root')!r}"
                )
            if same_root and not same_id:
                errors.append(
                    f"project root {entry['root']!r} is already registered as {existing.get('project_id')!r}"
                )
            if not (same_id and same_root):
                candidate_entries.append(existing)
        candidate_entries.append(entry)
        errors.extend(
            validate_entries(
                workspace_root,
                candidate_entries,
                require_files=False,
                require_paths=False,
            )
        )
        if errors:
            raise ValueError("cannot initialize project:\n- " + "\n- ".join(sorted(set(errors))))

        record_dir = project_root / PROJECT_RECORD_DIR
        with record_lock(record_dir):
            result = initialize(record_dir)
            if result:
                return result
            manifest_path = record_dir / PROJECT_MANIFEST
            if manifest_path.exists():
                existing_manifest = load_manifest(record_dir)
                if existing_manifest["project_id"] != project_id:
                    raise ValueError(
                        f"project already has ID {existing_manifest['project_id']!r}, not {project_id!r}"
                    )
            else:
                atomic_write_json(manifest_path, project_manifest(project_id))
        save_index(workspace_root, candidate_entries)

    print(f"registered: {project_id}")
    print(f"record directory: {record_dir}")
    return 0


def command_list(args):
    workspace_root = Path(args.workspace_root).resolve()
    index = load_index(workspace_root, required=True)
    errors = validate_entries(workspace_root, index["projects"], require_files=False)
    if errors:
        raise ValueError("invalid workspace index:\n- " + "\n- ".join(errors))
    report_entries(index["projects"], args.json)
    return 0


def command_resolve(args):
    workspace_root = Path(args.workspace_root).resolve()
    target = Path(args.path).resolve()
    relative_path(target, workspace_root, "target path")
    index = load_index(workspace_root, required=True)
    errors = validate_entries(workspace_root, index["projects"], require_files=True)
    if errors:
        raise ValueError("invalid workspace index:\n- " + "\n- ".join(errors))
    matches = []
    for entry in index["projects"]:
        project_root = path_from_workspace(workspace_root, entry["root"], "project root")
        if target == project_root or project_root in target.parents:
            matches.append(entry)
    if not matches:
        raise ValueError(f"no registered project owns path: {target}")
    if len(matches) != 1:
        ids = ", ".join(item["project_id"] for item in matches)
        raise ValueError(f"multiple registered projects own path {target}: {ids}")
    entry = matches[0]
    if args.json:
        value = dict(entry)
        value["absolute_root"] = str(path_from_workspace(workspace_root, entry["root"], "project root"))
        value["absolute_record_dir"] = str(
            path_from_workspace(workspace_root, entry["record_dir"], "record directory")
        )
        print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(path_from_workspace(workspace_root, entry["record_dir"], "record directory"))
    return 0


def command_check(args):
    workspace_root = Path(args.workspace_root).resolve()
    index = load_index(workspace_root, required=True)
    errors = validate_entries(workspace_root, index["projects"], require_files=True)
    if args.discover:
        discovered = discover_projects(workspace_root)
        indexed_pairs = {(item.get("project_id"), item.get("root")) for item in index["projects"]}
        discovered_pairs = {(item["project_id"], item["root"]) for item in discovered}
        for project_id, root in sorted(discovered_pairs - indexed_pairs):
            errors.append(f"unindexed project record: {project_id} at {root}")
        for project_id, root in sorted(indexed_pairs - discovered_pairs):
            errors.append(f"indexed project record was not discovered: {project_id} at {root}")
        errors.extend(validate_entries(workspace_root, discovered, require_files=True))
    errors = sorted(set(errors))
    if args.json:
        print(json.dumps({"ok": not errors, "projects": index["projects"], "errors": errors}, ensure_ascii=False, indent=2, sort_keys=True))
    elif errors:
        for error in errors:
            print(f"error: {error}")
    else:
        print(f"workspace index ok: {len(index['projects'])} project(s)")
    return 0 if not errors else 1


def command_rebuild(args):
    workspace_root = Path(args.workspace_root).resolve()
    if not workspace_root.is_dir():
        raise ValueError(f"workspace root is not a directory: {workspace_root}")
    with record_lock(workspace_root / INDEX_RELATIVE_PATH.parent):
        entries = discover_projects(workspace_root)
        errors = validate_entries(workspace_root, entries, require_files=True)
        if errors:
            raise ValueError("cannot rebuild workspace index:\n- " + "\n- ".join(errors))
        save_index(workspace_root, entries)
    if args.json:
        report_entries(entries, as_json=True)
    else:
        print(f"rebuilt workspace index: {len(entries)} project(s)")
    return 0


def command_archive_project(args):
    workspace_root = Path(args.workspace_root).resolve()
    project_id = normalize_project_id(args.project_id)
    index_lock_dir = workspace_root / INDEX_RELATIVE_PATH.parent

    with record_lock(index_lock_dir):
        index = load_index(workspace_root, required=True)
        matches = [item for item in index["projects"] if item.get("project_id") == project_id]
        if not matches:
            raise ValueError(f"project is not registered: {project_id}")
        if len(matches) != 1:
            raise ValueError(f"project ID is ambiguous in the saved index: {project_id}")
        entry = matches[0]
        project_root = path_from_workspace(workspace_root, entry["root"], "project root")
        record_dir = path_from_workspace(workspace_root, entry["record_dir"], "record directory")
        if project_root == workspace_root:
            raise ValueError("cannot archive a project whose root is the workspace root")
        errors = validate_entries(workspace_root, index["projects"], require_files=True)
        if errors:
            raise ValueError("invalid workspace index:\n- " + "\n- ".join(errors))

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive_parent = project_root / ".semantic-alignment-archive"
        destination = archive_parent / f"{project_id}-{stamp}"
        suffix = 2
        while destination.exists():
            destination = archive_parent / f"{project_id}-{stamp}-{suffix}"
            suffix += 1

        archive_parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(record_dir), str(destination))
        try:
            remaining = [item for item in index["projects"] if item is not entry]
            save_index(workspace_root, remaining)
        except Exception:
            shutil.move(str(destination), str(record_dir))
            raise

    print(f"archived project records: {destination}")
    print(f"unregistered: {project_id}")
    return 0


def add_workspace_option(parser):
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="Workspace root containing .semantic-alignment/projects.json (default: current directory)",
    )


def build_parser():
    parser = argparse.ArgumentParser(description="Manage project-local semantic-alignment records.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize and register a project-local record set")
    init_parser.add_argument("project_root")
    init_parser.add_argument("--project-id", help="Stable lowercase kebab-case project ID")
    add_workspace_option(init_parser)
    init_parser.set_defaults(handler=command_init)

    list_parser = subparsers.add_parser("list", help="List projects from the saved workspace index")
    add_workspace_option(list_parser)
    list_parser.add_argument("--json", action="store_true")
    list_parser.set_defaults(handler=command_list)

    resolve_parser = subparsers.add_parser("resolve", help="Resolve a path to exactly one project record set")
    resolve_parser.add_argument("path")
    add_workspace_option(resolve_parser)
    resolve_parser.add_argument("--json", action="store_true")
    resolve_parser.set_defaults(handler=command_resolve)

    check_parser = subparsers.add_parser("check", help="Check index, manifests, paths, and ownership conflicts")
    add_workspace_option(check_parser)
    check_parser.add_argument(
        "--discover",
        action="store_true",
        help="Also scan the workspace for unindexed project manifests",
    )
    check_parser.add_argument("--json", action="store_true")
    check_parser.set_defaults(handler=command_check)

    rebuild_parser = subparsers.add_parser(
        "rebuild-index", help="Rebuild the saved index from project-local manifests"
    )
    add_workspace_option(rebuild_parser)
    rebuild_parser.add_argument("--json", action="store_true")
    rebuild_parser.set_defaults(handler=command_rebuild)

    archive_parser = subparsers.add_parser(
        "archive-project",
        help="Archive a project record set and remove it from the saved index",
    )
    archive_parser.add_argument("project_id")
    add_workspace_option(archive_parser)
    archive_parser.set_defaults(handler=command_archive_project)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.handler(args)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
