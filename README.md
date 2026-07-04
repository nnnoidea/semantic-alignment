# Semantic Alignment

[中文说明](README.zh-CN.md)

AI agents usually do not fail by refusing to work. They fail by quietly turning the work into something else.

Users describe goals. Agents fill gaps, work around constraints, add details, and choose routes. At first, each choice may look reasonable. Over time, the project can drift: no one remembers what the user actually asked for, which parts were agent assumptions, and which decisions were only temporary compromises.

`semantic-alignment` keeps that drift visible.

It asks the agent to remember what the user really wants, record what it adds or changes during implementation, and audit the result item by item. Users should also initiate audits at key checkpoints to keep the project meaning from quietly drifting.

In short: this skill helps agents keep proving that the thing they built is still the thing the user wanted.

## How Does It Solve It?

The skill separates project meaning into a few durable records:

- `user-semantics.md`: what the user currently wants
- `user-semantic-ledger.md`: what changed, from what to what, and why
- `recheck-triggers.md`: observable conditions that mean an old decision may need review
- `realization-semantics.md`: what the agent intends to realize after interpreting the user
- `artifact-checks.md`: whether the real code, design, or document matches that intent
- `audits.md`: the alignment judgment across those layers

The important split is this: user meaning, agent-added realization meaning, and the real artifact are not treated as the same thing.

## What Does It Audit?

At review time, the skill pushes the agent to answer concrete questions instead of writing a vague summary:

- Which user semantics are satisfied, partial, unmet, unknown, or in conflict?
- Which implementation details were directly requested by the user?
- Which details were added by the agent but still serve the user's semantics?
- Which added details are risky or conflict with the user's semantics?
- Does the real artifact match what the agent believed it implemented?
- Did an old constraint disappear, making a previous compromise worth reopening?

For example, if export was unavailable and the project used copy-to-clipboard, a trigger can remind the agent to revisit that route once export becomes available. If an agent adds autosave, shortcuts, navigation, or public copy that the user never requested, the audit should classify whether those additions are aligned details or semantic drift.

## How Triggers Work

A recheck trigger is not a task and not a recommendation. It is an observable condition that means: "read the linked ledger entry again and decide whether this old semantic decision still holds."

The agent reads the compact trigger projection when it loads the semantic frame, before meaningful planning or delivery, when the user mentions a changed constraint, when the artifact exposes new evidence, and during audits. If a trigger appears true, the agent must read the linked ledger entry, state the old route and the now-true condition, and make the reminder visible before continuing or changing the baseline.

## How It Works

Before a meaningful task starts, the agent reads the current semantic frame and then plans or edits from that context.

The skill separates alignment into three layers:

1. **User semantics**: what the user currently wants.
2. **Realization semantics**: what the agent intends to realize in the artifact after interpreting the user.
3. **Artifact checks**: whether the actual code, design, document, or output matches those realization semantics.

When an important semantic change happens, the agent records whether it was added, updated, or removed, and why. If the change was caused by a constraint, the record can include a trigger for checking it again later.

Full audits are initiated or confirmed by the user. Before auditing, the agent should inspect the real project, refresh or confirm realization semantics, and refresh or confirm artifact checks. Full audit output should cover every current user semantic and every active realization semantic.

## Installation

Install this repository as a skill named `semantic-alignment` in Codex or another compatible agent environment.

The skill root is this directory:

```text
semantic-alignment/
  SKILL.md
  references/
  scripts/
  agents/
```

After installation, ask the agent to use `semantic-alignment` for a project, design, implementation, or writing task where intent may evolve over time.

## Where Records Live

By default, records are stored under:

```text
.semantic-alignment/<project-slug>/
```

The directory may live under a project root or a workspace root. In a workspace with multiple projects, each project should use a distinct slug. A project slug is a stable lowercase kebab-case identifier, usually derived from the repository root, package/project name, or project directory.

The main files are:

- `user-semantics.md`: the current semantic baseline for the user
- `user-semantic-ledger.md`: accepted semantic changes and reasons
- `recheck-triggers.md`: conditions for revisiting prior decisions
- `realization-semantics.md`: what the agent intends to realize in the artifact
- `artifact-checks.md`: checks between the real artifact and realization semantics
- `audits.md`: alignment, drift, contradictions, and recommendations

These records are project-process metadata, not the product itself.

## Example

`examples/semantic-alignment-skill/` contains the semantic records created while developing this skill.

They are included only as an example of how records can evolve in a real project. Installing or running the skill does not depend on them.

## Status

This skill is currently packaged as a Codex-style skill, while the record model is intended to remain platform-neutral.
