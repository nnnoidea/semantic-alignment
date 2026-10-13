# Audit Presentation

Present requirement fulfillment and meaningful agent choices together by product topic, so the user can judge actual behavior at a glance.

## Requirements In The Real Product

Connect intended behavior to observed realization, including important conditions and exceptions. Make missing, narrowed, conflicting, or unverified behavior visible. Cite the relevant code, configuration, outputs, UI, runtime observations, or tests without dumping logs.

## Details Filled In And Additional Mechanisms

Expose observed choices that matter: defaults and thresholds, data destinations and storage, triggers, failure handling, retries, permissions, and resource limits. Show the actual choices, not hypothetical ways to implement them.

An extra verification layer, state store, or protocol can matter even when the successful user flow is unchanged. Explain when it activates, its consequences and complexity, and evidence for its necessity. A documented agent explanation is context, not proof of benefit or necessity.

Passing tests do not establish user consent, and code alone does not establish decision rationale. Present coherent behavior and meaningful mechanisms instead of enumerating private functions or equivalent refactors.

Use concise prose, a topic-level comparison table, or a simple diagram where it clarifies actual behavior. Connect requested behavior, realization, meaningful choices, and evidence; no mandatory row schema or separate presentation system is needed.

## Decisions Needed To Repair Findings

For each meaningful repair direction, identify any missing user information or unsettled choice that changes the target, scope, acceptance criteria, or consequences. Examples include conflicting intended behavior, an unspecified retention policy, or a keep/remove choice for an added mechanism whose effects are not covered by the accepted design. First investigate its real role and dependencies; being unrequested alone does not prove that removing it is the correct repair.

Separate a user decision from an artifact fact still requiring investigation, and from permission for a specific external action. Existing answers and authorization still apply. An explicit requirement to export all records provides a clear target for fixing silent truncation; introducing a new retention period requires a product choice. Do not turn ordinary implementation judgment or restoring settled requirements into mandatory confirmation.

Present only genuine confirmation needs alongside the finding: what is missing or disputed, why available evidence cannot settle it, the exact question, and how plausible answers change the repair. Offer a recommendation and concrete options when supported, without inventing rationale or making a speculative alternative sound accepted. Group related questions by topic; no fixed checklist or per-finding form is required. If there are no new confirmation points, say so briefly for the checked scope.

This assessment belongs in the audit result even when implementation has not been requested. Make the decision-dependent proposal concrete enough to review, and request necessary answers while continuing authorized independent work. If an action needs additional approval, first complete its authorized preparation so the user can review the actual change. Record the user's resolved durable choice in current design; until then, retain the gap or uncertainty rather than guessing it away.

## Deferred Visual Presentation

A dedicated audit webpage is an accepted improvement direction: help the user see requirement realization and agent additions or filled-in details quickly, especially where implementation spans topics. Its information organization and interaction need separate design and are not settled.

The current compromise is concise reports while the dedicated webpage remains unimplemented. Do not build that webpage or its mockups and prototypes until the user asks to pursue its design. This deferral applies to the dedicated audit interface: ordinary report diagrams may be used when useful without a separate visualization request. Preserve both audit outcomes in the interim format.
