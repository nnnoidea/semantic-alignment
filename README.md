# Semantic Alignment

[中文说明](README.zh-CN.md)

## What Problem Does It Solve?

Most projects are not completed exactly as they were first imagined.

During design, implementation, or writing, the idea changes. Sometimes that happens because a better approach is found. Other times, it happens because reality gets in the way: a tool is missing, time is limited, an asset is unavailable, permissions are not ready, or the requirement is still unclear.

The second kind of change is the dangerous one. A temporary compromise can quietly become the default route. When the original constraint is gone, the project may keep following the compromised path simply because no one remembers why the detour was taken.

AI agents add another layer of risk. They naturally fill in missing details. Some of those additions are reasonable; others may change the product meaning, interaction direction, architecture, or acceptance criteria. Without a record, it becomes hard to tell which parts came from the user, which parts were inferred by the agent, and whether the final result still fits the original goal.

`semantic-alignment` is built to address this problem.

## How Does It Solve It?

This skill asks the agent to maintain a set of semantic records for the project.

It focuses on recording:

- what the user currently wants
- which important parts of that intent have changed, and why
- which routes were accepted only because of temporary constraints
- what conditions should trigger a review of an old compromise
- what the agent added that the user did not explicitly state
- whether the final code, design, or document still matches those meanings

The main file for the user is `user-semantics.md`. It keeps the current state readable and avoids mixing in the full history. Detailed changes and audit material live in separate files.

## What Can It Remind You About?

For example:

- File export was unavailable, so the project used copy-to-clipboard; now file export is available, so the old route may be worth reopening.
- The user wanted a quiet, practical tool, but the new request is pushing the design toward a high-pressure marketing page.
- The agent added autosave, shortcuts, or navigation, even though the user did not explicitly ask for them.
- A local implementation looks reasonable, but it no longer serves the global goal.
- The actual code or design does not match what the agent believed it had implemented.

The skill does not record every chat message. It records meanings that affect the project or design direction.

## How It Works

Before a meaningful task starts, the agent reads the current semantic frame and then plans or edits from that context.

The skill separates alignment into three layers:

1. **User semantics**: what the user currently wants.
2. **Realization semantics**: what the agent intends to realize in the artifact after interpreting the user.
3. **Artifact checks**: whether the actual code, design, document, or output matches those realization semantics.

When an important semantic change happens, the agent records whether it was added, updated, or removed, and why. If the change was caused by a constraint, the record can include a trigger for checking it again later. When that condition becomes true, the agent should remind the user that an old route may be reopened.

Full audits are initiated or confirmed by the user. The agent may still proactively warn about direct contradictions or clearly stale compromises.

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
.semantic-alignment/<task-slug>/
```

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
