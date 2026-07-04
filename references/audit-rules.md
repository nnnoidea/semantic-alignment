# Audit Rules

Load this reference when the user requests/accepts an audit, when recommending an audit, before final delivery with drift signals, or when a constraint/recheck trigger may reopen a prior route.

## Audit Lenses

Use three lenses:

- **Internal user audit**: user goals, global semantics, and local semantics are mutually consistent.
- **User-to-realization audit**: realization semantics are grounded in user semantics, reasonable additions, risky, or divergent.
- **Realization-to-artifact audit**: the real artifact matches realization semantics and still serves user semantics.

Full audits are user-initiated or user-accepted. The agent may recommend an audit, but should not silently run a full audit unless the user asks, accepts, or a material contradiction/risk appears at a natural checkpoint.

## Audit Recommendation Triggers

Recommend an audit when:

- many files, screens, components, sections, or public-facing behaviors changed
- a core artifact changed: architecture, data model, API contract, design system, navigation, workflow, public copy, build/deploy flow, or skill instructions
- several ledger entries or realization changes accumulated since the last audit
- any artifact check is `partial` or `fail`
- any realization semantic is `risky`, or multiple active realization semantics are `added`
- current work touches a user non-negotiable or review focus item
- a constraint recheck method passes or its evidence materially changes
- the user corrects direction, expresses doubt, asks whether the result still matches intent, or reopens a prior concern

Proactively warn without a full audit only for direct, material signals: user-semantic contradiction, active non-negotiable conflict, divergent realization semantic, material artifact failure, or clearly resolved blocking constraint.

## Constraint Recheck Rules

Constraint-driven changes must be checkable later. For meaningful constraint entries, preserve:

- blocked route
- accepted route
- evidence
- recheck method
- reopen trigger
- last checked, if known
- status: `active`, `unverified`, `resolved`, or `superseded`

Example recheck methods:

- command availability: run `<command> --version`
- dependency availability: inspect lockfile/package manifest or import/build
- asset availability: check expected file path
- API capability: check docs, schema, feature flag, or integration response
- permission: retry allowed operation or verify access state
- implementation feasibility: rerun failed test/build/prototype

Only remind that a constraint may be gone when the recheck method passes, evidence changed, or the user states the blocker is gone. Otherwise mark it `unverified` and suggest checking at the next audit.

## Reopen Decisions

For possible return-to-history decisions:

1. Verify the trigger if objective evidence exists.
2. Read the linked ledger entry before recommending a route change.
3. State which prior semantic/route may need reopening.
4. Ask whether to revisit the prior route when switching cost, scope, or product meaning is material.
5. Update the ledger only after the user accepts a baseline change.
6. Run `scripts/sync_triggers.py <record-dir>` after ledger trigger text or currentness changes. Edit trigger check metadata in `recheck-triggers.md` only for method/status/last-checked/notes.

If the user states in the same message that the trigger is true and asks to keep the old compromised route, do not treat the reminder as unnecessary. The response must still say that the old compromise is now stale or recheckable, name the better/prior route, and then explain whether the user's wording is being treated as explicit confirmation to keep the compromised route. If the wording is not explicit, pause and ask.

Never resolve, supersede, or remove a stale-route trigger only in records. A stale-route reminder is successful only when it is visible in the user-facing response or the user has already explicitly acknowledged it.

A recheck trigger should name the condition that makes the old semantic change questionable. Do not use recheck triggers to store open tasks, recommendations, or the action to perform after the trigger fires.

## Repeated Audits

Keep `audits.md` as a current summary plus recent material audit events, with the current summary at the top:

- latest alignment state
- open drift
- open contradictions
- reopen triggers
- current recommendations

Append material audits as events with date, trigger, inputs checked, findings, decision, follow-up status, and initiator. Mark findings `open`, `resolved`, `accepted`, or `superseded`. Do not delete normal history; remove or rewrite only duplicate, mistaken, sensitive, or noisy entries. When older resolved, accepted, or superseded events make routine reads noisy, move them to `archive/` and leave the current summary plus recent decision-relevant events in `audits.md`.

