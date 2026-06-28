# Audits

## Current Audit Summary

- Overall status: aligned.
- Open drift: GitHub publishing remains part of the original project goal but is not yet completed.
- Open contradictions: none observed.
- Reopen triggers: use generated `recheck-triggers.md` for routine trigger monitoring; if the projection becomes stale, run `scripts/sync_triggers.py`; if agents miss rules because references are not loaded, strengthen the reference-loading map; if trigger rows again contain open tasks/recommendations/actions, recheck U30; if JSONL mirrors diverge from Markdown records, recheck U35.
- Current recommendations:
  - Decide whether the GitHub repository should contain only this skill or multiple skills.
  - Initialize Git and publish the repository after choosing the GitHub layout.
  - Keep reference files unsplit unless a split creates distinct loading moments for real agent actions.

### 2026-06-29 - Scripted records and structured mirrors

- Trigger: User asked to complete the first, fourth, and fifth proposed optimizations, then clarified that reference splitting is useful only when split files are loaded separately.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `operational-workflow.md`, `semantic-record-template.md`, `sync_triggers.py`, `validate_records.py`, new `record_event.py`, new `export_structured.py`, temp script test records.
- Findings:
  - Manual Markdown table edits remain useful but are fragile for repeated appends.
  - Identical trigger rows add monitoring noise when multiple ledger entries share one observable recheck condition.
  - Non-user-facing records can gain machine-readable mirrors without replacing `user-semantics.md` as the user's Markdown review entry point.
  - Reference splitting should be justified by separate loading paths, not by file length alone.
- Decision: Add `scripts/record_event.py`, group identical trigger conditions in `sync_triggers.py`, update validation to expect grouped trigger rows, add `scripts/export_structured.py`, document structured mirrors, and record the reference-splitting criterion without splitting files now.
- Follow-up status: resolved for the three requested optimizations; open for future source-of-truth migration only if JSONL mirrors prove useful enough.

### 2026-06-29 - Whole-skill consistency review

- Trigger: User asked to reread the whole skill and check for internal inconsistency or redundancy.
- Initiated by: user.
- Inputs checked: `SKILL.md`, all reference files, `agents/openai.yaml`, record scripts, current semantic records.
- Findings:
  - `structured/` was documented too much like a standard required directory even though it is an optional generated mirror.
  - Structured mirror wording was too broad: the script exports selected records, not every non-user-facing record.
  - Recheck trigger documentation said not to hand-edit rows but did not clearly distinguish generated row identity from editable check metadata.
  - `audit-rules.md` referred to "ledger trigger state" even though trigger check status lives in `recheck-triggers.md`, not the ledger.
- Decision: Clarify optional structured mirrors, narrow structured-export wording, define editable trigger metadata fields, update generated trigger text in scripts/templates, and record K37.
- Follow-up status: resolved.

### 2026-06-29 - GitHub packaging preparation

- Trigger: User said the skill should be uploaded to GitHub, practice records should be included as examples, and README should be bilingual.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `agents/openai.yaml`, current practice records, generated structured mirrors.
- Findings:
  - The runtime skill can stay rooted at `SKILL.md` with `references/`, `scripts/`, and `agents/`.
  - GitHub documentation needs a README even though runtime skill instructions should stay lean.
  - Practice records are useful as examples but should not be referenced by `SKILL.md` as runtime material.
- Decision: Add bilingual `README.md`, add repository `.gitignore`, copy practice records to `examples/semantic-alignment-skill/`, and add an example README clarifying that examples are documentation only.
- Follow-up status: open until the GitHub remote is created and pushed.

### 2026-06-28 - Reminder behavior validation

- Trigger: User asked whether reminders for semantic conflict and mature-condition route changes are sufficient, and asked to test with sub-agents.
- Initiated by: user.
- Inputs checked: conflict test output, stale-route test output, `SKILL.md`, `operational-workflow.md`, `audit-rules.md`, generated test records.
- Findings:
  - Direct semantic conflict reminder passed: the sub-agent identified the conflict between a high-conversion decorative marketing direction and the existing quiet documentation-like baseline, refused to silently update the baseline, and recorded an open confirmation need.
  - Stale-route reminder was only partially sufficient: the sub-agent detected that Blob download availability satisfied the recheck trigger and updated records, but treated the user's same-message "keep fallback" instruction as enough to close the trigger without making the stale-route reminder visibly explicit.
