---
name: semantic-alignment
description: Preserve durable product and system design semantics, derive implementation semantics by auditing real artifacts, report differences, and retain compromises. Use when work creates or changes long-lived behavior, architecture, interfaces, UX, operational invariants, or acceptance criteria. Do not use for routine experiments, research runs, transient analysis, or ordinary document writing unless the user explicitly requests semantic tracking or the artifact is itself a durable implementation contract.
---

# Semantic Alignment

Keep the artifact faithful to the user's actual design meaning without making the agent maintain a second hand-written implementation specification.

The durable model is:

- complete current user semantics with small direct `related` sets
- retired user-semantic history that is excluded from current audits
- explicit compromises that code cannot explain
- implementation semantics derived from the real artifact by audit
- reusable audit results that are invalidated by semantic or artifact file-state changes
- a concise user-facing difference report

Do not treat implementation plans, code comments, or prior agent claims as implementation truth. Inspect the artifact.

## Activation Boundary

Use this skill when the work creates or changes meaning that future implementation must continue to preserve, including durable product behavior, system architecture, interfaces, UX rules, operational invariants, or acceptance criteria.

Do not activate it merely because work is non-trivial. By default, do not create semantic records for:

- individual experiments, training/evaluation runs, parameter sweeps, or transient research state
- routine analysis, benchmark execution, or result reporting
- ordinary documents, presentations, summaries, copy edits, or other writing tasks
- temporary scripts, generated outputs, or disposable prototypes

An experiment result becomes relevant only when the user accepts it as a durable product or system decision; record that accepted decision in the owning product project, not the experiment run. A document is in scope only when it is itself the canonical design specification or contract that governs later implementation. Explicit user requests for semantic tracking always take precedence.

## Startup

1. Identify the workspace root and the artifact path being changed.
2. Resolve the artifact path through the saved workspace index:

```bash
python semantic-alignment/scripts/workspace.py resolve <artifact-path> \
  --workspace-root <workspace-root>
```

3. The resolved record directory must be `<project-root>/.semantic-alignment/`. Project-local records are authoritative; the workspace index is routing metadata only. If no project is registered, initialize it with `workspace.py init` instead of inventing a record path.
4. If v1 files such as `realization-semantics.md` exist, read `references/operational-workflow.md` and run a dry-run migration before changing records. Use `migrate_v1.py --into` when old workspace-level or multi-record layouts must be consolidated into the project-local v2 record set.
5. For an existing v2 record set, read:
   - `user-semantics.md`
   - active entries in `compromises.jsonl`
   - `alignment-report.md`
6. Choose the lightest recording level that protects alignment.
7. Before meaningful artifact work, run an incremental audit plan when a trusted baseline exists:

```bash
python semantic-alignment/scripts/audit.py <project-root>/.semantic-alignment/ plan \
  --artifact-root <project-root>
```

## Core Workflow

### 1. Maintain user semantics

Record durable product/design meaning, not every utterance. User semantics include goals, principles, context, global and local design, system behavior, content, process constraints, and review criteria.

Use stable semantic IDs. Keep only the latest non-deleted revision in the active baseline; older revisions are retired history and are not loaded into ordinary audits. An update invalidates that semantic automatically.

Record every semantic mutation through `scripts/record_event.py`. Do not hand-edit the ledger or generated views. `related` is an optional, untyped set of directly related semantic IDs. The tool keeps both ends synchronized; read only one level and do not construct a typed dependency graph or transitive closure.

`related` never crosses project record sets. If several projects share one genuine product/design semantic, place that semantic in a separately registered project at their smallest meaningful common parent instead of linking ledgers or copying the semantic into the workspace index.

```bash
python semantic-alignment/scripts/record_event.py <record-dir> semantic \
  --operation add --category goal --text "..." --related U2,U3 \
  --reason clarification --source "..."

python semantic-alignment/scripts/record_event.py <record-dir> semantic \
  --operation update --id U1 --category goal --text "..." --reason correction --source "..."
```

Do not silently change the user baseline when product meaning, architecture, UX, public behavior, scope, or acceptance criteria materially change. Confirm the change first.

### 2. Record compromises immediately

A compromise is a chosen departure from a preferred target because of a constraint, uncertainty, cost, permission, dependency, asset, deadline, or feasibility limit. Code can show the resulting choice but usually cannot recover why it was accepted or when it should be revisited.

Record a material compromise when the decision is made. Include the original target, actual choice, gap, reason, evidence, affected semantics, scope, observable recheck condition, and recheck method.

Do not use compromises for ordinary implementation details, open tasks, speculative risks, or harmless agent additions.

### 3. Derive implementation semantics by auditing artifacts

Do not continuously maintain `realization-semantics.md`. Semantic audit starts from a current user semantic, loads its direct `related` semantics as a small context, and then inspects the real code, design, document, UI, configuration, tests, or generated output. This is different from a general code review: artifact inspection exists to prove or disprove user meaning.

Every audit must do both:

- check affected user semantics against artifact evidence
- inspect every new or changed artifact scope for implementation behavior the user did not request

This second pass prevents an audit from missing additions merely because no existing user semantic points to them.

### 4. Reuse only valid audit results

An audit result is reusable only while all of these remain unchanged:

- the referenced user semantic revision
- its direct related-semantic set and those semantic revisions
- its recorded evidence paths and low-cost file-state versions
- the artifact scope baseline used to discover additions

