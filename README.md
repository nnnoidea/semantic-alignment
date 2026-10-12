# Semantic Alignment

[中文说明](README.zh-CN.md)

Maintain readable current product and system design in Markdown. Check whether the user's requirements are implemented, and expose the concrete details the agent filled in or added.

## When It Applies

Use the skill when establishing, changing, or correcting lasting product behavior, system contracts, architecture constraints, operating rules, or acceptance criteria. Explicit requests for semantic recording or auditing also apply.

Routine implementation under an unchanged design, fixes restoring agreed behavior, internal refactors, tests, debugging, Git operations, installation, temporary analysis, research, and ordinary writing do not automatically activate it. Neither an existing semantic file nor an unspecified implementation detail is sufficient. Existing design still governs the work; consulting it does not require starting an audit.

## Current Design Records

Small projects can use one SEMANTICS.md. Larger projects can keep shared meaning and topic links there, with cohesive documents in semantics/. Group by product responsibility and complete behavioral chains, with descriptive filenames, headings, and nearby conditions and exceptions.

Edit the Markdown directly. There are no semantic IDs, JSON ledgers, generated views, relation registries, custom readers, or standing audit caches. Keep unmet requirements visible in their owning topic. Still-relevant alternatives can explain the current choice, potential improvement, deferral reason, and reconsideration conditions; they do not authorize implementation.

## What An Audit Shows

Report both requirement fulfillment and meaningful implementation choices by topic, using current artifact evidence. Show actual defaults, persistence, data flow, triggers, failure handling, and limits. Distinguish explicit requirements, agent-filled details, and additional mechanisms, including internal or apparently beneficial ones. Keep unknown rationale or necessity explicit.

Inspect applicable exceptions and bypass paths; main-path success does not prove universal compliance. State the checked scope rather than claiming whole-project alignment from a local check. Ordinary reports may use concise prose, tables, or useful diagrams. A dedicated audit webpage remains a deferred direction requiring separate design.

## Installation And Migration

Install this repository as a Codex-compatible skill named semantic-alignment. [SKILL.md](SKILL.md) is the entry point; the two linked references provide organization and report guidance as needed.

This version replaces the previous JSON workflow. Consolidate the latest accepted meaning, current gaps, and active alternatives into current Markdown, checking that conditions, prohibitions, exceptions, and acceptance boundaries survive. Stop old generators from overwriting the new records. Historical versions remain available in Git; ordinary work does not require loading them.