- Decision: Strengthen stale-route rules so a true recheck trigger must be surfaced in the user-facing response before resolving the trigger or continuing with the old compromised route; same-message keep-route instructions count as confirmation only when explicit and still require one visible reminder.
- Follow-up status: resolved for source-rule strengthening; future fresh-agent tests should check that stale-route reminders appear in the response, not only in records.

### 2026-06-28 - Fresh-agent forward validation

- Trigger: User asked to start a sub-agent validation.
- Initiated by: user.
- Inputs checked: sub-agent output in `tmp-semantic-forward-test/`, generated note-taking app records, `validate_records.py`, `sync_triggers.py`, `lint_records.py`, current practice records.
- Findings:
  - A fresh sub-agent loaded the skill sufficiently to create a small note-taking app, create standard semantic records, distinguish user semantics from realization semantics, mark agent-added interactions as interpretations, and generate recheck triggers from ledger entries.
  - The generated records passed structural validation, trigger-sync validation, and strict semantic linting.
  - The test environment lacked `node`, so JavaScript syntax checking for the simulated app could not run.
  - The forward test exposed an unrelated practice-record defect: duplicate `A32` in `realization-semantics.md` was not caught by existing validation.
- Decision: Record K30 for forward-test pass, add duplicate-ID validation to `validate_records.py`, remove the duplicate realization row, and record K31/A33 for the validator hardening.
- Follow-up status: resolved for fresh-agent semantic-record behavior; open only for optional Node-based app syntax/runtime checks if this temporary app is kept.

### 2026-06-28 - Agent behavior hardening

- Trigger: User agreed the identified agent-behavior risks were reasonable and asked to strengthen the skill.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `operational-workflow.md`, `semantic-record-template.md`, `validate_records.py`, `user-semantics.md`, `user-semantic-ledger.md`.
- Findings:
  - A fresh agent could still skip startup reads or fail to load the needed reference.
  - Structural validation cannot catch action-like triggers or likely missing current-state projection.
- Decision: Add a startup checklist, strengthen per-action reference-loading instructions, add `scripts/lint_records.py`, document lint usage, update current semantic records, and verify current records pass lint.
- Follow-up status: resolved for source changes; open for optional fresh-agent forward-test.

### 2026-06-28 - Trigger semantics correction

- Trigger: User clarified that a recheck trigger means satisfying a condition should cause the corresponding semantic change to be rechecked.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `semantic-model.md`, `operational-workflow.md`, `audit-rules.md`, `semantic-record-template.md`, `user-semantic-ledger.md`, `recheck-triggers.md`.
- Findings:
  - Previous trigger rows mixed true conditions, open tasks, recommendations, and actions.
  - `GitHub publishing remains open` is an open drift, not a recheck trigger for a semantic change.
- Decision: Define recheck triggers as observable conditions, clean current ledger trigger text, set non-trigger open tasks to `None.`, and regenerate `recheck-triggers.md`.
- Follow-up status: resolved.

### 2026-06-28 - Reason vocabulary alignment fix

- Trigger: User said the reason enum needs to be fixed.
- Initiated by: user.
- Inputs checked: `semantic-model.md`, `semantic-record-template.md`, `validate_records.py`, `artifact-checks.md`, `audits.md`.
- Findings:
  - `implementation-discovery` and `agent-inference` were valid in the semantic model but missing from the record template and validator allowlist.
- Decision: Add both reason values to the template example and validator; record K27 as the passing artifact check that resolves K25.
- Follow-up status: resolved.

### 2026-06-28 - User-requested audit after reference split