Evidence versions use file type, size, modification time, and mode. Do not hash artifact contents or use Git object IDs. Audit-rule document edits do not invalidate prior results automatically.

Run `audit.py plan` before auditing. Recheck only missing or stale semantics, using each target's direct related semantics as context, plus added, modified, and deleted artifact paths. Unrelated semantic changes never invalidate a completed result. A full audit is required for the first trusted baseline or when the artifact scope/mapping is unreliable.

Record each semantic conclusion through the tool immediately after auditing that semantic and its small related context. Do not wait for a long audit to finish: persisted coverage is the recovery checkpoint after context compaction. Never hand-edit `audit-state.json`. Finalize only after reviewing every changed path:

```bash
python semantic-alignment/scripts/audit.py <record-dir> record-coverage \
  --artifact-root <project-root> --semantic-id U1 --status satisfied \
  --source user-explicit --relation implements \
  --implementation "..." --evidence path/to/file --notes "..."

python semantic-alignment/scripts/audit.py <record-dir> record-difference \
  --artifact-root <project-root> --type added --source agent-added \
  --relation extends \
  --implementation "..." \
  --user-semantics U1 --evidence path/to/file --impact low --notes "..."

python semantic-alignment/scripts/audit.py <record-dir> finalize \
  --artifact-root <project-root> --mode incremental --confirm-all-changes-reviewed
```

Pass `--relevant-compromise C1` for compromises relevant to the audited scope. Other active compromises remain stored but are not shown as reminders.

### 5. Show users differences, not internal bookkeeping

`alignment-report.md` is generated from current audit state and active compromises. Default user-facing delivery should summarize:

- implementation additions or enhancements not explicitly requested
- omissions, narrowing, substitutions, conflicts, or artifact drift
- compromises whose recheck condition is relevant now

Provide the complete user design semantics when the user asks for them, when establishing a baseline, or when a material ambiguity requires review.

## Difference Model

Classify implementation relationships independently from their source:

- source: `user-explicit`, `user-inferred`, `agent-added`, `constraint-driven`
- relationship: `implements`, `extends`, `narrows`, `substitutes`, `conflicts`
- reported difference: `added`, `enhanced`, `omitted`, `substituted`, `narrowed`, `conflict`, `artifact-drift`

A reasonable addition is still a difference. For example, adding tests or checksum verification without a user request should be reported even when it improves quality.

## Recheck Compromises

Evaluate active compromises when:

- related user semantics or artifact paths are being changed
- new evidence matches a recorded recheck condition
- a relevant tool, permission, dependency, API, asset, deadline, or constraint changes
- an audit or delivery review reaches the affected scope

When a condition becomes true, tell the user the original target, accepted gap, and new evidence before continuing with the compromised route or changing it. Do not resolve a compromise only inside records.

## Record Set

Standard and Deep tracking keep the authoritative record set inside the project:

```text
<project-root>/.semantic-alignment/
  project.json
  user-semantics.md
  semantic-ledger.jsonl
  compromises.jsonl
  audit-state.json
  alignment-report.md
```

- `project.json`: tool-written stable project identity and local layout
- `user-semantics.md`: generated complete current user baseline
- `semantic-ledger.jsonl`: tool-written stable-ID revisions; only latest non-deleted revisions are active
- `compromises.jsonl`: append-only compromise revisions
- `audit-state.json`: tool-written per-semantic implementation findings, evidence, differences, and artifact snapshot
- `alignment-report.md`: generated concise user-facing differences and active compromises

Initialize and validate with:

```bash
python semantic-alignment/scripts/workspace.py init <project-root> \
  --workspace-root <workspace-root> --project-id <stable-project-id>
python semantic-alignment/scripts/validate_records.py <project-root>/.semantic-alignment/
```

The workspace keeps one rebuildable routing index:

```text
<workspace-root>/.semantic-alignment/projects.json
```

It contains only stable project IDs and workspace-relative project/record paths. It must not contain user semantics, compromises, differences, coverage, or audit state. Use `workspace.py list`, `resolve`, `check`, `archive-project`, and `rebuild-index`; do not hand-edit the index or project manifests. `archive-project` removes a retired project from the active index while preserving its complete record set under the project-local `.semantic-alignment-archive/`. Normal startup and default `check` read the saved index without rescanning the whole workspace. Use `check --discover` or `rebuild-index` for explicit discovery; they reject stale paths, duplicate IDs, duplicate roots, or overlapping active project roots rather than guessing ownership.

Keep project records outside product artifacts. They live with the project and may be versioned with it; `.semantic-alignment` remains excluded from artifact snapshots to avoid self-invalidating audits.

## Recording Levels

- **None**: tiny, reversible, mechanical work, routine experiments, transient analysis, and ordinary writing with no durable product/system semantic effect.
- **Light**: bounded, low-risk work with a durable semantic effect; retain the frame in conversation and report visible differences.
- **Standard**: multi-step project work; persist the five-file record set and use incremental audits.
- **Deep**: high-impact, ambiguous, long-running, or public work; establish a full baseline and use broader evidence scopes.

## Reference Loading

- Read `references/semantic-model.md` when deciding what counts as user semantics, implementation semantics, a difference, or a compromise.
- Read `references/operational-workflow.md` when creating, updating, or migrating records.
- Read `references/audit-rules.md` before incremental/full audits or compromise rechecks.
- Read `references/semantic-record-template.md` when exact schemas or command examples are needed.

Do not claim current alignment when `audit.py plan` reports missing or stale coverage, stale differences, or unreviewed artifact changes.
