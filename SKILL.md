---
name: semantic-alignment
description: Mandatory project/design semantic alignment workflow. Use before and during any non-trivial project design, implementation, refactor, product, writing, UI/UX, architecture, or artifact creation task where an agent must preserve user goals, read existing semantic records, track global/local semantics, record semantic changes and reasons, classify agent assumptions, manage constraint-driven compromises, remind users when an audit may be needed, and check consistency between user intent, agent interpretation, and actual code/design/artifacts.
---

# Semantic Alignment

Use this skill to keep non-trivial project/design/artifact work aligned with the user's real goal as conversation, constraints, implementation choices, and artifacts evolve.

Load this skill before planning or editing. Unread semantic records do not protect alignment.

## Startup Checklist

Before substantial work, do this in order:

1. Locate the record directory, usually `.semantic-alignment/<task-slug>/`.
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
3. Do not silently change the user-semantic baseline. Ask for confirmation when a change affects goal, product meaning, architecture, UX direction, public copy, delivery criteria, or a meaningful route choice.
   - when a recheck trigger becomes true, state the old compromise/route and the now-true condition before continuing
   - if the user simultaneously says to keep the old compromised route, still surface the reminder once; treat it as confirmation only when the wording is explicit
4. Record accepted semantic changes in `user-semantic-ledger.md`, then run `scripts/sync_triggers.py <record-dir>` if recheck triggers changed, then project the current state into `user-semantics.md`.
5. Record non-obvious intended artifact semantics in `realization-semantics.md`; classify agent additions as `grounded`, `added`, `risky`, or `divergent`.
6. After implementation or before delivery, check the real artifact against realization semantics in `artifact-checks.md`.
7. Recommend, or run if user-requested/accepted, an audit when meaningful drift signals exist.

## Record Setup

For Standard or Deep tracking, use a project-local metadata directory:

```text
.semantic-alignment/<task-slug>/
```

Create and maintain records with scripts:

```bash
python semantic-alignment/scripts/init_records.py .semantic-alignment/<task-slug>/ --title "<Task Name>"
python semantic-alignment/scripts/record_event.py .semantic-alignment/<task-slug>/ ledger --operation add --category process --before none --after "..." --reason clarification --source "..."
python semantic-alignment/scripts/sync_triggers.py .semantic-alignment/<task-slug>/
python semantic-alignment/scripts/validate_records.py .semantic-alignment/<task-slug>/
python semantic-alignment/scripts/lint_records.py .semantic-alignment/<task-slug>/
python semantic-alignment/scripts/export_structured.py .semantic-alignment/<task-slug>/
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
- Do not create a second generic semantic-change log.
- Do not persist unaccepted agent suggestions or limitations that have no actual effect.
- Treat realization semantics as intended artifact semantics; the real artifact is checked, not duplicated as another semantic layer.
- Full audits are user-initiated or user-accepted. Proactively warn only on direct, material contradictions, divergent realization semantics, material artifact check failures, or clearly resolved stale constraints.
- Do not mark a stale-route trigger handled only inside records; the user-facing response must show the reminder or confirmation basis.
- Do not claim alignment, stale-constraint resolution, or audit readiness without reading the relevant current records.

## Recording Level

Use the lightest level that protects alignment:

- **None**: tiny, reversible, mechanical tasks.
- **Light**: short semantic tasks; keep the semantic frame in conversation unless the task continues.
- **Standard**: multi-step implementation/design work; create the standard record directory.
- **Deep**: high-impact, ambiguous, long-running, or user-facing work; use full records and audits at major checkpoints.
