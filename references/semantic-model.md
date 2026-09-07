# Semantic Model

Load this reference when deciding what belongs in the durable user baseline, what must be captured as a compromise, or how artifact-derived implementation behavior relates to user intent.

## Four Objects

### User semantics (`U`)

The complete current, durable product/system design meaning accepted from the user:

- goals and success criteria
- principles and non-negotiables
- context and audience
- global and local design meaning
- system behavior, architecture, operations, and constraints
- public content meaning
- process and review expectations

Record semantics, not utterances. Status requests, command details, and ordinary coordination are not user semantics unless they change what should be built, preserved, checked, or revisited.

Experiment parameters, run status, intermediate research conclusions, and ordinary document-writing choices are not independently managed semantic projects. If the user accepts an experiment conclusion as a lasting product decision, record only that durable decision in the owning product project. Treat a document as a semantic artifact only when it is the canonical specification or contract for later implementation.

Each semantic has a stable ID and one current revision. Older revisions are retired history: they remain available for traceability but are excluded from normal loading and auditing. Update the existing ID when its meaning changes.

A semantic may list a small set of directly `related` semantic IDs. The relation is untyped, symmetric, limited to one level, and local to one project record set; the recording tool maintains both ends. It exists only to provide nearby design context during audit, not as a dependency graph. If a new statement changes an existing semantic's meaning, update or retire that semantic instead of encoding a complex relationship. If several projects share a genuine higher-level semantic, record it in a separate common-parent project instead of creating cross-project links.

### Artifact (`A`)

The real code, design, document, UI, configuration, tests, generated output, or other deliverable. It is the source of truth for what was actually implemented.

Do not create or maintain a separate hand-written intended-artifact layer. Plans and prior agent statements may guide inspection, but they are not evidence that the artifact implements something.

### Implementation semantics (`I`)

Behavior and meaning derived by inspecting the artifact. Implementation semantics are audit findings, not implementation-time promises.

For each finding, classify two independent dimensions:

- source: `user-explicit`, `user-inferred`, `agent-added`, `constraint-driven`, `unknown`
- relationship: `implements`, `extends`, `narrows`, `substitutes`, `conflicts`, `none`, `unknown`

`user-inferred` means the artifact fills a genuine gap in a way strongly implied by the user's design. `agent-added` means the artifact contains a choice the user did not request, even if it is beneficial. `constraint-driven` means the implementation reflects a recorded compromise.

### Compromise (`C`)

A durable decision to accept a gap between a preferred target and the actual route because of a constraint or uncertainty. A compromise must contain:

- original target
- actual choice
- explicit gap
- reason
- evidence
- affected user semantics
- affected scope
- observable recheck condition
- recheck method
- status and last checked value

Code cannot reliably reveal why a compromise was accepted, so capture it when the decision occurs. Ordinary additions, optimizations, and implementation details are not compromises unless they abandon or defer a meaningful target.

## Differences (`D`)

Differences are the user-facing comparison between current user semantics and artifact-derived implementation semantics.

- `added`: behavior exists without an explicit user requirement
- `enhanced`: the implementation goes beyond a requested behavior while preserving it
- `omitted`: requested behavior is absent
- `substituted`: a different behavior or route replaces the requested one
- `narrowed`: only a smaller part of the requested behavior is implemented
- `conflict`: implementation directly contradicts user semantics
- `artifact-drift`: artifact behavior is internally inconsistent or no longer matches previously audited evidence

Reasonable quality improvements remain differences. Tests, validation, retries, checksums, logging, or fallback behavior should be visible when the user did not request them.

Not every implementation detail is semantically relevant. Record a difference when it changes behavior, scope, risk, UX, architecture, delivery criteria, operational properties, or the user's judgment of whether the result is appropriate.

## Audit Coverage

Each current user semantic has one current coverage entry containing:

- the user semantic revision number
- its direct related-semantic IDs and revision numbers
- coverage status: `satisfied`, `partial`, `unmet`, `conflict`, or `unknown`
- assertion type: `capability`, `obligation`, or `prohibition`
- artifact-derived implementation semantics
- source and relationship classifications
- concrete evidence paths and low-cost file-state versions
- counterexample-path review for every satisfied entry, including applicability and bypass details for obligations and prohibitions
- a concise note and audit time

The audit cache is not trusted merely because an entry exists. It is valid only while the semantic revision, direct related context, and every evidence file-state version still match. These versions use type, size, modification time, and mode; they do not hash content or use Git object IDs. Audit-rule document edits do not automatically invalidate prior results. Unrelated semantic changes do not invalidate them either.

Record each completed semantic conclusion immediately through the audit tool. The persisted per-semantic coverage is also the recovery point when a long audit is interrupted or conversation context is compacted; do not wait until the end of a large audit to save findings.

## Complete Discovery

Auditing only known user semantics is insufficient because it cannot discover unrequested additions. Every audit therefore has two directions:

1. `U → A`: check missing or invalidated user-semantic coverage.
2. `ΔA → I`: inspect every added, modified, or deleted artifact path for new implementation semantics and differences.

The artifact snapshot is the completeness guard for the second direction.

Artifact-to-semantics discovery must follow control points, not only ledger links. A mode selector, router, exception, fallback, or early return may affect several user semantics at once. `related` helps load nearby design context but never limits which semantics an implementation branch can violate.

## Project Ownership

Every project owns its authoritative semantics, compromises, and audit state under `<project-root>/.semantic-alignment/`. A workspace-level `projects.json` is only a rebuildable routing index from project identity to relative location. It is not another semantic layer and must never duplicate project facts.

An artifact path must resolve to exactly one active project. Duplicate IDs, duplicate roots, stale paths, and overlapping project roots are errors because silently choosing one record set would make semantic ownership ambiguous.
