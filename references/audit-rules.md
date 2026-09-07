# Audit Rules

Load this reference before an incremental or full audit, when evaluating invalidation, or when a compromise may need reopening.

## Audit Objective

An audit compares complete current user semantics with implementation semantics derived from the real artifact. It answers:

- what user semantics the artifact satisfies, partially satisfies, omits, or conflicts with
- what behavior the artifact contains that the user did not explicitly request
- whether prior audit conclusions remain valid
- whether an active compromise should be revisited

Do not audit plans against plans. Inspect the code, design, document, UI, configuration, tests, generated output, or other actual deliverable.

Resolve the artifact through the workspace index before auditing. Audit state belongs only to the resolved project's `<project-root>/.semantic-alignment/`; never aggregate or copy per-project coverage into the workspace index. Direct related semantics are also project-local.

## Audit Validity

A cached coverage result is valid only when:

```text
same user semantic revision
+ same direct related-semantic set and revisions
+ same evidence scope
+ same evidence file-state versions
+ no unreviewed artifact changes that could alter the mapping
```

The first three conditions allow direct reuse. The artifact snapshot supplies the fourth: every changed path must be inspected for impact on existing semantics and for unrequested implementation behavior before a new trusted snapshot is finalized.

Never infer validity from elapsed time, file names alone, or the fact that user semantics did not change.

File-state versions use type, size, modification time, and mode. They intentionally avoid content hashing and Git object IDs. Audit-rule or semantic-model document edits do not automatically invalidate existing conclusions; change user semantics explicitly when the accepted design meaning changes.

## Incremental Audit

Incremental audit is the default after a trusted baseline exists.

1. Run `audit.py plan`.
2. Reaudit every missing or stale user semantic, loading its direct `related` semantics as context.
3. Inspect every added, modified, and deleted artifact path.
4. Record each completed semantic conclusion immediately through `audit.py record-coverage`; this is the durable checkpoint for context recovery.
5. Add, revise, accept, or resolve implementation differences.
6. Evaluate active compromises related to the changed scope or new evidence.
7. Finalize the audit only after every reported artifact change was reviewed.

Unchanged coverage remains reusable even when unrelated semantics are added or changed. Do not rewrite it merely to produce a fresh timestamp.

## Full Audit

A full audit is required when:

- no trusted artifact baseline exists
- v1 records were migrated
- the configured artifact scope changed and prior coverage cannot be related safely
- evidence mappings are missing or known to be incomplete

A full audit is normally preferable when the user requests it, audit rules invalidate all prior judgments, or a structural change makes existing evidence mappings unreliable. A goal or global semantic change does not by itself invalidate unrelated semantics.

Full does not mean writing an execution log. It means covering every current user semantic and inspecting the complete configured artifact scope for additions.

## Two-Direction Coverage

### User semantics to artifact (`U → A`)

For every missing or invalidated user semantic, inspect that semantic and its direct related semantics, then record:

- status: `satisfied`, `partial`, `unmet`, `conflict`, or `unknown`
- implementation semantics observed in the artifact
- source and relationship classification
- complete evidence scope
- concise reasoning

### Artifact changes to implementation semantics (`ΔA → I`)

Inspect all changed paths even when no user semantic currently references them. Determine whether they introduce, enhance, remove, substitute, narrow, or contradict behavior.

This pass is mandatory. Without it, tests, checksums, retries, telemetry, public copy, permission changes, or other agent additions can remain invisible.

## Evidence Scope

Use the narrowest scope that completely proves the conclusion:

- implementation file plus relevant configuration
- component directory when behavior is distributed
- generated artifact when source alone does not prove the output
- tests only as supporting evidence, not as proof that production behavior exists

The default whole-project snapshot uses Git tracked and non-ignored files when Git is available. Pass explicit `--scope` values for ignored generated outputs or other artifact directories that still carry product meaning; explicit scopes are scanned from the filesystem.

Overly broad evidence causes needless invalidation. Overly narrow evidence creates unsafe cache hits. If the complete scope cannot be established, mark coverage `unknown` or perform a full audit.

## Difference Judgment

Report decision-relevant differences, including beneficial additions. Do not flood the report with syntax, private helper names, command history, or mechanically equivalent refactors.

Impact guidance:

- `low`: does not change user-visible behavior or meaningful operating constraints
- `medium`: changes behavior, maintenance, performance, failure handling, or review expectations
- `high`: changes goals, architecture, public behavior, security/privacy, irreversible data handling, or a non-negotiable

Direct conflicts and high-impact unrequested additions should be surfaced immediately. Lower-impact differences may be delivered together at the audit checkpoint.

## Compromise Recheck

A compromise is relevant when the current task touches its affected semantics/scope or evidence suggests its recheck condition may be true.

If relevant:

1. verify the condition when possible
2. state the original target and accepted gap
3. show the new evidence
4. ask before a material route change

Do not repeatedly remind the user when neither the affected scope nor the recheck condition is relevant.

## Completion Gate

An audit may be finalized when:

- every current user semantic has current coverage
- no cached difference has stale evidence
- every changed artifact path has been inspected
- affected compromises were evaluated
- unknowns and unresolved differences are reported rather than hidden

`scripts/audit.py finalize` mechanically enforces the first three structural conditions and records the trusted artifact snapshot. Semantic correctness remains the auditing agent's responsibility.
