# Semantic Alignment

[中文说明](README.zh-CN.md)

AI agents often fail not by refusing to implement, but by quietly producing something different from what the user meant.

`semantic-alignment` preserves the complete user-design baseline, derives implementation semantics from the real artifact, and shows the user the differences. Users do not need to read every internal record; they can judge whether the differences are acceptable.

It is intentionally limited to durable product and system design. Routine experiments, research runs, transient analysis, and ordinary writing do not get semantic records unless the user explicitly requests them or the artifact is a canonical contract for future implementation. Accepted experimental conclusions are recorded as decisions in the owning product project, not as separate experiment projects.

## Core Design

The workflow persistently authors only information that cannot be recovered reliably from code:

- user design semantics: goals, principles, global/local design, constraints, and acceptance criteria
- compromises: original target, actual choice, gap, reason, evidence, and recheck condition

If a user states or accepts durable product/system meaning, it is persisted even when the change is small or low-risk. There is no conversation-only mode for durable semantics; lightness comes from incremental audit reuse, not from dropping the record.

Implementation semantics are not maintained as a second hand-written specification during development. They are derived by auditing the actual code, design, document, configuration, tests, or output.

Audit results are cached against:

```text
user semantic revision + direct related semantics and revisions + evidence scope/file-state versions + reviewed artifact snapshot
```

Each semantic can retain a small, untyped, one-level `related` set. A semantic audit starts from one user semantic and loads only its direct related context. Unchanged results are reused, and unrelated semantic changes do not invalidate them.

After auditing a semantic and its small related context, the agent records the conclusion immediately through the tool instead of waiting for the entire audit. Persisted per-semantic coverage makes interrupted or compacted work resumable.

For requirements expressed as obligations or prohibitions, an audit must also inspect routing, modes, exceptions, fallbacks, and early exits. A working main path proves capability, not that every applicable path preserves the user's meaning.

## What Users See

The default report contains decision-relevant differences:

- behavior added or enhanced without an explicit request
- requested behavior that is omitted, substituted, narrowed, or contradicted
- artifact drift
- compromises whose recheck condition may now be relevant

Tests, retries, validation, or checksum verification remain visible differences when the user did not request them, even if they are beneficial.

## Record Set

Each project owns its authoritative records locally:

```text
<project-root>/.semantic-alignment/
  project.json
  user-semantics.md
  semantic-ledger.jsonl
  compromises.jsonl
  audit-state.json
  alignment-report.md
```

- `project.json`: stable project identity and local record layout
- `user-semantics.md`: complete current user-design baseline
- `semantic-ledger.jsonl`: append-only user-semantic revisions with stable IDs
- `compromises.jsonl`: durable compromises and recheck conditions
- `audit-state.json`: implementation findings, low-cost evidence versions, coverage, and artifact snapshot
- `alignment-report.md`: concise current differences and active compromises

User semantics, compromises, and audit conclusions are recorded through the scripts. Both Markdown views are generated; the agent does not hand-edit ledgers, audit state, or projections.

A multi-project workspace stores one routing-only index:

```text
<workspace-root>/.semantic-alignment/projects.json
```

The index contains only stable project IDs and relative paths. It is generated from project-local manifests and never duplicates semantics, compromises, differences, or audit coverage. `related` links stay inside one project; genuinely shared semantics belong to a separately registered common-parent project.

## Incremental Audit

```bash
python semantic-alignment/scripts/audit.py <record-dir> plan --artifact-root <project-root>
```

The plan reports changed artifact paths, missing semantic coverage, invalidated cached results, direct related context, stale difference evidence, and whether a full audit is required. After inspecting each semantic against the real artifact and recording findings immediately, the agent finalizes a new trusted snapshot.

A full audit must start with an explicit, user-authorized run:

```bash
python semantic-alignment/scripts/audit.py <record-dir> begin-full \
  --artifact-root <project-root> --confirm-user-authorized
```

`finalize --mode full` then requires `--confirm-full-scope-reviewed` and refuses to reuse old coverage or open differences that were not refreshed in that active run.

## Compromise Reminders

Compromises are recorded when the decision occurs because their reasons cannot be reconstructed safely from code. They are surfaced only when current work touches their scope or new evidence matches the recorded recheck condition.

## Initialize And Migrate

Initialize and register project-local v2 records:

```bash
python semantic-alignment/scripts/workspace.py init <project-root> \
  --workspace-root <workspace-root> --project-id <stable-project-id>
```

List, resolve, verify, or rebuild the workspace index:

```bash
python semantic-alignment/scripts/workspace.py list --workspace-root <workspace-root>
python semantic-alignment/scripts/workspace.py resolve <artifact-path> --workspace-root <workspace-root>
python semantic-alignment/scripts/workspace.py check --workspace-root <workspace-root>
python semantic-alignment/scripts/workspace.py check --workspace-root <workspace-root> --discover
python semantic-alignment/scripts/workspace.py archive-project <project-id> --workspace-root <workspace-root>
python semantic-alignment/scripts/workspace.py rebuild-index --workspace-root <workspace-root>
```

The default check validates the saved index without rescanning the workspace. Use `--discover` only when looking for unindexed project manifests.

Legacy workspace-level or multi-record layouts can be consolidated into the project-local record set with `scripts/migrate_v1.py <legacy-record-dir> --into <project-root>/.semantic-alignment --source-label <label>`. Preview first, then add `--apply`. Confirmed superseded mirrors can be retained under the target archive with `--archive-only`.

Preview and apply migration from v1:

```bash
python semantic-alignment/scripts/migrate_v1.py <record-dir>
python semantic-alignment/scripts/migrate_v1.py <record-dir> --apply
```

Migration archives legacy files. Old audit conclusions are not treated as reusable cache entries because their evidence scope and file-state versions are incomplete, so a baseline full audit is required before alignment can be claimed; the user must request or accept that audit first.

## Installation

Install this repository as a Codex-compatible skill named `semantic-alignment`. The record model is designed to remain platform-neutral.