- Trigger: User asked to audit the current project after the skill was split into on-demand references.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `semantic-model.md`, `operational-workflow.md`, `audit-rules.md`, `semantic-record-template.md`, `init_records.py`, `sync_triggers.py`, `validate_records.py`, `agents/openai.yaml`, `user-semantics.md`, `user-semantic-ledger.md`, `recheck-triggers.md`, `realization-semantics.md`, `artifact-checks.md`, `audits.md`.
- Findings:
  - Current user semantics, realization semantics, and the refactored source structure are mostly aligned.
  - Validation passes today, and `recheck-triggers.md` is in sync with the ledger.
  - `semantic-model.md` allows `implementation-discovery` and `agent-inference` reasons, but `semantic-record-template.md` and `validate_records.py` do not allow those reason values.
  - `semantic-record-template.md` is 203 lines and lacks a table of contents, which weakens the on-demand reference design.
  - GitHub publishing remains open.
- Decision: Record K25 as a material artifact mismatch and K26 as a partial usability drift. Do not change source behavior in this audit pass without user confirmation.
- Follow-up status: open.

#### Internal User Audit

- Aligned: The current goal, platform-neutral record path, concise `SKILL.md`, reference split, user-readable current baseline, generated recheck triggers, and user-owned audit policy are mutually consistent.
- Potential drift: GitHub publishing remains incomplete; long schema reference may reduce usability.
- Contradictions: None observed in current user semantics.

#### User-To-Realization Audit

- Grounded: A29 follows U29 directly; generated trigger workflow follows U28; current record separation follows U6/U7/U24.
- Added by agent: Exact reference split into semantic model, operational workflow, audit rules, and record template.
- Risky: Validator/template reason vocabulary is narrower than the semantic model, so future valid ledger entries may fail validation.
- Divergent: None observed in the realization intent itself.

#### Realization-To-Artifact Audit

- Aligned: `SKILL.md` is now concise and routes to focused references; scripts validate records and trigger sync; source skill validates successfully.
- Potential drift: `semantic-record-template.md` lacks a table of contents despite being the largest reference.
- Contradictions: Reason vocabulary mismatch between model/template/validator.

### 2026-06-28 - Split long skill body into references

- Trigger: User said the skill is obviously too long and that splitting into on-demand reads may be more suitable.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `user-semantics.md`, `recheck-triggers.md`, `index.md`, `skill-creator` guidance.
- Findings:
  - The full SKILL body duplicated detailed model, workflow, audit, trigger, and schema guidance inline.
  - This conflicts with progressive disclosure and increases default context cost.
- Decision: Reduce `SKILL.md` to core workflow, record setup, minimal rules, recording levels, and a reference-loading map. Move details to `semantic-model.md`, `operational-workflow.md`, and `audit-rules.md`; keep exact schemas in `semantic-record-template.md`.
- Follow-up status: resolved for source structure; open to forward-test whether agents load references correctly.

### 2026-06-28 - Generated recheck triggers

- Trigger: User said `recheck-triggers.md` can be generated by script and that this is more stable.
- Initiated by: user.
- Inputs checked: `user-semantics.md`, `user-semantic-ledger.md`, `recheck-triggers.md`, `realization-semantics.md`, `artifact-checks.md`, `SKILL.md`, `semantic-record-template.md`, `init_records.py`, `validate_records.py`.
- Findings:
  - Agent-maintained trigger rows can drift from the authoritative ledger.
  - The ledger currently stores trigger text but not full method/status metadata, so sync needs to preserve existing projection metadata where possible.
- Decision: Add `scripts/sync_triggers.py`, update instructions and template, make validator check projection sync, and regenerate current `recheck-triggers.md`.
- Follow-up status: resolved for current design; monitor whether trigger metadata should move into structured ledger fields later.

### 2026-06-28 - Fresh semantic frame and trigger projection

- Trigger: User clarified that `user-semantics.md` need not be reread every time if already loaded, and that recheck triggers should be extracted to avoid scanning the complete ledger.
- Initiated by: user.
- Inputs checked: `user-semantics.md`, `user-semantic-ledger.md`, `realization-semantics.md`, `artifact-checks.md`, `SKILL.md`, `semantic-record-template.md`, `init_records.py`, `validate_records.py`.
- Findings:
  - The skill previously over-required rereading and scanning, which was practical overhead.
  - Recheck triggers need a compact current projection while keeping the ledger as authoritative history.
- Decision: Add fresh-frame read rules, add `recheck-triggers.md`, generate/validate it in scripts, and update current practice records.
- Follow-up status: resolved for current design; monitor whether manual trigger projection stays synchronized.

