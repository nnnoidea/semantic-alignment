# Operational Workflow

Load this reference when starting non-trivial work, creating/updating semantic records, deciding which files to read, or changing ledger/recheck trigger data.

## Record Location And Files

For Standard or Deep tracking, create or update:

```text
.semantic-alignment/<project-slug>/
  index.md
  user-semantics.md
  user-semantic-ledger.md
  recheck-triggers.md
  realization-semantics.md
  artifact-checks.md
  audits.md
  structured/   # optional generated JSONL mirrors
  archive/      # optional old non-current realization rows or resolved audit events
```

Use the first writable project- or workspace-local metadata location, defaulting to `.semantic-alignment/<project-slug>/`. The record unit is the project. In a multi-project workspace, a workspace-level `.semantic-alignment/` directory is acceptable only when each project has its own distinct slug. Do not place records inside source directories, design exports, app assets, end-user docs, or release artifacts.

Choose `<project-slug>` by this order:

1. User-provided project slug or project name, when explicit.
2. Nearest Git repository root directory name for the files being changed.
3. Project manifest/package name, such as package metadata, pyproject/project name, app config, or equivalent local convention.
4. Current project directory name.

Normalize the chosen name to lowercase kebab-case: trim whitespace, replace spaces/underscores with hyphens, remove unsafe path characters, collapse repeated hyphens, and keep enough words to distinguish the project. If several projects are plausible in the same workspace, inspect existing `.semantic-alignment/*/index.md` files and nearby repository roots; if ambiguity remains, ask the user before creating or updating records.

Use scripts for deterministic structure:

```bash
python semantic-alignment/scripts/init_records.py .semantic-alignment/<project-slug>/ --title "<Project Name>"
python semantic-alignment/scripts/record_event.py .semantic-alignment/<project-slug>/ ledger --operation add --category process --before none --after "..." --reason clarification --source "..."
python semantic-alignment/scripts/sync_triggers.py .semantic-alignment/<project-slug>/
python semantic-alignment/scripts/validate_records.py .semantic-alignment/<project-slug>/
python semantic-alignment/scripts/lint_records.py .semantic-alignment/<project-slug>/
python semantic-alignment/scripts/check_audit_coverage.py .semantic-alignment/<project-slug>/
python semantic-alignment/scripts/export_structured.py .semantic-alignment/<project-slug>/
```

Read `semantic-record-template.md` when creating records, editing table shape, or needing exact schemas.

## Required Reads

### Startup checklist

1. Identify the project, derive or confirm `<project-slug>`, then locate the project record directory, usually `.semantic-alignment/<project-slug>/`.
2. Read `user-semantics.md`, `index.md`, and `recheck-triggers.md` when the directory exists and the frame is not fresh.
3. Choose the recording level.
4. Create Standard/Deep records with `init_records.py` when needed.
5. Load the reference required for the next action before making that decision or edit.

Before non-trivial project/design/artifact work, ensure the current semantic frame is loaded and fresh. A frame is fresh when `user-semantics.md`, `index.md` known unknowns, and `recheck-triggers.md` were read in the current context after the last known semantic-record edit.

Reuse a fresh frame. Reread when the session is new, context was compacted, record files may have changed, the user asks for an audit, or the user message appears to change project meaning.

- At project work start: read `user-semantics.md`, `index.md`, and `recheck-triggers.md` if they exist.
- Before deciding whether a user message changes semantics: compare against the loaded baseline and triggers; read `user-semantic-ledger.md` only when likely change/conflict/trigger needs authoritative history.
- Before planning meaningful work: ensure `user-semantics.md` is fresh; read relevant `realization-semantics.md` and current open items in `audits.md`.
- Before and during non-obvious agent choices: ensure `user-semantics.md` is fresh; read relevant `realization-semantics.md`; classify the choice; update `realization-semantics.md` before or while implementing the choice, not only during audit.
- Before changing current user semantics: read `user-semantics.md` and `user-semantic-ledger.md`; confirm material changes with the user.
- Before warning about a stale compromise: read `recheck-triggers.md`, then the linked ledger entry.
- Before final delivery: ensure `user-semantics.md` and `recheck-triggers.md` are fresh; read relevant realization semantics and artifact checks.

Do not claim alignment, stale-constraint resolution, or audit readiness without reading the relevant current records.

## Recording Levels

Choose the lightest level that protects alignment:

- **None**: tiny, reversible, mechanical tasks.
- **Light**: short semantic tasks; keep current baseline/realization in conversation unless the task continues.
- **Standard**: multi-step implementation/design work; create the standard record directory.
- **Deep**: high-impact, ambiguous, long-running, or user-facing work; use the full record and audits at major checkpoints.

Upgrade when scope grows, user intent changes, risky assumptions appear, constraints shape the route, or the artifact starts expressing product/design meaning.

## Semantic Change Procedure

When likely user-semantic change or conflict appears:

1. Do not silently rewrite `user-semantics.md`.
2. Briefly state the current semantic that appears to change or conflict.
3. Ask for confirmation when the change affects goal, product meaning, architecture, UX direction, public copy, delivery criteria, or a meaningful route choice.
4. After confirmation, update `user-semantic-ledger.md`, preferably with `scripts/record_event.py`.
5. Run `scripts/sync_triggers.py <record-dir>` if any recheck trigger changed.
6. Project the latest current state into `user-semantics.md`.
7. Update `realization-semantics.md` if agent intended artifact meaning changes.
8. After implementation, update `artifact-checks.md`.

