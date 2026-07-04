# Semantic Record Template

Use this directory layout for `.semantic-alignment/<project-slug>/` or another writable project- or workspace-local semantic metadata directory configured by the user or host project. The slug identifies the project, not an individual work item. Derive it from an explicit user project name/slug, the nearest repository root, a project manifest/package name, or the project directory name, then normalize it to lowercase kebab-case.

```text
.semantic-alignment/<project-slug>/
  index.md
  user-semantics.md
  user-semantic-ledger.md
  recheck-triggers.md
  realization-semantics.md
  artifact-checks.md
  audits.md
  archive/                      # optional old non-current realization rows or resolved audit events
  structured/                    # optional generated mirrors
    realization-semantics.jsonl
    artifact-checks.jsonl
    recheck-triggers.jsonl
```

Keep this directory out of product/source/design artifact folders. Decide separately whether to commit it to version control; it is process metadata, not the product itself.

Create the directory with fixed file skeletons:

```bash
python semantic-alignment/scripts/init_records.py .semantic-alignment/<project-slug>/ --title "<Project Name>"
```

After substantial edits, validate the directory with:

```bash
python semantic-alignment/scripts/validate_records.py .semantic-alignment/<project-slug>/
```

Append standard table rows with:

```bash
python semantic-alignment/scripts/record_event.py .semantic-alignment/<project-slug>/ ledger --operation add --category process --before none --after "<semantics>" --reason clarification --source "<source>"
python semantic-alignment/scripts/record_event.py .semantic-alignment/<project-slug>/ realization --semantics "<intended artifact meaning>" --scope implementation --relation grounded --linked-user-semantics U1 --rationale "<why>"
python semantic-alignment/scripts/record_event.py .semantic-alignment/<project-slug>/ check --artifact "<file>" --checked-against R1 --result pass --note "<concrete note>"
```

After substantial edits or before delivery, lint semantic-quality risks:

```bash
python semantic-alignment/scripts/lint_records.py .semantic-alignment/<project-slug>/
```

Before reporting a full audit as complete, check exhaustive coverage:

```bash
python semantic-alignment/scripts/check_audit_coverage.py .semantic-alignment/<project-slug>/
```

After adding, removing, or changing ledger recheck triggers, regenerate the compact trigger projection:

```bash
python semantic-alignment/scripts/sync_triggers.py .semantic-alignment/<project-slug>/
```

After substantial edits to realization semantics, artifact checks, or recheck triggers, generate structured mirrors:

```bash
python semantic-alignment/scripts/export_structured.py .semantic-alignment/<project-slug>/
```

## index.md

```markdown
# <Project Name>

## Current Semantic Frame

### Goal

<The user's intended outcome.>

### Global Semantics

- <Overall project, design, architecture, or product meaning.>

### Local Semantics

- <Specific meanings for the current component, file, feature, interaction, or implementation.>

### Known Unknowns

- <Open semantic gaps that the agent must not silently treat as facts.>
```

## user-semantics.md

This is the user's review entry point and current user-semantic baseline. Write it for a human user first, not as an internal database. Only record active user-originated semantics here. Do not add agent rationale or detailed history.

```markdown
# User Semantics

## Goal

<Plain-language statement of what the user wants.>

## Global Semantics

- <User-originated project/design meaning.>

## Local Semantics

- <User-originated local requirements or preferences.>

## User Review Focus

- <Points the user should verify or correct.>
```

## user-semantic-ledger.md

Record user semantic changes here. This is not a chat log. Every entry should state whether a user semantic was added, updated, or deleted, and why.

Use `Recheck trigger` as the action hook for future route review. It must be an observable condition that means "recheck this ledger entry"; it must not be an open task, recommendation, or action. Keep `recheck-triggers.md` synchronized with `scripts/sync_triggers.py` as the compact current projection for frequent reading; the ledger remains the authoritative history.

```markdown
# User Semantic Ledger

## Categories

- `goal`: intended outcome and success definition
- `principle`: non-negotiables, quality bars, values
- `context`: audience, environment, domain, workflow situation
- `global-design`: overall product/design/project meaning
- `local-design`: component, screen, section, behavior, interaction, detail
- `system`: architecture, data model, API, integration, operations
- `content`: public copy, naming, documentation tone, message
- `process`: semantic-alignment workflow rules for this project/skill
- `constraint`: user-recognized constraint or assumption
- `review`: review criteria, audit expectations, acceptance checks

## Ledger

| ID | Date | Operation | Category | Before | After | Reason | Source | Current? | Recheck trigger |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U1 | YYYY-MM-DD | add/update/delete | goal/principle/context/global-design/local-design/system/content/process/constraint/review | <old semantics or none> | <new semantics or none> | clarification/correction/optimization/constraint/implementation-discovery/agent-inference/scope-control/preference-change/deletion/unknown | <quote or close paraphrase> | yes/no | <when to revisit or none> |
```

## recheck-triggers.md