### 2026-06-28 - Remove semantic deltas

- Trigger: User clarified that the future-action function belongs in `user-semantic-ledger.md`, and that unaccepted no-impact agent suggestions should not be recorded.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `semantic-record-template.md`, `init_records.py`, `validate_records.py`, `user-semantics.md`, `user-semantic-ledger.md`, `realization-semantics.md`, `artifact-checks.md`.
- Findings:
  - `semantic-deltas.md` duplicated the practical purpose of the user semantic ledger.
  - The useful action hook is `Recheck trigger`, which already belongs to `user-semantic-ledger.md`.
  - Persisting unaccepted, no-impact agent suggestions would create noise rather than alignment value.
- Decision: Remove `semantic-deltas.md` from standard records, templates, generator, validator, and current practice records. Keep unaccepted no-impact suggestions out of persistent records.
- Follow-up status: resolved.

#### Internal User Audit

- Aligned: The user semantic ledger now owns accepted user-baseline history, causes, and future recheck triggers.
- Potential drift: Historical audit events still mention `semantic-deltas.md`; they remain as history, not current design.
- Contradictions: None observed.

#### User-To-Realization Audit

- Grounded: A24 and A25 follow U24 and U25 directly.
- Added by agent: Keeping historical U22/U23 rows but marking them no/current superseded rather than deleting.
- Risky: If future users want a separate idea backlog, it should be explicit and not part of semantic alignment records by default.
- Divergent: None observed.

#### Realization-To-Artifact Audit

- Aligned: Source files, generator, validator, and practice directory no longer require `semantic-deltas.md`.
- Potential drift: `audits.md` retains prior event text that references the old file.
- Contradictions: None observed.

## Audit Events

### 2026-06-28 - Current skill structure review

- Trigger: User asked whether repeated audits should be updated, deleted, or recorded differently.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `semantic-record-template.md`, current practice records.
- Findings:
  - User semantics, agent/intended artifact semantics, artifact checks, semantic deltas, and audit material are separated.
  - `user-semantics.md` is readable as a current user baseline.
  - Metadata is scoped under `.semantic-alignment/`.
  - Repeated audit handling needed explicit current-summary plus event-history rules.
- Decision: Add repeated-audit rules to the skill and template; restructure this file around current summary plus audit events.
- Follow-up status: resolved.

#### Internal User Audit

- Aligned: The requested name, user semantics, agent/intended artifact semantics, change history, repeated audit model, separated records, user-readable entry point, operational triggers, and project hygiene rules all support the stated goal.
- Potential drift: GitHub publishing remains pending.
- Contradictions: None observed.

### 2026-06-28 - Ledger and delta boundary

- Trigger: User asked whether `user-semantic-ledger.md` and `semantic-deltas.md` are duplicate, how deltas arise, and whether semantic changes can originate from agent responses.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `semantic-record-template.md`, `user-semantics.md`, `user-semantic-ledger.md`, `realization-semantics.md`, `semantic-deltas.md`, `artifact-checks.md`.
- Findings:
  - The previous skill text did not make the boundary strong enough.
  - `user-semantic-ledger.md` should track user-originated current-baseline changes.
  - `semantic-deltas.md` should track material cross-layer semantic transitions, including changes caused by agent suggestions, limitations, compromises, artifact checks, implementation discovery, audits, and external constraints.
- Decision: Add a Ledger And Delta Boundary section, expand delta triggers to include agent responses, and update the delta table with `ID`, `Layer`, `Source`, and `Linked records`.
- Follow-up status: resolved.

#### Internal User Audit

- Aligned: The user wants semantic changes recorded by meaning and cause, not only by user utterance; the new boundary supports that.
- Potential drift: If deltas record every small realization detail, they may become noisy. The skill now limits deltas to material semantic transitions.
- Contradictions: None observed.

#### User-To-Realization Audit

- Grounded: The change follows the user's clarification that agent responses can drive semantic changes.
- Added by agent: Specific delta source/layer vocabulary and linked-record column.
- Risky: Structured Markdown tables may become wide; future YAML/JSON migration remains an option for non-user-facing records.
- Divergent: None observed.

