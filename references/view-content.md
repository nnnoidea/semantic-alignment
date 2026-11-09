# Check Report Content And Sources

Organize semantic-check findings and their evidence for the result view; [template usage](template-usage.md) explains how to render that report.

## Scope

Keep the report within the check's project, single-module or multi-module scope; otherwise focus on known changed modules with enough context, asking only if the check scope remains unclear.

Scope determines what is checked; the default entry is the relevant user agreements, including unmet or unverified ones. Expand an agreement into its evidenced implementation, which may span modules. When the user requests an architecture/flow overview, it may be the entry while agreements remain the assessment basis.

Show final expectations and current-stage agreements as two parts of user meaning; use the current agreement and applicable constraints to judge this stage, while keeping explicitly deferred goals visible as later scope.

## Content

Keep these contexts reachable in parent details or the full report, including missing slots:

| Level | Required context |
| --- | --- |
| Project | Goal; scope/exclusions; shared constraints; acceptance. |
| Agreement / implementation context | Responsibility; inputs/trigger; outputs/effects; behavior/rules; boundaries/exceptions; acceptance. |
| Relationship | Counterpart; direction; meaning; source or labeled inference. |

Keep ownership/refinement distinct from execution, exchange or association; preserve relevant branches, waits, returns and failures, and identify where cross-boundary inputs and effects go.

Attach choices to their actual point of effect, retaining implementations without a matching user agreement. Give a shared mechanism one primary explanation; related agreements link to the precise step and have a return path, rather than duplicating whole chapters.

Show non-executing subjects as relationships; a list or interpretation of rules does not establish a runtime sequence.

Give every finding a short, evidence-backed headline such as “Existing files are overwritten”, rather than a topic name or generic status. Summary and node details use the same reading order: concrete finding → brief requirement/actual-behavior comparison → expandable effects and evidence. List Agent-added decisions by their specific names, with details on expansion; keep unverified items separate. Preserve full original wording, sources, relevant diagrams and tradeoffs below the brief view. A headline is the Agent's conclusion, not a new user quotation or permission to omit conditions.

## Evidence

Use the user's own wording wherever possible in titles, node and relationship labels, and requirement details; shorten overlong text only lightly, preserving their terms and meaning, with the full wording available in details or sources.

Use verified current user wording, otherwise labeled contiguous record excerpts; retain conditions, exceptions, full relevant context and precise sources without scanning private history merely to fill the view.

Distinguish user wording, record excerpts, Agent summaries/inferences and observed behavior, including on relationships; put agreement text in the requirement field and code observations in actual behavior. Preserve the date, scope and limits of reused evidence.

Mark the exact text involved in each identified mismatch or added choice, pairing corresponding requirement and implementation fragments with a local number and a concrete explanation. Green means that fragment was checked as matching, red means deviation or unimplemented behavior, orange means an Agent-added choice, and gray means implementation remains unverified; additions may have no requirement-side fragment. Preserve the prose and judge meaning from evidence, not wording differences; unmarked text is not a fulfillment verdict.

Put confirmed violations of applicable user constraints first, with a conspicuous restriction-violation label in the summary, detail and graph. Quote the specific restriction and its source, alongside the behavior that violates it; an unspecified choice or unverified behavior alone does not establish a violation.

Mark absent material **缺少**, uninvestigated specification **Agent 未核查**, unverified behavior **未核实**, and a genuine exclusion **不适用（理由）**. An explicit agreement with unverified implementation keeps its specification status; the uncertainty belongs to actual behavior. Keep agreement-review and implementation-verification labels distinct in both summary and details; preserve unresolved-decision badges on the relevant items, using “含待定方案” when only internal items are pending.

Retain the specified part of a partial requirement and name its concrete gap; broad requests, blank report inputs and Agent-chosen solutions do not establish user acceptance.