When an audit changes current user semantics, update `user-semantics.md`, add a ledger entry, and sync triggers. When it changes realization semantics, update `realization-semantics.md` and re-check affected artifacts.

## Realization Refresh Gate

Before a full audit, do not trust `realization-semantics.md` just because it exists. First inspect the real project/artifact, update stale intended-artifact semantics, add missing realization rows, mark obsolete rows `revised` or `rejected`, and refresh `artifact-checks.md` against the updated active realization semantics. If inspection shows no realization change is needed, record that as `unchanged` with concrete evidence.

Add this table to each full audit event before the coverage tables:

```markdown
#### Realization Refresh

| Refresh item | Status | Evidence | Notes |
| --- | --- | --- | --- |
| inspect-real-project | done | <files, commands, or artifacts inspected> | <short note> |
| update-realization-semantics | done/unchanged | <realization rows changed or evidence no change was needed> | <short note> |
| refresh-artifact-checks | done/unchanged | <artifact checks changed or evidence existing checks are current> | <short note> |
```

`scripts/check_audit_coverage.py <record-dir>` rejects full audit events that omit this table, omit a required refresh item, use any status other than `done` or `unchanged`, or leave evidence empty. Treat `unchanged` as a positive claim that the existing record was checked against the real project and remains current.

## Audit Output

Report concise decision-relevant findings:

- `Aligned`: user semantics, realization semantics, and checked artifact are consistent.
- `Added by agent`: details the agent introduced that the user did not explicitly request.
- `Potential drift`: semantics that may no longer serve the goal or global direction.
- `Contradictions`: direct conflicts between goal, global semantics, local semantics, realization semantics, or artifact.
- `Reopen triggers`: constraints or assumptions that should cause a prior semantic choice to be revisited.

Use `artifact-checks.md` as input to `audits.md`, not as a second audit. `artifact-checks.md` records concrete pass/partial/fail checks; `audits.md` synthesizes alignment/drift/contradiction.

## Exhaustive Coverage Gate

A full audit is incomplete unless the latest audit event first passes the realization refresh gate, then checks every current user semantic and every active realization semantic. Use `user-semantic-ledger.md` current `yes` rows, excluding delete operations, as the mechanically checkable user-semantic item set. Use active rows in the refreshed `realization-semantics.md` as the realization item set.

Add these two tables to each full audit event:

```markdown
#### User Semantic Coverage

| User semantic ID | Coverage | Evidence | Notes |
| --- | --- | --- | --- |
| U1 | satisfied/partial/unmet/conflict/unknown | <artifact checks, files, or missing evidence> | <short reason> |

#### Realization Semantic Coverage

| Realization ID | Grounding | User basis | Conflict | Notes |
| --- | --- | --- | --- | --- |
| R1 | direct/aligned-addition/risky-addition/conflict/unknown | <linked user semantic IDs or none> | yes/no/unknown | <short reason> |
```

Coverage meanings:

- `satisfied`: the artifact and realization evidence currently satisfy this user semantic.
- `partial`: some evidence satisfies it, but a material part is missing or unverified.
- `unmet`: current realization or artifact evidence does not satisfy it.
- `conflict`: realization semantics or artifacts directly contradict it.
- `unknown`: evidence is missing or was not checked; do not treat this as aligned.

Grounding meanings:

- `direct`: the realization is directly expressed by user semantics.
- `aligned-addition`: the user did not directly say it, but it serves linked user semantics.
- `risky-addition`: the user did not directly say it and it may affect meaning, scope, UX, architecture, or delivery criteria.
- `conflict`: the realization conflicts with current user semantics.
- `unknown`: the grounding cannot be established from the records.

Run `scripts/check_audit_coverage.py <record-dir>` before reporting a full audit as complete. The script checks only coverage shape: every current user semantic ID and active realization ID must appear exactly once with allowed status values. The agent still judges the correctness of the statuses and evidence.