#### Realization-To-Artifact Audit

- Aligned: Source skill, template, validator, and current practice delta records now express source/layer boundaries.
- Potential drift: Historical rows were normalized into the new table format, so the wording is summarized rather than byte-for-byte original.
- Contradictions: None observed.

#### User-To-Agent Audit

- Grounded: User internal audit, user-to-agent audit, agent-to-artifact check, semantic deltas, reason tracking, agent inference classification, split records by source, prose-first `user-semantics.md`, confirmation rules, metadata hygiene, and repeated audit status handling.
- Added by agent: Reason vocabulary, reference template shape, replacement of the old directory, and audit event format.
- Risky: Current session PATH is stale, so commands in this turn need full paths.
- Divergent: Earlier single-file practice record, table-first user record, standalone artifact semantics layer, `artifact evidence` wording, and action-log file were corrected.

#### Agent-To-Artifact Audit

- Aligned: Skill and practice records now include repeated audit rules; `artifact-checks.md` remains a mechanical pass/partial/fail log; `audits.md` now holds current summary and audit events.
- Potential drift: Template may still be too heavy for very small tasks; recording levels reduce that risk.
- Contradictions: None observed.

### 2026-06-28 - Audit initiation policy update

- Trigger: User clarified that full audits should be user-initiated while agent should remind at checkpoints and proactively flag direct semantic contradictions.
- Initiated by: user.
- Inputs checked: `SKILL.md`, current user semantics, semantic deltas.
- Findings:
  - Prior rules said to audit at checkpoints, which could imply agent-initiated full audits.
  - User wants full audit control but still wants proactive narrow warnings for contradictions and clearly stale constraints.
- Decision: Update skill rules so Codex recommends audits and only performs full audits when user requests or accepts; keep proactive warnings for direct contradictions, divergent agent semantics, material artifact check failures, and clearly resolved constraints.
- Follow-up status: resolved.

#### Internal User Audit

- Aligned: User-owned full audit and proactive narrow warnings can coexist.
- Potential drift: Agent may under-remind if thresholds are too vague.
- Contradictions: None observed.

#### User-To-Agent Audit

- Grounded: Audit initiation policy directly follows U22.
- Added by agent: Specific trigger list for audit recommendations.
- Risky: Detecting whether a historical route should be reopened may require judgment; rule now recommends surfacing it at constraint resolution or audit checkpoints.
- Divergent: None observed.

#### Agent-To-Artifact Audit

- Aligned: `SKILL.md` now reflects user-initiated audit behavior and proactive warning boundaries.
- Potential drift: Future use may need tighter thresholds for "many changes" or "enough iterations".
- Contradictions: None observed.

### 2026-06-28 - Required reads and observable triggers

- Trigger: User pointed out that records have no value if agents do not read them, and that reminders need concrete detection rules.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `semantic-record-template.md`, current user semantics.
- Findings:
  - Prior rules said when to record and suggest audits, but did not force reading records before decisions.
  - Constraint rechecks needed structured fields and observable methods.
  - Skill metadata could be stronger for automatic invocation on non-trivial project/design/artifact tasks.
- Decision: Add Required Reads, Trigger Heuristics, and Constraint Recheck Rules; strengthen frontmatter description.
- Follow-up status: resolved.

#### Internal User Audit

- Aligned: Required reads directly support the goal that semantic records affect agent behavior.
- Potential drift: Skill triggering still depends on installation and the host system's skill selection mechanism.
- Contradictions: None observed.

#### User-To-Agent Audit

- Grounded: Required reads, observable trigger heuristics, and constraint recheck fields follow U23.
- Added by agent: Concrete recheck method examples.
- Risky: Strong trigger wording cannot guarantee invocation if the skill is not installed or the environment does not select it.
- Divergent: None observed.

#### Agent-To-Artifact Audit

- Aligned: `SKILL.md` and template now include required read and constraint recheck mechanics.
- Potential drift: The stronger description may trigger the skill broadly; recording levels should prevent over-documenting tiny tasks.
- Contradictions: None observed.

### 2026-06-28 - Process adherence check

