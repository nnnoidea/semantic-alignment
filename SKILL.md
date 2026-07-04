---
name: semantic-alignment
description: Mandatory project/design semantic alignment workflow. Use before and during any non-trivial project design, implementation, refactor, product, writing, UI/UX, architecture, or artifact creation task where an agent must preserve user goals, read existing semantic records, track global/local semantics, record semantic changes and reasons, classify agent assumptions, manage constraint-driven compromises, remind users when an audit may be needed, and check consistency between user intent, agent interpretation, and actual code/design/artifacts.
---

# Semantic Alignment

Use this skill to keep non-trivial project/design/artifact work aligned with the user's real goal as conversation, constraints, implementation choices, and artifacts evolve.

Load this skill before planning or editing. Unread semantic records do not protect alignment.

## Startup Checklist

Before substantial work, do this in order:

1. Identify the project and record directory, usually `.semantic-alignment/<project-slug>/` under the relevant project or workspace. The slug is a stable project identifier, not an individual work item.
   - Prefer an explicit user-provided project name/slug.
   - Otherwise use the nearest repository root directory name.
   - Otherwise use a project manifest/package name when available.
   - Otherwise use the current project directory name.
   - Normalize to lowercase kebab-case. If multiple plausible projects match, list the candidates and ask instead of inventing a new baseline.
2. If it exists, read `user-semantics.md`, `index.md`, and `recheck-triggers.md`.
3. Choose the recording level: None, Light, Standard, or Deep.
4. If Standard/Deep records are missing, create them with `scripts/init_records.py`.
5. Load the required reference before acting: semantic change -> `semantic-model.md`; record edits -> `operational-workflow.md`; audit/reopen -> `audit-rules.md`; schema edits -> `semantic-record-template.md`.

## Core Workflow

1. Establish the current semantic frame before substantial work:
   - read `user-semantics.md`, `index.md`, and `recheck-triggers.md` when they exist and are not already fresh in context
   - reread when the session is new, context was compacted, record files may have changed, the user asks for an audit, or the user message appears to change project meaning
2. Compare new user requests against the current frame:
   - direct conflicts with current goals, principles, constraints, review criteria, or local requirements
   - likely semantic add/update/delete
   - active recheck trigger condition becoming true
   - evidence from real artifacts, tool availability, permissions, dependencies, user statements, or audit findings that may satisfy an active recheck trigger
3. Do not silently change the user-semantic baseline. Ask for confirmation when a change affects goal, product meaning, architecture, UX direction, public copy, delivery criteria, or a meaningful route choice.
   - when a recheck trigger becomes true, state the old compromise/route and the now-true condition before continuing
   - if the user simultaneously says to keep the old compromised route, still surface the reminder once; treat it as confirmation only when the wording is explicit
4. Record accepted semantic changes in `user-semantic-ledger.md`, then run `scripts/sync_triggers.py <record-dir>` if recheck triggers changed, then project the current state into `user-semantics.md`.
5. During implementation, keep `realization-semantics.md` current as non-obvious intended artifact semantics appear, change, or become obsolete; classify agent additions as `grounded`, `added`, `risky`, or `divergent`.
6. After implementation or before delivery, check the real artifact against realization semantics in `artifact-checks.md`.
7. Before a full audit, inspect the real project/artifact, update or confirm `realization-semantics.md`, then refresh or confirm `artifact-checks.md`; only the updated realization semantics are valid audit input.
8. For full audits, cover every current user semantic and every active realization semantic; run `scripts/check_audit_coverage.py <record-dir>` before claiming completion.
9. Recommend, or run if user-requested/accepted, an audit when meaningful drift signals exist.

## Recheck Trigger Use

Recheck triggers are early-warning conditions for old semantic decisions. They are not tasks and not recommendations. When a trigger appears true, read the linked `user-semantic-ledger.md` row, identify the old decision or compromise, and decide whether the baseline should be reopened.

Read and evaluate `recheck-triggers.md`:

- at startup when loading an existing semantic frame
- before meaningful planning, implementation, or delivery when the frame may be stale
- when the user says a constraint, tool, permission, dependency, asset, or requirement has changed
- when implementation or artifact checks reveal new evidence relevant to a recorded trigger
- before and during user-requested audits

If a trigger appears true, make the reminder visible to the user before continuing with the old route, resolving the trigger, or changing the semantic baseline.

## Record Setup

For Standard or Deep tracking, use a project- or workspace-local metadata directory. The record unit is the project. Workspace-local storage is acceptable when a workspace contains multiple projects, as long as each project has a distinct slug:

```text
.semantic-alignment/<project-slug>/
```

