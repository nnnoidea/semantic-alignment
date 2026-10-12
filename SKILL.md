---
name: semantic-alignment
description: Maintain current Markdown design when a task establishes or changes durable product behavior, system contracts, or acceptance criteria, or explicitly requests semantic recording or auditing. Verify requirements and expose agent implementation choices. Do not auto-trigger for routine implementation under an unchanged design, bug fixes restoring it, internal refactors, tests, Git operations, temporary analysis, research, or ordinary writing.
---

# Semantic Alignment

Keep a readable current design and check real artifacts against it. Maintain meaning by product topic and behavioral chain, not by individual semantic records.

## Activation Boundary

Use this skill when the user establishes, changes, or corrects lasting product or system meaning: behavior users rely on, interfaces, architecture constraints, operating rules, or acceptance criteria. An explicit request to maintain semantic records or perform a semantic audit also activates it.

An existing semantic file, a substantial coding task, or an unspecified implementation detail alone is not a trigger. Routine implementation under an unchanged design, fixes restoring agreed behavior, internal refactors, tests, debugging, repository discovery, commits or pushes, installation, temporary scripts, experiments, research, summaries, and ordinary writing do not automatically activate it. A request to review code is not by itself a semantic audit.

If such work reveals a durable design decision, activate for that affected meaning only. Record accepted experimental conclusions in the owning product when they become lasting decisions. Relevant existing design remains applicable even when this skill is inactive; reading it does not require initiating semantic maintenance or an audit. Once activated, persist accepted meaning even for a small change and check the affected artifacts as described below.

## Records

Small projects can keep the current design in one SEMANTICS.md. For a large project, keep the same entry point and organize substantial topics as Markdown documents:

```text
<project-root>/SEMANTICS.md       project meaning, shared constraints, topic links
<project-root>/semantics/         topic documents, only when useful
```

Markdown is authoritative and directly editable. Do not maintain semantic IDs, revisions, relation registries, event ledgers, JSON indexes, generated projections, file-state snapshots, or standing coverage caches. Do not create semantic change history or load retired designs during ordinary work.

Reuse an existing canonical design document instead of duplicating it. Identify its exact path in SEMANTICS.md when the conventional filename is needed for discovery; keep each topic authoritative in one place. Existing repository ownership and documentation conventions take precedence.

## Shape

SEMANTICS.md carries project purpose, shared vocabulary, and cross-cutting constraints. For multiple files, add topic links with short scope descriptions, without duplicating their detailed requirements.

Group detailed design by product responsibilities and complete behavioral chains, not abstract categories or individual requirements. Split where distinct tasks need different substantial topics; impose no file count or size limit.

Use descriptive filenames, product terms, useful implementation names, and meaningful subheadings. Write connected prose with concrete triggers, outcomes, limits, and nearby exceptions. Ordinary physical line and paragraph breaks support search, bounded reads, and local edits. Avoid giant lines or distant qualifications; use lists for parallel rules.

Give each rule one authoritative home. Link precisely where a real prerequisite crosses topics, without a broad relation registry. Keep enough local context to understand ordinary behavior without loading unrelated chapters.

Distinguish accepted intent from implementation. Keep unmet requirements in their authoritative topic with known gaps; do not weaken them to match code or move them to optional alternatives. Keep uncertainty visible; agent proposals do not silently become accepted design.

Put relevant alternatives in a marked "Not adopted" section of the owning topic; a substantial separate document is optional. Explain the current choice, potential improvement, deferral reason, and reconsideration conditions. Distinguish accepted deferred targets from unverified suggestions. Avoid speculative backlogs and unsupported claims of superiority. Remove adopted, rejected, or irrelevant alternatives and update current design as needed.

## Context And Discovery

Choose tools and reading breadth for the task; document structure prescribes no reading sequence. Account for applicable shared constraints, complete affected behavior, and cross-topic dependencies. Search hits or misses alone do not establish complete context.

Use the known project or existing documentation boundary to locate the authoritative design. Do not create records for a source subdirectory merely because it is the current working directory, or scan unrelated projects and retired ledgers during ordinary work.

See [record design](references/record-design.md) for the organization rationale and migration considerations.

## Update Current Meaning

Persist user-stated or accepted durable meaning while handling the task. Patch current paragraphs instead of appending corrections below obsolete statements. Preserve sufficient semantic context and check affected statements and shared constraints for contradictions; choose the reading and editing scope appropriate to the change. Do not rewrite unrelated chapters for style.

An explicit user correction authorizes updating the baseline. When a substantive change is only the agent's proposal, resolve the uncertainty before treating it as accepted. Reconsidering an alternative does not itself authorize changing product behavior.

## Check The Artifact

The audit has two primary outcomes: establish whether user requirements are implemented, and expose agent additions and choices for unspecified details. Show how the product actually works, including fulfilled requirements, rather than only defects or an alignment declaration.

For ordinary work, check affected behavior and changed artifacts using appropriate diffs, file tools, runtime checks, or tests. Without Git, use changed files and relevant callers. Do not imply a whole-project audit.

Inspect both directions: requirements to artifact, and changed behavior back to design. Trace obligations and prohibitions through triggers, routing, modes, exceptions, fallbacks, and early exits. Main-path success does not prove universal compliance. Expand scope when shared controls affect other topics.

Report fulfillment and concrete choices by topic. Distinguish explicit requirements, agent-filled details, and additional mechanisms; reasonable gap filling is neither automatically a defect nor user-approved design.

Inspect potentially unnecessary additions such as SHA256 checks, extra state, protocols, retries, or verification layers. Internal or apparently beneficial mechanisms still need visibility. Support judgments of effects, benefit, cost, complexity, and necessity with evidence; keep unknown rationale or necessity explicit. Checksums are not inherently wrong, and syntax-only changes are not product decisions.

Surface omissions, narrowing, substitutions, conflicts, and uncertainty alongside choices. No omissions does not mean no additions. Do not promote observed choices into accepted requirements; leave unmet behavior visible as a current design gap.

State scope, limits, and evidence for substantive findings. Avoid persistent per-requirement pass entries or repeated generic counterexample paragraphs. Reuse understanding for navigation, but verify current artifacts before making current correctness claims.

A requested whole-project audit covers all current design documents and relevant artifacts, including unrequested behavior. Long audits may use temporary checkpoints by topic and artifact scope, not reusable coverage. Check scope changes when resuming and remove completed checkpoints.

See [audit presentation](references/audit-presentation.md) for concrete details and report formats. The dedicated audit webpage and its prototypes remain deferred until the user asks to pursue their design. Ordinary report diagrams are available when useful.
