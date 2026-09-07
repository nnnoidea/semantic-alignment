# Operational Workflow

Load this reference when creating, updating, or migrating semantic records.

## Record Location

Keep each authoritative record set inside the project it describes:

```text
<project-root>/.semantic-alignment/
```

The workspace root contains only a rebuildable routing index:

```text
<workspace-root>/.semantic-alignment/projects.json
```

The index maps a stable project ID to workspace-relative project and record paths. It never stores or copies semantics, compromises, implementation findings, differences, or audit state. A project's local files are the sole source of truth and move with that project.

Create an indexed project record only for a durable product/system design scope. Do not create one for each experiment, research run, report, presentation, or ordinary document. When experimental evidence changes a lasting product decision, update the owning product project's semantics instead of registering the experiment as another semantic project.

Choose the stable project ID in this order:

1. explicit user-provided project name or ID
2. nearest repository root name
3. manifest/package project name
4. project directory name

Normalize to lowercase kebab-case. Ask when ambiguity would attach records to the wrong project. IDs must be unique within a workspace.

Do not create cross-project `related` links. A genuine semantic shared by several projects belongs to a separately registered project at their smallest meaningful common parent.

## Workspace Index

Initialize and register a project:

```bash
python semantic-alignment/scripts/workspace.py init <project-root> \
  --workspace-root <workspace-root> --project-id <stable-project-id>
```

Locate records for an artifact before loading or changing semantics:

```bash
python semantic-alignment/scripts/workspace.py resolve <artifact-path> \
  --workspace-root <workspace-root>
```

Manage the saved index only through the tool:

```bash
python semantic-alignment/scripts/workspace.py list --workspace-root <workspace-root>
python semantic-alignment/scripts/workspace.py check --workspace-root <workspace-root>
python semantic-alignment/scripts/workspace.py check --workspace-root <workspace-root> --discover
python semantic-alignment/scripts/workspace.py archive-project <project-id> --workspace-root <workspace-root>
python semantic-alignment/scripts/workspace.py rebuild-index --workspace-root <workspace-root>
```

Normal startup, `list`, `resolve`, `archive-project`, and default `check` use the saved index and do not scan the full workspace. `archive-project` moves the complete record set to `<project-root>/.semantic-alignment-archive/` before removing its active index entry. `check --discover` and `rebuild-index` explicitly discover project-local `project.json` manifests. They reject stale paths, duplicate project IDs, duplicate roots, and overlapping active project roots instead of choosing silently.

## V2 Project Record Set

```text
<project-root>/.semantic-alignment/
  project.json            # tool-written project identity and local layout
  user-semantics.md       # generated complete current baseline
  semantic-ledger.jsonl   # tool-written semantic revisions; retired history stays inactive
  compromises.jsonl       # authoritative append-only compromise revisions
  audit-state.json        # current incremental audit cache
  alignment-report.md     # generated user-facing differences
  archive/                # optional migrated or retired records
```

Only two sources require semantic authoring:

- accepted user semantic changes
- material compromises

Implementation semantics, audit coverage, low-cost evidence versions, and the user-facing difference report are produced by artifact audits and scripts.

Never hand-edit the semantic ledger, audit state, or generated Markdown views. Use the provided tools so IDs, revisions, related references, invalidation, locking, and projections stay consistent.

## Initialize

```bash
python semantic-alignment/scripts/workspace.py init <project-root> \
  --workspace-root <workspace-root> --project-id <stable-project-id>
```

The initializer writes the project-local record set and `project.json`, then updates the workspace index atomically under locks. It refuses conflicts and does not overwrite v1 records. Migrate existing records instead of silently replacing them.

## Load A Project

For an existing v2 project:

1. Run `workspace.py resolve` for the artifact path.
2. Read `user-semantics.md` from the resolved project-local record directory.
3. Read current active compromise revisions from `compromises.jsonl`.
4. Read `alignment-report.md`.
5. Run `audit.py plan` before meaningful implementation or delivery when artifact state may have changed.

Read the full ledgers only when changing a semantic, revising a compromise, resolving historical ambiguity, or auditing history.

## Record User Semantics

Add a stable semantic:

```bash
python semantic-alignment/scripts/record_event.py <record-dir> semantic \
  --operation add \
  --category global-design \
  --text "The product must preserve ..." \
  --related U1,U2 \
  --reason clarification \
  --source "User clarified ..."
```

Update the same semantic ID when its meaning changes:

```bash
python semantic-alignment/scripts/record_event.py <record-dir> semantic \
  --operation update --id U3 \
  --category global-design \
  --text "The revised meaning is ..." \
  --reason correction \
  --source "User corrected ..."
```

`--related` is an optional comma-separated set of current semantic IDs; use `--related none` to clear it. Relations are untyped and one level deep. The tool synchronizes both ends so agents never edit a second semantic manually.

Delete with `--operation delete --id U3`. The script appends a retired revision, regenerates `user-semantics.md`, and marks the latest audit stale. Retired revisions remain available for history but are excluded from current audits.

## Record Compromises

Record a compromise at the decision point, not during a later code audit:

```bash
python semantic-alignment/scripts/record_event.py <record-dir> compromise \
  --operation add \
  --original-target "Direct file export" \
  --actual-choice "Copy result to clipboard" \
  --gap "The user must create the file manually" \
  --reason "The runtime has no file-write permission" \
  --evidence "Write attempt was denied" \
  --scope "export workflow" \
  --affected-user-semantics U4 \
  --recheck-condition "File-write permission becomes available" \
  --recheck-method "Attempt a bounded write in the configured output directory"
```

Use `--operation update`, `resolve`, or `supersede` with the same compromise ID. Updates append revisions; they do not rewrite history.

When a recheck condition appears true:

1. read the latest compromise revision
2. verify the condition when objective evidence is available
3. tell the user the original target, current gap, and new evidence
4. ask before a material route change
5. update or resolve the compromise only after the decision is visible

## Incremental Audit Cycle

### Plan

```bash
python semantic-alignment/scripts/audit.py <record-dir> plan --artifact-root <project-root>
```

The plan reports:

- added, modified, and deleted artifact paths since the trusted snapshot
- current user semantics with missing audit coverage
- cached coverage invalidated by a semantic revision or evidence change
- each missing or stale semantic's direct related context
- implementation differences whose evidence changed
- whether a full audit is recommended

The default `.` scope uses Git tracked and non-ignored files when available. Repeat `--scope <path>` to audit ignored generated outputs or a narrower artifact subtree directly from the filesystem.

### Inspect

Inspect two sets:

1. every missing or stale user semantic, its direct related semantics, and its relevant artifact evidence
2. every changed artifact path, including paths not mapped to an existing user semantic

The first finds unmet user intent. The second finds agent additions and unexpected behavior. Unrelated semantic changes do not invalidate completed coverage.

### Record Coverage

```bash
python semantic-alignment/scripts/audit.py <record-dir> record-coverage \
  --artifact-root <project-root> \
  --semantic-id U3 \
  --status satisfied \
  --source user-explicit \
  --relation implements \
  --implementation "The artifact ..." \
  --evidence src/example.py \
  --notes "Concrete audit conclusion"
```

Evidence may be a file or directory. The script records a low-cost version from file type, size, modification time, and mode; it does not hash contents or use Git object IDs. Use the narrowest complete evidence scope; overly broad directories cause unnecessary invalidation, while incomplete scopes can incorrectly reuse stale conclusions.

Record each semantic as soon as it and its directly related context have been audited. Do not defer all writes until the end of a long audit: `record-coverage` is the durable checkpoint used to resume after interruption or context compaction.

### Record Differences

```bash
python semantic-alignment/scripts/audit.py <record-dir> record-difference \
  --artifact-root <project-root> \
  --type added \
  --source agent-added \
  --relation extends \
  --implementation "The artifact adds automatic retries" \
  --user-semantics U3 \
  --evidence src/example.py \
  --impact low \
  --notes "Not explicitly requested"
```

Use `user-semantics none` for an implementation addition with no direct user-semantic basis. Update a difference by supplying its existing `--id`; mark it accepted or resolved with `resolve-difference`.

### Finalize

Finalize only after inspecting every path listed by the plan:

```bash
python semantic-alignment/scripts/audit.py <record-dir> finalize \
  --artifact-root <project-root> \
  --mode incremental \
  --confirm-all-changes-reviewed
```

Add `--relevant-compromise C1` for each active compromise that was relevant to this audit. Finalization refuses missing or stale coverage and stale difference evidence. It stores the new artifact snapshot and regenerates `alignment-report.md`, showing only the compromises relevant to that audit while retaining all others internally.

## Migration

V1 records contain hand-maintained realization semantics and audit prose without reusable evidence scopes and file-state versions. Preview migration with:

```bash
python semantic-alignment/scripts/migrate_v1.py <record-dir>
```

Apply only after reviewing the plan:

```bash
python semantic-alignment/scripts/migrate_v1.py <record-dir> --apply
```

Migration archives v1 files, converts current user semantics, and conservatively preserves active recheck conditions as unverified compromises. It does not trust old audit conclusions as v2 cache entries; one baseline full audit is required.

When several legacy record directories belong to one project, initialize the project-local v2 record set and merge each source through the migration tool:

```bash
python semantic-alignment/scripts/migrate_v1.py <legacy-record-dir> \
  --into <project-root>/.semantic-alignment/ \
  --source-label <stable-source-label>

python semantic-alignment/scripts/migrate_v1.py <legacy-record-dir> \
  --into <project-root>/.semantic-alignment/ \
  --source-label <stable-source-label> --apply
```

The merge preserves exact existing semantics without duplication, assigns new stable `U<number>` IDs when legacy IDs conflict or use another format, converts recheck conditions to compromises, and archives then removes the legacy source. Use `--archive-only` only for a confirmed superseded pointer or mirror whose semantics are already represented by the canonical project record.

## Validation

```bash
python semantic-alignment/scripts/validate_records.py <record-dir>
```

Validation checks JSONL event sequences, controlled vocabulary, audit-state references, and generated projections. It verifies structure and cache shape, not the truth of an agent's semantic judgment.