This is a generated compact current projection of active recheck triggers from `user-semantic-ledger.md`. Read this file often instead of scanning the full ledger every time. Do not treat it as independent history. When trigger presence or text changes, update the ledger and run `scripts/sync_triggers.py`; when only check metadata changes, edit `Recheck method`, `Status`, `Last checked`, or `Notes` here.

Rows with the same trigger condition are grouped. In that case, `Ledger ID` is a comma-separated list such as `U3,U4`.

Do not add or remove rows by hand. Edit trigger presence or text in `user-semantic-ledger.md`, then run `scripts/sync_triggers.py`. You may edit `Recheck method`, `Status`, `Last checked`, and `Notes`; the sync script preserves those fields when the trigger still matches.

```markdown
# Recheck Triggers

This file is generated from current rows in `user-semantic-ledger.md`. Do not add or remove trigger rows by hand; edit trigger presence/text in the ledger and run `scripts/sync_triggers.py`. You may edit `Recheck method`, `Status`, `Last checked`, and `Notes`; the sync script preserves those fields for matching triggers.

| ID | Ledger ID | Trigger | Recheck method | Status | Last checked | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | U1 | <condition that may require revisiting the current route> | <how to check it> | active/unverified/resolved/superseded | YYYY-MM-DD or never | <short note preserved by sync script> |
```

## realization-semantics.md

Record current realization semantics here: intended artifact semantics after agent interpretation, gap filling, and implementation/design choices. Every row should link back to user semantics when possible.

Update this file while implementing non-obvious choices, not only during audits. Keep it focused on active current semantics. Use `revised` or `rejected` for recent non-current rows only when they clarify current state; archive older non-current rows under `archive/` when routine reads become noisy.

```markdown
# Realization Semantics

## Realization Semantics

| ID | Realization semantics | Scope | Relation to user semantics | Linked user semantics | Rationale | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R1 | <meaning the agent added or inferred> | global/local/implementation | grounded/added/risky/divergent | U1 | <why the agent believed this> | active/rejected/revised |
```

## artifact-checks.md

Record artifact checks here. This is not a separate semantic layer, not a duplicate of the artifact, and not the audit conclusion. Keep it as a mechanical check log from comparing the real code, design, document, UI, or skill against `realization-semantics.md`.

```markdown
# Artifact Checks

## Artifact Checks

| ID | Artifact | Checked against | Result | Concrete note |
| --- | --- | --- | --- | --- |
| K1 | <file/component/output> | R1 | pass/partial/fail | <specific mismatch or "none"> |
```

## audits.md

Record the current audit summary and recent material audit events here. Use artifact checks as input; do not repeat the whole check log. Archive older resolved, accepted, or superseded audit events under `archive/` when the file becomes hard to scan.

```markdown
# Audits

## Current Audit Summary

- Overall status: aligned/potential-drift/contradiction
- Open drift:
- Open contradictions:
- Reopen triggers:
- Current recommendations:

## Audit Events

### YYYY-MM-DD - <trigger>

- Trigger:
- Inputs checked: user semantics, user semantic ledger, realization semantics, artifact checks
- Findings:
- Decision:
- Follow-up status: open/resolved/accepted/superseded
- Initiated by: user/requested-by-agent/narrow-warning

#### Internal User Audit

- Aligned:
- Potential drift:
- Contradictions:

#### User-To-Realization Audit

- Grounded:
- Added by agent:
- Risky:
- Divergent:

#### Realization Refresh

| Refresh item | Status | Evidence | Notes |
| --- | --- | --- | --- |
| inspect-real-project | done | <files, commands, or artifacts inspected> | <short note> |
| update-realization-semantics | done/unchanged | <realization rows changed or evidence no change was needed> | <short note> |
| refresh-artifact-checks | done/unchanged | <artifact checks changed or evidence existing checks are current> | <short note> |

#### User Semantic Coverage

| User semantic ID | Coverage | Evidence | Notes |
| --- | --- | --- | --- |
| U1 | satisfied/partial/unmet/conflict/unknown | <artifact checks, files, or missing evidence> | <short reason> |

#### Realization Semantic Coverage

| Realization ID | Grounding | User basis | Conflict | Notes |
| --- | --- | --- | --- | --- |
| R1 | direct/aligned-addition/risky-addition/conflict/unknown | <linked user semantic IDs or none> | yes/no/unknown | <short reason> |

#### Realization-To-Artifact Audit

- Aligned:
- Potential drift:
- Contradictions:
```

If evidence is missing, mark it as missing. Do not invent user semantics to make the audit look complete.

Keep `user-semantics.md` as Markdown. Other records may later move to YAML, JSON, or JSONL if a project needs stronger parsing; when doing so, update the generator and validator scripts together.

`realization-semantics.md` and `audits.md` are working records, not append-only history stores. Preserve useful history by status markers or archive files, but keep the main files readable enough for startup reads and audit gates.

For now, `structured/*.jsonl` files are generated machine-readable mirrors for selected non-user-entry records, not the user review entry point.
