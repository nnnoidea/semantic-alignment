# Semantic Record Schemas

Load this reference when exact v2 record fields or command shapes are needed.

## Directory

```text
<workspace-root>/.semantic-alignment/
  projects.json               # rebuildable routing index only

<project-root>/.semantic-alignment/
  project.json                # stable project identity and local layout
  user-semantics.md
  semantic-ledger.jsonl
  compromises.jsonl
  audit-state.json
  alignment-report.md
  archive/                    # optional migrated/retired material
```

Create it with:

```bash
python semantic-alignment/scripts/workspace.py init <project-root> \
  --workspace-root <workspace-root> --project-id <stable-project-id>
```

`user-semantics.md` and `alignment-report.md` are generated projections. Do not edit them manually.

## projects.json

The workspace index is a tool-written, rebuildable routing cache:

```json
{
  "schema_version": 1,
  "projects": [
    {
      "project_id": "example-project",
      "root": "projects/example-project",
      "record_dir": "projects/example-project/.semantic-alignment"
    }
  ]
}
```

All paths are workspace-relative. Entries contain no semantic or audit data. Use `scripts/workspace.py`; do not edit the index manually. Default `check` validates saved entries only; `check --discover` and `rebuild-index` perform a full manifest scan.

## project.json

Each project-local record set has a tool-written manifest:

```json
{
  "schema_version": 1,
  "project_id": "example-project",
  "artifact_root": ".",
  "record_dir": ".semantic-alignment"
}
```

This manifest is the discovery source used by `workspace.py rebuild-index`. The current schema deliberately fixes the artifact root to the project root and the record directory to `.semantic-alignment`, keeping ownership unambiguous.

## semantic-ledger.jsonl

One append-only JSON object per revision:

```json
{
  "semantic_id": "U1",
  "revision": 1,
  "date": "2026-09-04",
  "operation": "add",
  "category": "goal",
  "before": null,
  "text": "Preserve complete product design semantics.",
  "related": ["U2"],
  "reason": "clarification",
  "source": "User explicitly required a complete baseline.",
  "recorded_at": "2026-09-04T08:00:00Z"
}
```

Fields:

- `semantic_id`: stable `U<number>` identifier
- `revision`: contiguous revision number for this ID
- `operation`: `add`, `update`, or `delete`
- `category`: `goal`, `principle`, `context`, `global-design`, `local-design`, `system`, `content`, `process`, `constraint`, or `review`
- `before`: previous text, or `null` for the first revision
- `text`: current text, or `null` for deletion
- `related`: optional untyped direct semantic IDs; read as undirected and one level deep
- `reason`: `clarification`, `correction`, `optimization`, `constraint`, `implementation-discovery`, `agent-inference`, `scope-control`, `preference-change`, `deletion`, or `unknown`
- `source`: user statement or concise provenance

Use `scripts/record_event.py ... semantic`; it validates related IDs, computes IDs, revisions, `before`, timestamps, and regenerates `user-semantics.md`. Never edit this file manually.

## compromises.jsonl

One append-only JSON object per compromise revision:

```json
{
  "compromise_id": "C1",
  "revision": 1,
  "date": "2026-09-04",
  "operation": "add",
  "original_target": "Export a file directly",
  "actual_choice": "Copy content to the clipboard",
  "gap": "The user must create the file manually",
  "reason": "The runtime lacked file-write permission",
  "evidence": "The bounded write request was denied",
  "scope": "export workflow",
  "affected_user_semantics": ["U4"],
  "recheck_condition": "File-write permission becomes available",
  "recheck_method": "Attempt a bounded write in the configured output directory",
  "status": "active",
  "last_checked": "never",
  "recorded_at": "2026-09-04T08:00:00Z"
}
```

Statuses are `active`, `resolved`, and `superseded`. Preserve the original target and gap even after resolution.

## audit-state.json

This is the current machine-owned audit cache, not an append-only history file.