- Trigger: User asked whether Codex had failed to update the current project semantic files according to the skill.
- Initiated by: user.
- Inputs checked: `user-semantics.md`, `user-semantic-ledger.md`, `agent-semantics.md`, `semantic-deltas.md`, `artifact-checks.md`, `audits.md`.
- Findings:
  - Prior updates for U23 and related skill changes were present across the semantic files.
  - The user's challenge itself was not yet recorded before this check.
- Decision: Record U24, add A15, add K11, and append this audit event.
- Follow-up status: superseded by semantic capture filter update. The process check remains an audit event, but the process-only user statement was kept out of `user-semantic-ledger.md`.

#### Internal User Audit

- Aligned: The user expects the skill practice records to be updated as part of changing the skill.
- Potential drift: None after recording this check.
- Contradictions: None observed.

#### User-To-Agent Audit

- Grounded: A15 directly follows U24.
- Added by agent: Formalizing the challenge as a process-adherence check.
- Risky: None.
- Divergent: None observed.

#### Agent-To-Artifact Audit

- Aligned: Current practice records include the process-adherence check as an audit event, not user semantic history.
- Potential drift: Future changes should continue this pattern without over-recording trivial exchanges.
- Contradictions: None observed.

### 2026-06-28 - U22 classification check

- Trigger: User asked whether the history-route reminder point was recorded and whether it was recorded as a compromise.
- Initiated by: user.
- Inputs checked: `user-semantic-ledger.md`, `semantic-deltas.md`, `audits.md`, `user-semantics.md`.
- Findings:
  - The history-route reminder was recorded in the user semantic history.
  - The corresponding delta was recorded as `clarification`, not `constraint` or compromise.
  - The record did not explicitly say "not a compromise", so it could be misread later.
- Decision: Add U25 and an explicit semantic delta clarifying that U22 is not a compromise; future concrete capability limits should be recorded separately as constraints with recheck methods.
- Follow-up status: resolved. Source note was renumbered after removing process-only U24 from user history.

### 2026-06-28 - Semantic capture filter

- Trigger: User clarified that the record should capture "用户对项目设计的语义", not every user input.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `semantic-record-template.md`, `user-semantics.md`, `user-semantic-ledger.md`.
- Findings:
  - `user-history.md` could be misused as a chronological chat log.
  - A prior process-only challenge had been recorded as a user semantic source note.
- Decision: Add Semantic Capture Filter to the skill, update the template, keep process-only checks in `audits.md`, and later replace source-note history with `user-semantic-ledger.md`.
- Follow-up status: resolved.

### 2026-06-28 - User semantic ledger model

- Trigger: User clarified that semantic history must show add/update/delete operations from A to B with reasons, and that user-facing semantics should be the latest state.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `semantic-record-template.md`, `user-semantics.md`, prior user history, `semantic-deltas.md`.
- Findings:
  - Source-note history did not clearly show before/after transitions.
  - User-facing current semantics should be the latest projection from history.
  - Semantics need categories beyond high-level/detail.
- Decision: Replace `user-history.md` with `user-semantic-ledger.md`, add semantic categories, and make `user-semantics.md` the current-state projection.
- Follow-up status: resolved.

### 2026-06-28 - Record format validation

- Trigger: User asked whether semantic files are written only by agent judgment and whether scripts should fix or check their format.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `semantic-record-template.md`, current practice records.
- Findings:
  - Semantic interpretation should remain with agent/user judgment.
  - File presence, table headers, and controlled vocabulary can be deterministically checked.
- Decision: Add `scripts/init_records.py`, expand `scripts/validate_records.py`, and require initialization plus validation for standard/deep record directories.
- Follow-up status: resolved.

### 2026-06-28 - Platform-neutral record path

- Trigger: User said `.codex` should be removed because it limits use on other agent platforms.
- Initiated by: user.
- Inputs checked: `SKILL.md`, `semantic-record-template.md`, scripts, `.gitignore`, current practice records.
- Findings:
  - A Codex-specific record path creates unnecessary permission and portability risk.
  - The skill's actual semantic model is platform-neutral agent alignment, not Codex-only storage.
- Decision: Make `.semantic-alignment/<task-slug>/` the default record path, remove `.codex` from skill instructions, and move current practice records to `.semantic-alignment/`.
- Follow-up status: resolved.