## Implementation-Time Realization Updates

Keep `realization-semantics.md` as the current intended-artifact semantics while implementing. Update it when:

- the agent chooses behavior, UX, architecture, data shape, public copy, or workflow details not directly stated by the user
- a prior realization semantic changes because implementation reality differs from the plan
- an added detail becomes risky, divergent, rejected, or obsolete
- an implementation choice materially affects how a later audit should judge the artifact

Prefer updating or adding rows close to the implementation moment. Do not wait for a later audit to reconstruct intended semantics from the finished artifact. When a row is no longer current, mark it `revised` or `rejected` and keep it only if it still helps explain current state; otherwise move older non-current rows to `archive/` with enough context to preserve traceability.

When an active recheck trigger appears true:

1. Read `recheck-triggers.md`, then the linked `user-semantic-ledger.md` row.
2. State the prior compromise or route and the condition that appears to be true.
3. If switching route has material cost or changes product meaning, ask whether to reopen the prior route.
4. If the same user message explicitly says to keep the old compromised route despite the trigger, still include the reminder in the response before proceeding.
5. Treat that same-message instruction as confirmation only when it is unambiguous; otherwise pause for confirmation.
6. Do not mark the trigger handled, resolved, or superseded only through file edits. The user-facing response must make the reminder or confirmation basis visible.
7. After the user confirms the route choice, update the ledger, sync triggers, and project the current baseline.

## Recheck Trigger Projection

`user-semantic-ledger.md` is authoritative. `recheck-triggers.md` is generated for frequent reads.

Recheck triggers are active decision guards. They should be checked when current evidence may invalidate an earlier semantic decision, especially a constraint-driven compromise or a route chosen under uncertainty. They are useful only when the agent compares them with real signals; simply generating the file is not enough.

- Add or change trigger text in the ledger only when there is a condition that should cause this ledger entry to be rechecked.
- Write trigger text as an observable condition, not as the action to take after it fires.
- Run `scripts/sync_triggers.py <record-dir>` after trigger changes.
- The generated projection groups multiple ledger rows with the same trigger into one row whose `Ledger ID` cell is comma-separated.
- Run `scripts/validate_records.py <record-dir>` after substantial record edits.
- Run `scripts/lint_records.py <record-dir>` after substantial record edits or before delivery to catch likely semantic-quality issues.
- Do not add or remove trigger rows by hand. Edit trigger presence/text in the ledger, then run the sync script.
- It is acceptable to edit `Recheck method`, `Status`, `Last checked`, and `Notes` in `recheck-triggers.md`; the sync script preserves those fields for matching triggers.

### Trigger Evaluation Timing

Read and evaluate `recheck-triggers.md` at these points:

- startup/frame load for an existing record directory
- before meaningful planning or delivery when using a stored semantic frame
- after the user mentions changed constraints, tools, permissions, dependencies, assets, project direction, or acceptance criteria
- after implementation discovery or artifact checks reveal evidence related to a trigger
- before recommending an audit and during any user-requested full audit

When a trigger may be true:

1. Read the linked ledger row to recover the old semantic decision, reason, and accepted route.
2. Check the trigger using the row's `Recheck method` when possible.
3. State the old route and the now-observed condition in the user-facing response.
4. Ask before changing the baseline when reopening would alter scope, product meaning, architecture, UX, or delivery criteria.
5. Update ledger/current semantics only after the user accepts the change; update trigger metadata only after the reminder/decision is visible.

## Structured Mirrors

Keep `user-semantics.md` as Markdown. For machine-readable mirrors of selected non-user-entry records, run `scripts/export_structured.py <record-dir>` to generate `structured/realization-semantics.jsonl`, `structured/artifact-checks.jsonl`, and `structured/recheck-triggers.jsonl`.

These JSONL files are generated mirrors unless the project explicitly promotes them to source of truth. Do not ask the user to review them as the main semantic entry point.

## Operational Actions

- Capture user semantics when project/design/artifact meaning changes.
- Capture realization semantics before implementing non-obvious inferred details or tradeoffs.
- Check artifacts after implementation or before delivery.
- Suggest an audit at natural checkpoints, after substantial edits, after constraints change, before final delivery, or when the user questions direction.
- For full audits, inspect the real project first, update or explicitly confirm `realization-semantics.md`, refresh or explicitly confirm `artifact-checks.md`, write the realization refresh table and exhaustive coverage tables, then run `scripts/check_audit_coverage.py <record-dir>` before claiming the audit is complete.
- Reopen decisions when a constraint, missing tool, missing asset, deadline, or uncertainty that caused a compromise is resolved.
- Escalate to the user when user semantics conflict, realization semantics are risky/divergent, the artifact fails a material check, or the best aligned path has high switching cost.

## History And Hygiene

Keep `user-semantics.md` short and current. Keep ledger history traceable, but compress low-value repetition. Preserve major turning points, user corrections, superseded semantics, and constraint-driven compromises. Keep `realization-semantics.md` focused on active current semantics plus only recent useful non-current rows. Keep `audits.md` focused on current summary and recent material audit events. Archive old non-current realization rows and old resolved/accepted/superseded audit events under `archive/` when records become hard to scan.

Commit semantic records only when the team wants durable design rationale or project memory. Do not commit private conversation, speculative internal reasoning, credentials, unreleased strategy, verbose internal rationale, installers, caches, or local tool state.
