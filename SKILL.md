---
name: semantic-alignment
description: Perform semantic checks to help users discover where an Agent's implementation departs from their intent or fills in unspecified choices. Use for requests such as “有没有自作主张” or “是不是按我的要求做的”, including intent-comparison requests without the word “semantic”. Maintain current Markdown user meaning as the check baseline and deliver findings through editable Markdown and expandable HTML/SVG reports. Ordinary code reviews, standalone diagrams and repository walkthroughs are outside scope.
---

# Semantic Alignment

Help users see whether an Agent followed their intent and what it decided without explicit direction.

## When To Use

Activate when the user asks to compare implementation with their intent or uncover Agent-added decisions, explicitly or through context.

Maintain accepted durable meaning as the check baseline when it changes or the user requests record maintenance; recording alone does not require a full check.

Ordinary code reviews, standalone diagram requests, routine work under unchanged design and generic repository learning stay outside this scope; “check/检查” alone, existing records or coding complexity are not triggers.

A check can start from the user's request and available sources without existing records; save accepted durable meaning when needed. Changes to an existing check report belong to its delivery step.

## Semantic Check

Check each current agreement’s behavior, conditions, exceptions and shared constraints, alongside **every user-unspecified implementation choice**, including necessary, ordinary, internal, inherited and low-impact choices.

Inspect requirements → artifacts and independently artifacts → user meaning, covering actual entry points, helpers, configuration, dependencies, defaults, exceptions and shipped inactive mechanisms within scope.

Code, tests and implementation notes are not user acceptance; keep unknown provenance and unmet requirements visible.

Prioritize confirmed violations of the user's constraints so they are immediately visible among the findings.

Follow [semantic check presentation](references/audit-presentation.md) for complete disclosure, optional-mechanism analysis, source-driven verification and repair questions.

A semantic check defaults to local implementation-comparison HTML/SVG with a separate discrepancy-summary page, backed by editable semantic-check Markdown, unless another format is requested. Visualization presents check findings; it is not a separate service.

Present **user agreements → actual flows → steps and evidence**, using [report content and sources](references/view-content.md) and [report template usage](references/template-usage.md); shared implementations have one main explanation with precise links from related agreements.

Lead each finding with a short, concrete conclusion, followed by a brief requirement/behavior comparison; keep added choices concise and make their effects, full wording and evidence available on expansion.

## Maintain Current Meaning

Honor a user-designated record location; otherwise reuse the target project's canonical Markdown document, or default to `<project-root>/SEMANTICS.md` if none exists. Use the user's own wording wherever possible; shorten overlong passages only lightly, preserving their terms, conditions and meaning. Use this structure:

```markdown
# Project or topic
## Purpose
## Constraints
## User agreements
### Agreement topic
**Final expectation:**
**Current-stage agreement:**
**Stage completion criteria:**
**Related agreements:**
**Related files:**
```

Fill each part with the following meaning:

| Part | What to record |
| --- | --- |
| Purpose | Why the project/topic is needed: the user's problem and desired outcome at this scope. |
| Constraints | User-set boundaries and rules that apply across this scope, including explicit exclusions; put topic-specific constraints beside that topic. |
| User agreements | User expectations, behavior, boundaries and stage decisions, grouped into named topics; each topic uses the five fields below. |
| Final expectation | The complete target behavior the user has described, including applicable conditions and exceptions; do not expand it into an Agent-invented roadmap. |
| Current-stage agreement | What the user wants in this stage: required behavior, scope, agreed approach, and explicit postponements or compromises. This is an agreement, not progress or observed implementation. |
| Stage completion criteria | User-provided conditions for this stage to count as complete; reference the current agreement when it already states them. Record the criteria, not test results or completion status. |
| Related agreements | Names/links of other agreement topics and the relationship: depends on, supplies input/output to, shares a constraint with, or refines. Label Agent-inferred relationships as such. |
| Related files | Relevant record, source or documentation files/directories, with their connection to the topic; multiple paths are allowed. Distinguish user-required paths from Agent-maintained navigation metadata. |

Group topics by the user's concerns; a topic may cover an overall responsibility or a specific behavior. Preserve explicit module boundaries and refinement relationships, while labeling Agent-created groupings as navigation. File splits do not define implementation modules.

Record only expressed or accepted user meaning; write **未约定** for unstated items and preserve known requirements without inventing a final vision, stage boundary or additional acceptance criteria.

For example, if the user says “eventually support local and cloud copying; start with local single-file copying”, the first clause is the final expectation and the second is the current-stage agreement; neither says what has been implemented.

Use one file for records within 100 lines; beyond 100 lines, topics may be split into `semantics/` beside the main record, leaving shared meaning and an agreement index at the entry. Split files have no size limit.

Replace old statements with accepted changes and update affected references; make retained variants' conditions, agreed stage boundaries and unresolved intent explicit.

Put actual behavior found during semantic checking and its supporting evidence, such as code locations or observed results, in the check report rather than the user-meaning record.