```json
{
  "schema_version": 2,
  "artifact_snapshot": {
    "scopes": ["."],
    "files": {"src/app.py": "stat:file:0o644:1200:1788750000000000000"},
    "completed_at": "2026-09-04T08:30:00Z"
  },
  "coverage": {
    "U1": {
      "semantic_revision": "r3",
      "related_semantics": {"U2": "r2"},
      "status": "satisfied",
      "source": "user-explicit",
      "relation": "implements",
      "implementation": "The artifact preserves the complete baseline.",
      "assertion_type": "obligation",
      "counterexample_review": "Checked routing, modes, exceptions, fallbacks, and early exits; no path bypasses the requirement.",
      "evidence": [
        {"path": "src/app.py", "kind": "file", "version": "stat:file:0o644:1200:1788750000000000000"}
      ],
      "notes": "Concrete audit conclusion",
      "audit_run_id": "full-20260904T080000Z",
      "audited_at": "2026-09-04T08:20:00Z"
    }
  },
  "differences": [
    {
      "id": "D1",
      "type": "added",
      "source": "agent-added",
      "relation": "extends",
      "implementation": "The artifact adds automatic retry.",
      "user_semantics": ["U1"],
      "semantic_revisions": {"U1": "r3"},
      "evidence": [
        {"path": "src/app.py", "kind": "file", "version": "stat:file:0o644:1200:1788750000000000000"}
      ],
      "impact": "low",
      "status": "open",
      "notes": "Not explicitly requested",
      "audit_run_id": "full-20260904T080000Z",
      "audited_at": "2026-09-04T08:20:00Z"
    }
  ],
  "last_audit": {
    "mode": "full",
    "completed_at": "2026-09-04T08:30:00Z",
    "audit_run_id": "full-20260904T080000Z",
    "current": true,
    "relevant_compromises": [],
    "reviewed_changes": {"added": [], "modified": [], "deleted": []},
    "semantic_count": 1,
    "file_count": 1
  }
}
```

Coverage status:

- `satisfied`, `partial`, `unmet`, `conflict`, `unknown`

Assertion type:

- `capability`: positive implementation evidence is sufficient
- `obligation`: every applicable path must produce the required result
- `prohibition`: no applicable path may produce the forbidden result

Current `record-coverage` writes `assertion_type` for every refreshed entry. Every satisfied entry also requires a non-empty `counterexample_review`; capability entries may explain that no universal constraint applies. Legacy cached entries may omit these fields until their normal semantic or artifact invalidation; once refreshed, the current tool requirements apply.

Implementation source:

- `user-explicit`, `user-inferred`, `agent-added`, `constraint-driven`, `unknown`

Relationship:

- `implements`, `extends`, `narrows`, `substitutes`, `conflicts`, `none`, `unknown`

Difference type:

- `added`, `enhanced`, `omitted`, `substituted`, `narrowed`, `conflict`, `artifact-drift`

Difference impact:

- `low`, `medium`, `high`

`related_semantics` captures the direct related context and revision numbers used for that conclusion. Unrelated semantics are intentionally absent and do not invalidate it.

Evidence `version` values use file type, size, nanosecond modification time, and mode. They intentionally do not hash file contents or use Git object IDs. Audit-rule document edits are not stored as a cache version and do not automatically invalidate conclusions.

`active_audit` is optional and exists only while a full audit is in progress:

```json
{
  "active_audit": {
    "run_id": "full-20260904T080000Z",
    "mode": "full",
    "artifact_root": "/workspace/example-project",
    "scopes": ["."],
    "started_at": "2026-09-04T08:00:00Z",
    "user_authorized": true
  }
}
```

Full-audit coverage and difference entries written during that run include `audit_run_id`; older cached entries may omit it and remain valid for incremental planning, but they cannot satisfy a later `finalize --mode full`.

Do not hand-edit coverage, differences, evidence versions, or snapshots. Use `scripts/audit.py`, and record each semantic conclusion immediately after auditing its small related context.

## user-semantics.md

Generated from the latest non-deleted revision of every stable user semantic ID. It groups complete current semantics by category and intentionally excludes history, implementation findings, and agent rationale.

## alignment-report.md

Generated from `audit-state.json` and current compromises. It is the default user-facing view and contains:

- overall audit status and compact coverage counts
- current implementation differences
- active compromises and their recheck conditions

The absence of a difference row does not prove current alignment unless the audit state is current and complete.

## Validation

```bash
python semantic-alignment/scripts/validate_records.py <project-root>/.semantic-alignment/
```

Validation checks record structure, event revision sequences, controlled values, cross-record IDs, and generated projections. Artifact freshness is checked by `audit.py plan`, because validation alone does not know which artifact root to inspect.