### 2026-06-28 - User-requested full semantic audit

- Trigger: User asked to audit the current project.
- Initiated by: user.
- Inputs checked: `user-semantics.md`, `user-semantic-ledger.md`, `agent-semantics.md`, `semantic-deltas.md`, `artifact-checks.md`, `audits.md`, `SKILL.md`, `semantic-record-template.md`, `init_records.py`, `validate_records.py`.
- Findings:
  - The skill source now uses platform-neutral `.semantic-alignment/` and no longer documents `.codex` as a record path.
  - The scripts support deterministic record initialization and validation.
  - `user-semantics.md` was not actually user-readable before this audit because it contained mojibake and duplicate old sections.
  - GitHub publishing remains open.
- Decision: Rewrite `user-semantics.md` as a clean current baseline, record K16/K17 artifact checks, keep GitHub publishing as the main open drift.
- Follow-up status: resolved for readability drift; open for GitHub publishing.

#### Internal User Audit

- Aligned: The current user goal, platform-neutral record path, user-owned audits, semantic ledger model, script-backed format, and three-layer audit model are mutually consistent.
- Potential drift: The project is still packaged as a Codex-compatible skill, while the broader intent is platform-neutral agent use. This is acceptable if treated as the first package format rather than the whole concept.
- Contradictions: None observed.

#### User-To-Agent Audit

- Grounded: `.semantic-alignment/` as default path, script-backed record skeleton/validation, current-state `user-semantics.md`, semantic ledger history, agent semantics as intended artifact semantics, artifact checks as mechanical checks, and user-initiated audits.
- Added by agent: Exact file layout, reason vocabularies, validation script implementation, initialization script implementation, and audit event structure.
- Risky: Markdown tables remain fragile for long-term structured history; YAML/JSON source with generated Markdown may be better if records grow.
- Divergent: The previous unreadable `user-semantics.md` diverged from the user's readability requirement; it has been corrected.

#### Agent-To-Artifact Audit

- Aligned: `SKILL.md`, `semantic-record-template.md`, `init_records.py`, and `validate_records.py` match the current agent semantics.
- Potential drift: `agents/openai.yaml` remains Codex/OpenAI-specific metadata by nature of the current package format; the core record model is platform-neutral.
- Contradictions: None observed after rewriting `user-semantics.md`.

### 2026-06-28 - Realization semantics rename

- Trigger: User accepted renaming "agent semantics" to "realization semantics" and clarified that only user-readable files need to be Markdown.
- Initiated by: user.
- Inputs checked: `user-semantics.md`, `user-semantic-ledger.md`, `realization-semantics.md`, `semantic-deltas.md`, `artifact-checks.md`, `SKILL.md`, `semantic-record-template.md`, `init_records.py`, `validate_records.py`.
- Findings:
  - "Agent semantics" named the acting subject rather than the artifact-realization layer.
  - `realization-semantics.md` better describes intended artifact semantics after interpretation and gap filling.
  - User-facing current semantics should remain Markdown; other records can later move to stronger structured formats.
- Decision: Rename `agent-semantics.md` to `realization-semantics.md`, update source skill/template/scripts, and keep Markdown as the current implementation while allowing structured non-user-facing records later.
- Follow-up status: resolved for naming; open for future structured-record migration if needed.

#### Internal User Audit

- Aligned: The rename supports the user's distinction between user semantics, intended artifact realization, and real artifacts.
- Potential drift: Existing historical IDs still use `A` prefixes. This is acceptable as historical continuity, but future examples use `R`.
- Contradictions: None observed.

#### User-To-Realization Audit

- Grounded: The rename directly follows the user's accepted preference.
- Added by agent: Keeping existing IDs instead of renumbering them to avoid noisy history churn.
- Risky: If future records mix `A` and `R` prefixes without explanation, users may find references confusing.
- Divergent: None observed.

#### Realization-To-Artifact Audit

- Aligned: Source files and scripts now use `realization-semantics.md`; current practice record was moved to the new filename.
- Potential drift: Non-user-facing records are still Markdown tables today; structured data remains a future improvement.
- Contradictions: None observed.
