# Audit Presentation

Present requirement fulfillment and meaningful agent choices together by product topic, so the user can judge actual behavior at a glance.

## Requirements In The Real Product

Connect intended behavior to observed realization, including important conditions and exceptions. Make missing, narrowed, conflicting, or unverified behavior visible. Cite the relevant code, configuration, outputs, UI, runtime observations, or tests without dumping logs.

## Details Filled In And Additional Mechanisms

Expose observed choices that matter: defaults and thresholds, data destinations and storage, triggers, failure handling, retries, permissions, and resource limits. Show the actual choices, not hypothetical ways to implement them.

An extra verification layer, state store, or protocol can matter even when the successful user flow is unchanged. Explain when it activates, its consequences and complexity, and evidence for its necessity. A documented agent explanation is context, not proof of benefit or necessity.

Passing tests do not establish user consent, and code alone does not establish decision rationale. Present coherent behavior and meaningful mechanisms instead of enumerating private functions or equivalent refactors.

Use concise prose, a topic-level comparison table, or a simple diagram where it clarifies actual behavior. Connect requested behavior, realization, meaningful choices, and evidence; no mandatory row schema or separate presentation system is needed.

## Deferred Visual Presentation

A dedicated audit webpage is an accepted improvement direction: help the user see requirement realization and agent additions or filled-in details quickly, especially where implementation spans topics. Its information organization and interaction need separate design and are not settled.

The current compromise is concise reports while the dedicated webpage remains unimplemented. Do not build that webpage or its mockups and prototypes until the user asks to pursue its design. This deferral applies to the dedicated audit interface: ordinary report diagrams may be used when useful without a separate visualization request. Preserve both audit outcomes in the interim format.