`<project-slug>` is a stable, lowercase kebab-case project identifier derived from an explicit user name, repository root, manifest/package name, or project directory. Do not use a short-lived task name as the slug.

Create and maintain records with scripts:

```bash
python semantic-alignment/scripts/init_records.py .semantic-alignment/<project-slug>/ --title "<Project Name>"
python semantic-alignment/scripts/record_event.py .semantic-alignment/<project-slug>/ ledger --operation add --category process --before none --after "..." --reason clarification --source "..."
python semantic-alignment/scripts/sync_triggers.py .semantic-alignment/<project-slug>/
python semantic-alignment/scripts/validate_records.py .semantic-alignment/<project-slug>/
python semantic-alignment/scripts/lint_records.py .semantic-alignment/<project-slug>/
python semantic-alignment/scripts/check_audit_coverage.py .semantic-alignment/<project-slug>/
python semantic-alignment/scripts/export_structured.py .semantic-alignment/<project-slug>/
```

Standard files:

- `user-semantics.md`: user-readable current baseline only
- `user-semantic-ledger.md`: authoritative add/update/delete history with reasons and recheck triggers
- `recheck-triggers.md`: generated compact current trigger projection for frequent reads
- `realization-semantics.md`: intended artifact semantics after agent interpretation/gap filling
- `artifact-checks.md`: mechanical pass/partial/fail artifact checks
- `audits.md`: current audit summary plus audit events
- `index.md`: current semantic frame and known unknowns
- `structured/*.jsonl`: optional generated structured mirrors for selected non-user-entry records

Keep semantic records out of source directories, design exports, release artifacts, and end-user documentation unless explicitly configured.

## Reference Loading

Load only the reference needed for the current action:

- `references/semantic-model.md`: read when deciding whether a user message changes semantics, classifying categories/reasons, or writing ledger/realization entries.
- `references/operational-workflow.md`: read when starting Standard/Deep tracking, deciding required reads, updating records, syncing triggers, or handling semantic changes during work.
- `references/audit-rules.md`: read when the user requests/accepts an audit, when recommending an audit, before final delivery with drift signals, or when a constraint/recheck trigger may reopen a route.
- `references/semantic-record-template.md`: read when creating records, editing table shape, or needing exact file schemas.

If the needed reference is not loaded, load it before making that decision or edit.

## Minimal Rules

- Record user semantics, not every user utterance.
- Keep `user-semantics.md` readable and concise; it is the user's review entry point.
- Use `user-semantic-ledger.md` as the single action-bearing history for accepted user-baseline changes.
- Prefer `scripts/record_event.py` for appending ledger, realization, and artifact-check rows; hand-edit only when the script cannot express the needed change.
- Write recheck triggers as observable conditions that mean "revisit this ledger entry"; do not use them for open tasks, recommendations, or actions.
- Evaluate active recheck triggers against new user messages, implementation discoveries, artifact checks, and audit evidence; do not treat trigger rows as passive documentation.
- Do not create a second generic semantic-change log.
- Do not persist unaccepted agent suggestions or limitations that have no actual effect.
- Treat realization semantics as intended artifact semantics; the real artifact is checked, not duplicated as another semantic layer.
- Keep realization semantics current during implementation, not only during audit. Do not let `realization-semantics.md` become a long history file; mark obsolete rows `revised`/`rejected` only while useful, and archive old non-current material when it stops helping routine reads.
- Keep `audits.md` focused on the current summary and recent material events; archive older resolved/accepted/superseded events when the file becomes hard to scan.
- Full audits are user-initiated or user-accepted. Proactively warn only on direct, material contradictions, divergent realization semantics, material artifact check failures, or clearly resolved stale constraints.
- Do not audit against stale realization semantics. A full audit must first inspect the real project, update or explicitly confirm `realization-semantics.md`, and refresh or explicitly confirm `artifact-checks.md`.
- Do not summarize a full audit in aggregate only. The latest audit event must include exhaustive user-semantic and realization-semantic coverage tables, and `scripts/check_audit_coverage.py <record-dir>` must pass before reporting the audit as complete.
- Do not mark a stale-route trigger handled only inside records; the user-facing response must show the reminder or confirmation basis.
- Do not claim alignment, stale-constraint resolution, or audit readiness without reading the relevant current records.

## Recording Level

Use the lightest level that protects alignment:

- **None**: tiny, reversible, mechanical tasks.
- **Light**: short semantic tasks; keep the semantic frame in conversation unless the task continues.
- **Standard**: multi-step implementation/design work; create the standard record directory.
- **Deep**: high-impact, ambiguous, long-running, or user-facing work; use full records and audits at major checkpoints.
