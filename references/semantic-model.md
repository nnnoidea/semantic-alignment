# Semantic Model

Load this reference when interpreting whether a user message changes project meaning, classifying agent additions, or writing `user-semantic-ledger.md` / `realization-semantics.md`.

## Layers

Track two semantic layers plus artifact checks:

- **User semantics**: goals, non-negotiables, preferences, global direction, local requirements, constraints, review criteria, and later corrections stated or accepted by the user.
- **Realization semantics**: current intended artifact semantics after the agent interprets user semantics, fills gaps, and chooses implementation/design details.
- **Artifact checks**: concrete pass/partial/fail notes from inspecting the actual code, design, document, UI, or skill against realization semantics.

The artifact itself is the product. Do not create a separate artifact-semantics layer.

## Capture Filter

Record user semantics, not every user utterance.

Capture a user statement only when it changes or clarifies project/design/artifact meaning:

- goal, audience, direction, quality bar, non-negotiable, constraint, or review criterion
- global semantics, local semantics, expected behavior, UX meaning, architecture meaning, or public artifact meaning
- how semantic records should work for this project or skill
- correction that changes what should be built, preserved, checked, or revisited

Do not record ordinary status checks, approval/permission chatter, command details, or logistics unless they change project meaning. If a process message exposes a workflow defect, record it in `audits.md`; add it to the ledger only if it changes the skill/project semantics.

## User Semantic Categories

Use the narrowest category that fits:

- `goal`: intended outcome and success definition
- `principle`: non-negotiables, quality bars, values, constraints on acceptable solutions
- `context`: audience, environment, domain, workflow situation
- `global-design`: overall product/design/project meaning
- `local-design`: component, screen, section, behavior, interaction, or detailed design meaning
- `system`: architecture, data model, API, integration, performance, security, or operational meaning
- `content`: public copy, naming, documentation tone, narrative, or message
- `process`: semantic-alignment workflow rules for this project/skill
- `constraint`: user-recognized constraint or assumption that shapes meaning or route
- `review`: user-facing review criteria, audit expectations, acceptance checks

## Ledger Semantics

`user-semantic-ledger.md` is the single action-bearing history for user semantics.

- Use `add` when a new user semantic appears.
- Use `update` when an existing semantic changes from A to B.
- Use `delete` when a prior semantic is removed, rejected, or no longer applies.

Each entry needs semantic ID, operation, category, before, after, reason, source, current flag, and recheck trigger if conditions may change. `user-semantics.md` is the latest current projection, not the history.

A recheck trigger is an observable condition whose truth means "revisit this ledger entry and decide whether the semantic change still holds." It is not an open task, recommendation, or action. Put actions in `Recheck method`, `audits.md`, or conversation.

Triggers are meant to be evaluated against new evidence: user statements, implementation discoveries, artifact checks, dependency/tool availability, permissions, assets, audit findings, and final-delivery checks. If the condition appears true, the agent must read the linked ledger row before deciding whether to keep, reopen, or change the prior semantic decision.

Ledger entries may come from direct user clarification, user acceptance of an agent proposal, user acceptance of a limitation/compromise, implementation discovery, external constraints, or audit findings. Do not persist unaccepted agent suggestions that have no actual effect.

## Change Reasons

Use the closest reason:

- `clarification`: user clarified intent
- `correction`: prior semantics were wrong
- `optimization`: new semantics better serve the goal
- `constraint`: tools, permissions, dependencies, APIs, assets, data, time, or environment blocked a route
- `implementation-discovery`: code/system reality was different than expected
- `agent-inference`: agent filled a missing detail
- `scope-control`: change keeps the task bounded
- `preference-change`: user changed preference
- `deletion`: semantic was removed
- `unknown`: reason is not established

Audit the reason: optimization must still serve the goal; constraint needs a recheck trigger; implementation discovery needs artifact verification; agent inference must be classified.

## Realization Classification

Before and during implementation of non-obvious agent choices, classify and record them:

- `grounded`: directly follows from user semantics or local conventions
- `added`: user did not say it, but it is a reasonable detail
- `risky`: may change meaning, priority, UX, architecture, scope, or delivery criteria
- `divergent`: conflicts with current user semantics

Proceed with grounded choices. Record added choices. Surface or ask before risky choices. Stop, correct, or explicitly confirm divergent choices.

`realization-semantics.md` should stay current. It is not the realization history ledger. Keep active rows as the main working set. Use `revised` or `rejected` for recent non-current rows only when they clarify the current route; archive older non-current realization material instead of letting routine reads accumulate stale history.
