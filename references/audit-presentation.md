# Semantic Check Presentation

Apply the [content and source rules](view-content.md); this reference owns semantic-check coverage, findings and repair decisions.

Help the user discover what the Agent added, changed or decided without explicit direction, alongside unmet user requirements.

Code inspection establishes actual behavior against user intent; report omissions, deviations and unspecified choices, including logic defects that explain a semantic mismatch.

Judge this stage against all stated behavior, conditions, exceptions and applicable shared constraints in the current agreements; completion criteria supplement this meaning. Explicitly deferred final goals remain later scope, and an agreement is never implementation evidence.

## Inspect And Disclose

- Establish the artifact scope from real entries, callers, configuration, dependencies and supplied tools, distinguishing active behavior from shipped inactive content.
- Trace normal and exceptional paths, including inherited defaults, early exits, partial effects, cleanup and recovery; verify dependency contracts and observable state where they affect a claim.
- For each topic, connect user requirements to actual behavior and disclose every concrete choice with its values, conditions, ordering, outputs, side effects and evidence.
- Preserve omissions, narrowing, conflicts, unverified behavior and unknown authorship; an implementation description or successful test does not establish user agreement or rationale.
- Group for readability while retaining every distinct choice, including UI wording, styling, interaction and internal mechanisms; labels, counts and representative examples cannot replace full detail.

## Prioritize Optional Mechanisms

Prioritize supported candidates for whole unrequested mechanisms that can be omitted while retaining the requested capability, keeping all other choices reachable.

For each candidate, trace producers, consumers and failure paths and state the removal boundary, retained capability, lost guarantees, compatibility and resource effects; an unsettled consequence remains a tradeoff rather than a confident removal recommendation.

Distinguish removal from choosing a replacement implementation, and distinguish an exploratory probe from a deployable change; neither an unchanged normal result nor passing tests authorize deletion.

Support benefit/cost claims with evidence, label hypothetical simplified flows, and link each candidate to its complete detail and original sources.

## Checking Disclosure Completeness

Reconcile actual artifact choices with the report, including compound behavior and helper/library options, then correct omissions and overgeneralizations consistently across overview, detail and appendices.

For a completeness claim, use independent source-first review of semantic coverage when available and authorized; otherwise perform a fresh artifact-driven countercheck and disclose that limitation.

Resolve review disagreements against actual evidence, recheck repeated omission patterns and remaining findings, and leave unexamined areas explicitly outstanding.

Temporary notes are optional aids, not reusable coverage; report the checked scope and limits rather than inferring completeness from files read or bugs found.

## Decisions Needed To Repair Findings

Assess repair information after disclosure: reuse existing intent, answers, authorization and inspectable facts, then ask only about consequential unresolved targets, scope, acceptance or effects.

Each genuine question explains the uncertainty, concrete options, consequences and dependent work; restoring settled requirements and ordinary implementation choices need no new blanket approval.

Include this assessment even when only a semantic check was requested, state briefly when no new decisions are needed, and continue authorized independent work while awaiting necessary answers.

An unspecified choice is neither automatically wrong nor a deletion instruction; accepted durable decisions update the current design.

## Report Contract: Markdown And Visual HTML

Deliver the check findings as self-contained HTML with native SVG, plus standalone SVG files and editable semantic-check Markdown as its full-content source, unless the user requests another format. Visualization is the report's presentation layer, not a separate task entry point.

Organize Markdown by agreements and their actual implementation relationships, retaining all requirements, concrete choices, values/effects, sources, uncertainty and repair decisions; keep shared scope, date, baseline, conclusions and verification limits in one place.

The default reading path is **user agreements → their actual flows → concrete steps, choices and evidence**, with a brief explanation of scope and verification limits.

Also provide a separate summary page for quick reading: collect identified deviations/omissions and Agent-added choices, keep unverified items separate, and link each item to its original detail and evidence. Reuse the report's findings and scope; an empty category is not a completeness or fulfillment verdict.

Before delivery, reconcile every finding disclosed in Markdown, prose and detail diagrams with the summary; grouping may shorten presentation, but an annotated sample does not cover the rest of an item's known choices.

Keep fulfillment gaps, optional mechanisms and implementations without a specific user requirement visible at their relevant locations; complete findings, appendices, reused-evidence dates and unchecked scope remain reachable from the full-report entry.

Use [view content](view-content.md) for source distinctions and [template usage](template-usage.md) for presentation; retain legible source paths and unfiltered content for reading/printing, and do not treat presentation changes as product re-verification.
